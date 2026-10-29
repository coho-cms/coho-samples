"""
How an OpenAlex record becomes a Coho entry. The content types themselves are the JSON
files in `types/`, which you put with the CLI on page 1; this reads them too, so a field
you add or remove there changes what the converter writes.
"""

from __future__ import annotations

import html
import json
import re
import uuid
from functools import cache
from pathlib import Path
from typing import Any

TYPES = Path(__file__).resolve().parent / "types"

# Every entry's id is derived from its OpenAlex id in this namespace, so the same record
# is the same entry on every run, and loading a batch twice writes nothing the second time.
NAMESPACE = uuid.UUID("3c9e2a71-0a1e-4d00-8000-0000000a1e00")

# OpenAlex's work type, and the content type it loads as. `other`, `paratext` and
# `libguides` are left out: covers, tables of contents and library guides.
WORK_TYPES: dict[str, str] = {
    "article": "researchArticle",
    "review": "review",
    "letter": "letter",
    "editorial": "editorial",
    "book-review": "bookReview",
    "peer-review": "peerReview",
    "erratum": "erratum",
    "retraction": "retraction",
    "data-paper": "dataPaper",
    "software-paper": "softwarePaper",
    "book": "book",
    "book-chapter": "bookChapter",
    "reference-entry": "referenceEntry",
    "conference-paper": "conferencePaper",
    "conference-abstract": "conferenceAbstract",
    "preprint": "preprint",
    "dissertation": "dissertation",
    "report": "report",
    "standard": "standard",
    "dataset": "dataset",
    "software": "software",
    "supplementary-materials": "supplementaryMaterial",
}


def node_id(kind: str, openalex_id: str) -> str:
    return str(uuid.uuid5(NAMESPACE, f"{kind}:{openalex_id}"))


def short(openalex_url: str | None) -> str | None:
    """`https://openalex.org/W4417445208` is `W4417445208`."""
    return openalex_url.rsplit("/", 1)[-1] if openalex_url else None


# THE TYPES
# THE TYPES
# THE TYPES

def slug_of(name: str) -> str:
    """As the CLI makes a type's slug from its `_name`: `Research topic` is `researchTopic`."""
    words = re.split(r"[^A-Za-z0-9]+", name)
    words = [w for w in words if w]
    return words[0].lower() + "".join(w[0].upper() + w[1:].lower() for w in words[1:])


@cache
def definitions() -> dict[str, dict[str, Any]]:
    """Every type in `types/`, by slug."""
    return {slug_of(d["_name"]): d for d in (json.loads(p.read_text()) for p in sorted(TYPES.glob("*.json")))}


@cache
def fields_of(slug: str) -> frozenset[str]:
    """Every field a type has, its ancestors' included: all an entry of it may carry."""
    ids: set[str] = set()
    current: str | None = slug
    while current:
        definition = definitions()[current]
        ids |= {f["id"] for f in definition.get("fields", [])}
        current = definition.get("extends")
    return frozenset(ids)


@cache
def values_of(slug: str, field: str) -> frozenset[str]:
    """A choice field's values, as its type file lists them."""
    for f in definitions()[slug].get("fields", []):
        if f["id"] == field:
            return frozenset(f.get("values", []))
    return frozenset()


# THE RECORDS
# THE RECORDS
# THE RECORDS

TAG = re.compile(r"<[^>]+>")
SPACE = re.compile(r"\s+")


def clean(value: str | None, limit: int = 0) -> str | None:
    """Markup out, entities decoded, whitespace folded; cut at [limit] when one is given."""
    if not value:
        return None
    out = SPACE.sub(" ", html.unescape(TAG.sub("", value))).strip()
    if limit and len(out) > limit:
        out = out[: limit - 1].rstrip() + "…"
    return out or None


def abstract_of(inverted: dict[str, list[int]] | None) -> str | None:
    """OpenAlex keeps an abstract as word → positions. Put the words back in order."""
    if not inverted:
        return None
    positions = [(p, word) for word, ps in inverted.items() for p in ps]
    return clean(" ".join(word for _, word in sorted(positions)))


def drop_empty(body: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in body.items() if v not in (None, "", [])}


def one_of(value: str | None, slug: str, field: str, otherwise: str | None = "other") -> str | None:
    """[value] if the type's choice offers it, else [otherwise]; nothing for nothing."""
    if not value:
        return None
    return value if value in values_of(slug, field) else otherwise


def topic_body(topic: dict[str, Any]) -> dict[str, Any]:
    return drop_empty({
        "_name": clean(topic.get("display_name"), 200),
        "domain": one_of((topic.get("domain") or {}).get("display_name"), "researchTopic", "domain", None),
        "field": (topic.get("field") or {}).get("display_name"),
        "subfield": (topic.get("subfield") or {}).get("display_name"),
        "openAlexId": short(topic.get("id")),
    })


def institution_body(inst: dict[str, Any]) -> dict[str, Any]:
    return drop_empty({
        "_name": clean(inst.get("display_name"), 200),
        "kind": one_of(inst.get("type"), "institution", "kind"),
        "country": inst.get("country_code"),
        "ror": short(inst.get("ror")),
        "openAlexId": short(inst.get("id")),
    })


def source_body(src: dict[str, Any]) -> dict[str, Any]:
    return drop_empty({
        "_name": clean(src.get("display_name"), 200),
        "kind": one_of(src.get("type"), "source", "kind"),
        "issn": src.get("issn_l"),
        "publisher": clean(src.get("host_organization_name"), 200),
        "openAccess": src.get("is_oa"),
        "inDoaj": src.get("is_in_doaj"),
        "openAlexId": short(src.get("id")),
    })


def author_body(author: dict[str, Any], institution: str | None) -> dict[str, Any]:
    return drop_empty({
        "_name": clean(author.get("display_name"), 200),
        "orcid": short(author.get("orcid")),
        "institution": institution,
        "openAlexId": short(author.get("id")),
    })


def pages(biblio: dict[str, Any]) -> str | None:
    first, last = biblio.get("first_page"), biblio.get("last_page")
    if first and last and first != last:
        return f"{first}–{last}"
    return first or last
