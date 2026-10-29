# 1. Set up the content model

This page creates a project and puts the 33 content types in `types/` into it. Nothing is
loaded yet: page 2 gets the data and page 3 loads it.

Sign in first, as described under [Before you start](README.md#before-you-start), and work
from inside this folder:

```bash
cd coho-samples/python/openalex-research-catalog
```

## 1. Create a project

Project names must be unique within the account. If `research-catalog` is taken, pick
another name and use it in the rest of this guide.

```bash
coho project create research-catalog
```

This creates the project with a trunk ref named `v0.0.x`, and makes it the current
project. `catalog.py` loads into whatever `coho status` says is current, so check it:

```bash
coho status
```

## 2. Look at a type before you put it

Open `types/05-work.json`. It is the root of every work, and it is abstract: no entry is
ever just a Work, only one of the kinds that extend it. Its fields are the ones every work
shares, such as the abstract, when it was published, its citations, and its links:

```json
{
  "_name": "Work",
  "abstract": true,
  "fields": [
    { "id": "abstract", "type": "longText", "name": "Abstract" },
    { "id": "published", "type": "datetime", "name": "Published" },
    …
    { "id": "source", "type": "reference", "name": "Published in", "of": ["source"] },
    { "id": "authors", "type": "reference", "name": "Authors", "of": ["author"], "many": true },
    …
  ]
}
```

Now open `types/14-erratum.json`, the deepest of them:

```json
{
  "_name": "Erratum",
  "extends": "notice",
  "fields": []
}
```

An Erratum adds no fields of its own. It has every field of Notice, Journal content, and
Work, and it exists so a list of errata is one click away and so a filter can tell an
erratum from a research article. Notice is abstract too: an erratum and a retraction are
both notices, and nothing is only a notice.

## 3. Put the types

A type that extends another needs its parent to be there first. The files are numbered in
that order, so putting them in the order your shell lists them is enough:

```bash
for f in types/*.json; do coho type put --file "$f"; done
```

The slug comes from each file's `_name`: `Research topic` becomes `researchTopic`, and
`Supplementary material` becomes `supplementaryMaterial`.

Check that all 33 are there:

```bash
coho type list
```

## 4. See the tree

Open the project in the portal and choose **Content types** under **Model**. The types are
nested under the ones they extend, with Work and its 28 descendants as one tree, and the
four types every work links to (Author, Institution, Research topic, and Source) beside it.

There are no entries yet. Page 2 gets some.

Next: [Get the data](02_GET_THE_DATA.md).
