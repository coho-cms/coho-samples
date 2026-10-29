# 2. Get the data

This page takes a slice of OpenAlex and turns it into documents Coho can load. Nothing is
sent to Coho yet.

OpenAlex has more than 300 million works. The [snapshot](https://help.openalex.org/tutorials/download-the-snapshot/)
is several hundred gigabytes, so this sample reads the API instead and asks it for a random
sample of each kind of work in each field of research.

## 1. Get an OpenAlex API key

The API's data is free; using it is metered. Every account gets $1 of usage a day free,
and a list of 100 works costs a hundredth of a cent, so a day's free usage reads up to a
million works. Without a key, everyone on your network shares a tenth of that.

Get a free key at [openalex.org/settings/api](https://openalex.org/settings/api), and put it
where `catalog.py` looks for it:

```bash
export OPENALEX_API_KEY=<your key>
```

## 2. Plan the slice

```bash
uv run catalog.py plan --works 10000
```

`plan` asks OpenAlex how many works of each kind there are in each of its 26 fields of
research, such as Medicine, Computer Science, and Arts and Humanities. That is about 570
pairs of kind and field. It then shares the 10,000 works out between them, evenly: a pair
with fewer works than its share, such as software papers in nursing, takes all it has and
gives the rest back to the others. So the slice is as wide as it can be, and only as deep
as the number you ask for.

```
572 cells, 10,000 works:
  article                       468
  review                        468
  …
  supplementary-materials       442
  software-paper                376

Fetching it is 572 list calls, about $0.06. Planning cost $0.0022.
```

Each pair needs at least one request, however few works it takes, so a small slice costs
more a work than a large one: 100,000 works is about 1,100 requests, around $0.11.

Start with 10,000 works. They become about 35,000 entries, because each work brings its
authors, institutions, source, and topic with it. Once you have seen them load, plan again
with `--works 100000` for a project of a few hundred thousand.

## 3. Fetch it

```bash
uv run catalog.py fetch
```

`fetch` samples each pair's share, 100 works a request, into `data/works`. A sample is
seeded, so planning and fetching again gets the same works. It can be stopped and run
again: each pair it finishes is marked done and skipped next time.

## 4. Convert it

```bash
uv run catalog.py convert
```

`convert` reads every fetched work and writes Coho backup documents, 1,000 entries each,
into `data/backup`, then counts what it wrote by content type. Expect about three and a
half entries for every work: authors are the most numerous, then the works, then their
institutions, sources, and topics.

A few things it does on the way, all in `model.py`:

- **Kinds.** OpenAlex's type picks the content type: an `article` is a Research article,
  an `erratum` an Erratum, and so on. `other`, `paratext` and `libguides` are left out.
- **Links.** A work's authors, institutions, source, and topic become entries of their own
  the first time any work mentions them, and every later work links to the same entry.
- **Authors.** By default only the first and last author of each work are kept, since a
  whole author list makes authors outnumber works several times over.
  `--authors-per-work 0` keeps every author.
- **Names.** An entry's name is unique among the entries of its base type, and OpenAlex
  repeats titles ("Erratum") and authors' names freely. Every entry with a repeated name
  gets its OpenAlex id in brackets, such as `Erratum (W4236116516)`, the first one too, so
  a later, larger load never hands one entry's name to another.
- **Ids.** Each entry's id is made from its OpenAlex id, so loading the same batch twice
  changes nothing.
- **Abstracts.** OpenAlex keeps an abstract as a list of words and their positions, and
  the converter puts the words back in order.

Next: [Load it](03_LOAD.md).
