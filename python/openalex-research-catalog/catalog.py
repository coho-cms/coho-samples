#!/usr/bin/env python3
"""
A wide slice of OpenAlex, loaded into a Coho project. Four steps, each one resumable,
each writing under `data/`:

    plan     counts every work type in every research field, and shares the target
             out so the slice is as wide as it can be before it is deep
    fetch    samples each share from the OpenAlex API, 100 works a call, into data/works
    convert  turns those works into Coho backup documents in data/backup, a batch each
    load     posts each batch to the current project's ref, remembering which landed

The standard library only. The pages beside this file walk through each step.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterator

import model

API = "https://api.openalex.org"
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

# What a work is read with: everything the model maps, and nothing it does not.
SELECT = ",".join([
    "id", "title", "type", "publication_date", "publication_year", "language", "doi",
    "cited_by_count", "open_access", "primary_location", "authorships", "primary_topic",
    "biblio", "keywords", "abstract_inverted_index",
])

# A sample is at most 10,000 works (page × per_page), so no share is larger.
MAX_SHARE = 10_000
PER_PAGE = 100


# THE API
# THE API
# THE API

class OpenAlex:
    """The API, with the key if there is one, a retry for a busy server, and a running cost."""

    def __init__(self, key: str | None, mailto: str | None):
        self.key = key
        self.mailto = mailto
        self.spent = 0.0

    def get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        query = dict(params)
        if self.key:
            query["api_key"] = self.key
        if self.mailto:
            query["mailto"] = self.mailto
        url = f"{API}{path}?{urllib.parse.urlencode(query)}"
        for attempt in range(6):
            try:
                with urllib.request.urlopen(url, timeout=60) as response:
                    body = json.load(response)
                self.spent += float(body.get("meta", {}).get("cost_usd") or 0)
                return body
            except urllib.error.HTTPError as e:
                detail = e.read().decode(errors="replace")[:500]
                # A refusal for the day's budget is final; waiting will not help until tomorrow.
                if e.code in (402, 403) or "budget" in detail.lower():
                    sys.exit(f"OpenAlex refused the request ({e.code}): {detail}\nSpent so far this run: ${self.spent:.4f}")
                if e.code not in (429, 500, 502, 503, 504) or attempt == 5:
                    sys.exit(f"OpenAlex said {e.code} for {path}: {detail}")
            except urllib.error.URLError as e:
                if attempt == 5:
                    sys.exit(f"OpenAlex could not be reached: {e.reason}")
            time.sleep(2 ** attempt)
        raise AssertionError("unreachable")


# PLAN
# PLAN
# PLAN

def plan(args: argparse.Namespace, api: OpenAlex) -> None:
    """Count each (type, field) cell and share the target out by water-filling."""
    cells: dict[str, int] = {}
    for openalex_type in model.WORK_TYPES:
        body = api.get("/works", {"filter": f"type:{openalex_type}", "group_by": "primary_topic.field.id"})
        for group in body.get("group_by", []):
            field = model.short(group["key"])
            if field and field != "unknown":
                cells[f"{openalex_type}|{field}|{group['key_display_name']}"] = int(group["count"])
        print(f"  {openalex_type:<24} {sum(g['count'] for g in body.get('group_by', [])):>12,}")

    shares = water_fill(cells, args.works)
    DATA.mkdir(exist_ok=True)
    (DATA / "plan.json").write_text(json.dumps({"seed": args.seed, "works": args.works, "shares": shares}, indent=1))
    by_type: dict[str, int] = {}
    for cell, n in shares.items():
        by_type[cell.split("|")[0]] = by_type.get(cell.split("|")[0], 0) + n
    print(f"\n{len(shares)} cells, {sum(shares.values()):,} works:")
    for t, n in sorted(by_type.items(), key=lambda kv: -kv[1]):
        print(f"  {t:<24} {n:>8,}")
    calls = sum(math.ceil(n / PER_PAGE) for n in shares.values())
    print(f"\nFetching it is {calls:,} list calls, about ${calls * 0.0001:.2f}. Planning cost ${api.spent:.4f}.")


def water_fill(available: dict[str, int], target: int) -> dict[str, int]:
    """
    Every cell an equal share, a cell with fewer works than that giving the rest back to the
    others, until the target is spent or every cell is exhausted: as wide as the data
    allows, then as deep as the target needs.
    """
    room = {cell: min(n, MAX_SHARE) for cell, n in available.items() if n > 0}
    shares = {cell: 0 for cell in room}
    left = target
    while left > 0:
        open_cells = [c for c in room if shares[c] < room[c]]
        if not open_cells:
            break
        each = max(1, left // len(open_cells))
        for cell in open_cells:
            give = min(each, room[cell] - shares[cell], left)
            shares[cell] += give
            left -= give
            if left == 0:
                break
    return {cell: n for cell, n in shares.items() if n > 0}


# FETCH
# FETCH
# FETCH

def fetch(args: argparse.Namespace, api: OpenAlex) -> None:
    """Sample each cell's share, a cell to a file, skipping cells already complete."""
    planned = json.loads((DATA / "plan.json").read_text())
    cache = DATA / "works"
    cache.mkdir(parents=True, exist_ok=True)
    todo = [(cell, n) for cell, n in planned["shares"].items() if not (cache / f"{slug_of(cell, n)}.done").exists()]
    print(f"{len(planned['shares']) - len(todo)} cells already fetched, {len(todo)} to go.")
    if args.cells:
        # A trial: the first cell of each type in turn, so even a few cells span the model.
        by_type: dict[str, list[tuple[str, int]]] = {}
        for cell, n in todo:
            by_type.setdefault(cell.split("|")[0], []).append((cell, n))
        spread = [cells[i] for i in range(max(map(len, by_type.values()), default=0)) for cells in by_type.values() if i < len(cells)]
        todo = spread[: args.cells]
    for i, (cell, n) in enumerate(todo, 1):
        openalex_type, field, _ = cell.split("|", 2)
        out = cache / f"{slug_of(cell, n)}.jsonl.gz"
        got = 0
        with gzip.open(out, "wt") as f:
            for page in range(1, math.ceil(n / PER_PAGE) + 1):
                body = api.get("/works", {
                    "filter": f"type:{openalex_type},primary_topic.field.id:{field}",
                    "sample": n,
                    "seed": planned["seed"],
                    "per_page": PER_PAGE,
                    "page": page,
                    "select": SELECT,
                })
                for work in body.get("results", []):
                    f.write(json.dumps(work) + "\n")
                    got += 1
                if len(body.get("results", [])) < PER_PAGE:
                    break
        (cache / f"{slug_of(cell, n)}.done").write_text(str(got))
        print(f"  [{i}/{len(todo)}] {cell.split('|')[0]} in {cell.split('|')[2]}: {got:,} (${api.spent:.4f} so far)")
        if args.budget and api.spent >= args.budget:
            print(f"Stopped at the ${args.budget} budget; run fetch again to carry on.")
            return
    print(f"Done. This run cost ${api.spent:.4f}.")


