# A research catalog from OpenAlex

The blog samples load a handful of entries by hand. This one loads tens of thousands, so you
can see how Coho behaves with a project the size a real one reaches: a type tree that goes
four levels deep, lists you page through, search, and entries that link to each other in
every direction.

The content is real. [OpenAlex](https://openalex.org) is an open catalog of the world's
research: papers, books, datasets, theses, software, and the authors, institutions, and
journals behind them. Its data is [CC0](https://creativecommons.org/publicdomain/zero/1.0/),
free to use for anything. You take a slice of it, as wide as it can be: every kind of work
OpenAlex knows, in every field of research, and only as deep as the number of works you
ask for.

1. [Set up the content model](01_CONTENT_MODEL.md)
2. [Get the data](02_GET_THE_DATA.md)
3. [Load it](03_LOAD.md)
4. [Explore it](04_EXPLORE.md)

The model is mostly inheritance. A work is abstract, and OpenAlex's own type for each work
decides which kind it loads as. Two families go the full three levels below their root that
Coho allows:

```
Work
├── Journal content          volume, issue, pages
│   ├── Research article
│   ├── Review
│   ├── Letter
│   ├── Editorial
│   ├── Book review
│   ├── Peer review
│   ├── Notice
│   │   ├── Erratum
│   │   └── Retraction
│   └── Descriptor
│       ├── Data paper
│       └── Software paper
├── Book content             publisher
│   ├── Book
│   ├── Book chapter
│   └── Reference entry
├── Conference content
│   ├── Conference paper
│   └── Conference abstract
├── Preprint
├── Dissertation             granted by an institution
├── Report
├── Standard
└── Research output
    ├── Dataset
    ├── Software
    └── Supplementary material
```

Every work links to its authors, the source it was published in, the institutions behind
it, and its research topic, which are entries of their own:

```
openalex-research-catalog/
├── types/        the 33 content types, as JSON, numbered so a parent comes before its children
├── model.py      how an OpenAlex record becomes an entry
├── catalog.py    plan, fetch, convert, and load
└── data/         what catalog.py fetches and writes; not committed
```

## Before you start

You need:

- the `coho` CLI and a Coho account. [Installing the `coho` CLI](../../INSTALLING.md) sets it
  up, once for every sample. Every command in this sample uses the default profile, so none
  of them needs a `-p` flag.
- [uv](https://docs.astral.sh/uv/), which installs Python for you if you have none. Check
  with `uv --version`. `catalog.py` needs Python 3.11 or later. It uses the standard
  library, and for the load the Coho SDK, which `uv run` installs for it.
- a free OpenAlex API key, which page 2 shows how to get. Without one, the API allows a
  tenth of a day's usage, shared with everyone on your network.

Every command in this sample runs from inside this folder. Start by moving into it:

```bash
git clone https://github.com/coho-cms/coho-samples.git
cd coho-samples/python/openalex-research-catalog
```

Sign in to the default profile. This opens a browser:

```bash
coho login
```

If `coho login` reports that there is no profile yet, run the `coho configure` command in
[Installing the `coho` CLI](../../INSTALLING.md#2-point-it-at-coho), then `coho login` again.

Check who you are:

```bash
coho whoami
```

This lists the accounts you belong to. If you belong to more than one, add
`--account <name-or-id>` to the commands that follow, or set `COHO_ACCOUNT`.

Next: [Set up the content model](01_CONTENT_MODEL.md).
