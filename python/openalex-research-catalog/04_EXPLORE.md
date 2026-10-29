# 4. Explore it

The project now holds tens of thousands of entries. This page is a tour of what that looks
like, in the portal and from the CLI.

## In the portal

Open the project and choose **All entries**.

- **The newest first.** All entries lists what changed last at the top, 25 to a page, with
  when each was last updated. Everything was loaded at once, so the works, loaded last,
  come first.
- **Search.** Type in the box above the list. Every word you type must appear in an
  entry's name or its slug, in any case: `crispr` finds every title and name with CRISPR
  in it, `climate model` the ones with both words, and `w4402` works by the start of their
  OpenAlex id, which is their slug.

Then look at **Entries by type** in the sidebar.

- **Work** is abstract and has no entries of its own; its count is every work. The chevron
  beside it opens its kinds, on a tinted panel.
- **Journal content** opens a second panel, a shade darker, and **Notice** inside it a
  third, holding **Erratum** and **Retraction**: the four levels a type tree may have.
- **Only its own** appears in the panel of a type that has entries of its own as well as
  subtypes. Here every type with subtypes is abstract, so you won't see it; the blog
  samples' Blog post, which Photo gallery extends, shows it.
- Open **Journal content** itself. Its list holds every research article, review, letter,
  erratum, and the rest, each saying which kind it is in its Type column.

Open a work. Its authors, source, and topic are links, and each opens that entry's own page,
with the path you took kept in the breadcrumbs. Open an author or a source and look at
**Referenced by**: every work that links to it.

Under **Model**, **Content types** lists all 33 types, with a search and every column
sorting. With this many works, the **Entries** column says which kinds OpenAlex has most of.

## From the CLI

A base type's list includes its descendants' entries:

```bash
coho entry list -t notice --limit 5
```

lists errata and retractions together. `-t erratum` lists the errata alone.

Read one entry whole:

```bash
coho -o json entry get <entry-id>
```

## What next

- **Go bigger.** Plan again with `--works 100000`, then fetch, convert, and load into the
  same project. The larger sample is fetched alongside the first, and convert reads both,
  so the first load's entries are reported as unchanged and everything else is new.
- **Change the model on a branch.** Add a field to `types/05-work.json`, put it on a branch,
  and merge it back: every one of the 28 kinds below Work has it at once.
- **Read it from code.** The [FastAPI sample](../cli-fastapi-blog/README.md) generates a
  library of Pydantic models from a project's types. Pointed at this project, it generates
  them for these.