def slug_of(cell: str, share: int) -> str:
    """A cell's file name, with its share: a later, larger plan fetches the cell again, and convert reads both."""
    openalex_type, field, _ = cell.split("|", 2)
    return f"{openalex_type}--{field}--{share}"


def cached_works() -> Iterator[dict[str, Any]]:
    seen: set[str] = set()
    for path in sorted((DATA / "works").glob("*.jsonl.gz")):
        with gzip.open(path, "rt") as f:
            for line in f:
                work = json.loads(line)
                if work["id"] not in seen:
                    seen.add(work["id"])
                    yield work


# CONVERT
# CONVERT
# CONVERT

def disambiguate(entries: dict[str, dict[str, Any]], bases: dict[str, str]) -> None:
    """
    Internal names are unique within a base type (V9), case and all, and OpenAlex repeats
    titles ("Erratum") and authors' names freely. Every holder of a repeated name takes its
    OpenAlex id, the first included, so which one keeps the plain name never depends on
    the order works were read in. Each load reads everything fetched so far, so a name only
    gains holders: a later, larger load renames an entry, and never gives its old name to
    another.
    """
    holders: dict[tuple[str, str], int] = {}
    for nid, e in entries.items():
        key = (bases[nid], e["body"]["_name"])
        holders[key] = holders.get(key, 0) + 1
    for nid, e in entries.items():
        if holders[(bases[nid], e["body"]["_name"])] > 1:
            e["body"]["_name"] = f"{e['body']['_name'][:180]} ({e['slug'].upper()})"


def convert(args: argparse.Namespace) -> None:
    out = DATA / "backup"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.json"):
        old.unlink()
    loaded = DATA / "loaded.txt"
    if loaded.exists():
        loaded.unlink()

    entries: dict[str, dict[str, Any]] = {}
    bases: dict[str, str] = {}
    counts: dict[str, int] = {}

    def entry(kind: str, type_slug: str, openalex_id: str, body: dict[str, Any], base: str | None = None) -> str | None:
        """Add an entry once, by its OpenAlex id; the first sighting is the one kept."""
        nid = model.node_id(kind, openalex_id)
        if nid in entries:
            return nid
        if not body.get("_name"):
            return None
        bases[nid] = base or type_slug
        allowed = model.fields_of(type_slug) | {"_name"}
        entries[nid] = {"id": nid, "kind": "entry", "type": type_slug, "slug": openalex_id.lower(), "body": {k: v for k, v in body.items() if k in allowed}}
        counts[type_slug] = counts.get(type_slug, 0) + 1
        return nid

    skipped = 0
    for work in cached_works():
        type_slug = model.WORK_TYPES.get(work.get("type") or "")
        title = model.clean(work.get("title"), 300)
        if not type_slug or not title:
            skipped += 1
            continue

        location = work.get("primary_location") or {}
        source = location.get("source")
        source_id = entry("source", "source", model.short(source["id"]), model.source_body(source)) if source and source.get("id") else None

        topic = work.get("primary_topic")
        topic_id = entry("topic", "researchTopic", model.short(topic["id"]), model.topic_body(topic)) if topic and topic.get("id") else None

        authors: list[str] = []
        institutions: list[str] = []
        authorships = work.get("authorships") or []
        kept = trimmed(authorships, args.authors_per_work)
        for authorship in authorships:
            for inst in authorship.get("institutions") or []:
                if inst.get("id") and len(institutions) < 10:
                    iid = entry("institution", "institution", model.short(inst["id"]), model.institution_body(inst))
                    if iid and iid not in institutions:
                        institutions.append(iid)
        for authorship in kept:
            author = authorship.get("author") or {}
            if not author.get("id"):
                continue
            first_inst = next((i for i in authorship.get("institutions") or [] if i.get("id")), None)
            inst_id = model.node_id("institution", model.short(first_inst["id"])) if first_inst and model.node_id("institution", model.short(first_inst["id"])) in entries else None
            aid = entry("author", "author", model.short(author["id"]), model.author_body(author, inst_id))
            if aid and aid not in authors:
                authors.append(aid)

        oa = (work.get("open_access") or {}).get("oa_status")
        biblio = work.get("biblio") or {}
        published = work.get("publication_date")
        body = model.drop_empty({
            "_name": title,
            "abstract": model.abstract_of(work.get("abstract_inverted_index")),
            "published": f"{published}T00:00:00Z" if published else None,
            "year": work.get("publication_year"),
            "doi": work.get("doi", "").replace("https://doi.org/", "") if work.get("doi") else None,
            "language": work.get("language"),
            "citations": work.get("cited_by_count"),
            "openAccess": model.one_of(oa, "work", "openAccess", None),
            "license": location.get("license"),
            "source": source_id,
            "authors": authors,
            "institutions": institutions,
            "topic": topic_id,
            "keywords": ", ".join(k["display_name"] for k in (work.get("keywords") or [])[:8]) or None,
            "openAlexId": model.short(work["id"]),
            "volume": biblio.get("volume"),
            "issue": biblio.get("issue"),
            "pages": model.pages(biblio),
            "publisher": (source or {}).get("host_organization_name"),
            "grantedBy": institutions[0] if type_slug == "dissertation" and institutions else None,
        })
        entry("work", type_slug, model.short(work["id"]), body, base="work")

    disambiguate(entries, bases)

    # Referenced entries first, so a batch's links land on entries already written: topics,
    # institutions, sources, authors, then works.
    order = {"researchTopic": 0, "institution": 1, "source": 2, "author": 3}
    ordered = sorted(entries.values(), key=lambda e: order.get(e["type"], 4))
    for i in range(0, len(ordered), args.batch):
        batch = ordered[i : i + args.batch]
        (out / f"{i // args.batch + 1:04d}.json").write_text(json.dumps({"format": "coho-backup", "version": 1, "nodes": batch}))

    print(f"{len(ordered):,} entries in {math.ceil(len(ordered) / args.batch)} batches of up to {args.batch:,}; {skipped:,} works skipped (no title, or a type left out).")
    for t, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {t:<24} {n:>8,}")


def trimmed(authorships: list[dict[str, Any]], keep: int) -> list[dict[str, Any]]:
    """
    The first [keep] - 1 authors and the last, or every one with [keep] 0. A whole author
    list makes authors outnumber works several times over; first and last are the two a
    reader of a paper looks for.
    """
    if keep == 0 or len(authorships) <= keep:
        return authorships
    return authorships[: keep - 1] + authorships[-1:]


# LOAD
# LOAD
# LOAD

def load(args: argparse.Namespace) -> None:
    token = os.environ.get("COHO_TOKEN")
    if not token:
        sys.exit("Set COHO_TOKEN to a project token with the author role first: see 03_LOAD.md.")
    place = current_place()
    ref = args.ref or place["ref"]
    path = f"/api/v1/accounts/{place['account']}/projects/{place['project']}/refs/{urllib.parse.quote(ref, safe='')}/backup"
    done_file = DATA / "loaded.txt"
    done = set(done_file.read_text().split()) if done_file.exists() else set()
    batches = sorted((DATA / "backup").glob("*.json"))
    if not batches:
        sys.exit("Nothing to load: run convert first.")
    print(f"Loading into {place['projectName'] or place['project']} on {ref}: {len(done)} of {len(batches)} batches already in.")
    started = time.time()
    for batch in batches:
        if batch.name in done:
            continue
        request = urllib.request.Request(
            place["url"].rstrip("/") + path,
            data=batch.read_bytes(),
            method="POST",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        t0 = time.time()
        try:
            with urllib.request.urlopen(request, timeout=900) as response:
                result = json.load(response)
        except urllib.error.HTTPError as e:
            if e.code == 504:
                sys.exit(
                    f"{batch.name} took longer than Coho waits for one request. It may still land: run load again, "
                    "and whatever it wrote comes back as unchanged. If this keeps happening, convert again with a "
                    "smaller --batch."
                )
            sys.exit(f"{batch.name} was refused ({e.code}): {e.read().decode(errors='replace')[:2000]}")
        with done_file.open("a") as f:
            f.write(batch.name + "\n")
        print(f"  {batch.name}: {result.get('created', 0):,} created, {result.get('updated', 0):,} updated, {result.get('unchanged', 0):,} unchanged in {time.time() - t0:.1f}s")
    print(f"Done in {time.time() - started:.0f}s.")


def current_place() -> dict[str, Any]:
    """The CLI's current URL, account, project and ref: what `coho status` shows."""
    env = {k: v for k, v in os.environ.items() if k != "COHO_TOKEN"}
    try:
        out = subprocess.run(["coho", "-o", "json", "status"], capture_output=True, text=True, check=True, env=env).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        sys.exit(f"Could not read `coho status` ({e}). Is the CLI installed, and are you signed in?")
    place = json.loads(out)
    for key in ("url", "account", "project", "ref"):
        if not place.get(key):
            sys.exit(f"`coho status` has no {key}. Run `coho project use research-catalog` first: see 01_CONTENT_MODEL.md.")
    return place


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--key", default=os.environ.get("OPENALEX_API_KEY"), help="OpenAlex API key (or OPENALEX_API_KEY). Without one the day's budget is $0.10, shared by your IP.")
    parser.add_argument("--mailto", default=os.environ.get("OPENALEX_MAILTO"))
    steps = parser.add_subparsers(dest="step", required=True)

    p = steps.add_parser("plan", help="count the cells and share the target out")
    p.add_argument("--works", type=int, default=10_000)
    p.add_argument("--seed", type=int, default=42)

    p = steps.add_parser("fetch", help="sample each cell into data/works")
    p.add_argument("--budget", type=float, default=0, help="stop once this run has spent this many dollars")
    p.add_argument("--cells", type=int, default=0, help="fetch only this many cells, spread across the types: a trial")

    p = steps.add_parser("convert", help="write backup documents into data/backup")
    p.add_argument("--batch", type=int, default=1000, help="entries per backup document, each one transaction")
    p.add_argument("--authors-per-work", type=int, default=2, help="the first n-1 and the last; 0 for every author")

    p = steps.add_parser("load", help="post each backup document to the current project's ref")
    p.add_argument("--ref", help="a branch other than the current ref")

    args = parser.parse_args()
    api = OpenAlex(args.key, args.mailto)
    {"plan": lambda: plan(args, api), "fetch": lambda: fetch(args, api), "convert": lambda: convert(args), "load": lambda: load(args)}[args.step]()


if __name__ == "__main__":
    main()
