# 5. Reference repeaters and inline repeaters

Page 3 built two repeaters, the post's tags and its related posts. Each is a stream
over a list of **references**: every tag is an entry of its own, which many
posts link to. This page builds the other kind, an **inline repeater**, whose items live
inside the post itself. Each post gets a list of citations, as at the end of a paper: two each, in a
basic ASCE style.

You need the service from [Images and downloads](04_IMAGES_AND_ASSETS.md). The CLI steps run
from inside this folder, `cli-spring-blog`, as on page 1.
If you have already worked through another sample's page 5 in the same project, the
citations are there: skip to step 5.

## 1. Two kinds of list

|  | Tags: a reference repeater | Citations: an inline repeater |
|---|---|---|
| Each item is | an entry, with its own slug | an object stored in the post |
| Its type is | a content type, `tag` | a component type, `citation` |
| Shared | by every post that links it: rename a tag once, and every post shows the new name | by nothing: each post has its own citations |
| Listed and read on its own | yes: `coho entry list`, `coho.tag().list()` | no: only as part of its post |
| Read with the post | only to the `depth` you ask for, and a link to a deleted tag is a stub | always, whole, because it is part of the post |
| In the service's code | `Linked.resolved(post.getTags())`, mapped | `post.getCitations()`, mapped |

Use a reference when the thing has a life of its own: an author, a tag, a related post.
Use an inline repeater when it only makes sense inside one entry: the sections of a
page, the rows of a table, the citations at the end of a post.

## 2. Define the citation

The items of an inline repeater have a type, as entries do. It is a **component type**:
defined like a content type, but its documents are never entries.
[`types/citation.json`](types/citation.json) is a very basic ASCE citation:

```json
{
  "_name": "Citation",
  "kind": "component",
  "fields": [
    { "id": "authors", "name": "Authors",              "type": "text",    "required": true, "max": 300 },
    { "id": "year",    "name": "Year",                 "type": "integer", "required": true, "min": 1800, "max": 2100 },
    { "id": "title",   "name": "Title",                "type": "text",    "required": true, "max": 300 },
    { "id": "source",  "name": "Journal or publisher", "type": "text",    "max": 300 },
    { "id": "url",     "name": "DOI or URL",           "type": "text",    "max": 500 }
  ]
}
```

`"kind": "component"` is the one difference from the types on page 1. Put it:

```bash
coho type put --file types/citation.json
```

List the types. The `KIND` column says which is which:

```bash
coho type list
```

A type's kind is fixed when it is created. A component type has no entries: `coho entry
create -t citation` is refused, because a citation only exists inside a post.

## 3. Add the citations field

[`types/blogPost-with-citations.json`](types/blogPost-with-citations.json) is the type
from page 4, with one field added at the end:

```json
{ "id": "citations", "name": "Citations", "type": "repeater", "of": ["citation"], "max": 20 }
```

A `repeater` holds a list of items, and `of` says which component types an item may be.
Here it is only `citation`, and at most twenty of them.

As on page 4, read the type for its ETag:

```bash
coho type get blogPost
```

Then put the new definition with that ETag:

```bash
coho type put --file types/blogPost-with-citations.json --if-match '<etag>'
```

## 4. Add two citations to each post

Each post's citations are in a file under [`entries/citations`](entries/citations).
The roundabout post's cite the first and second editions of the US roundabout guide:

```json
[
  {
    "authors": "Robinson, B. W., et al.",
    "year": 2000,
    "title": "Roundabouts: An informational guide",
    "source": "FHWA-RD-00-067. Federal Highway Administration",
    "url": "https://www.fhwa.dot.gov/publications/research/safety/00067/"
  },
  {
    "authors": "Rodegerdts, L., et al.",
    "year": 2010,
    "title": "Roundabouts: An informational guide, 2nd ed.",
    "source": "NCHRP Report 672. Transportation Research Board",
    "url": "https://doi.org/10.17226/22914"
  }
]
```

Set each post's `citations` to its file. `--set` takes a JSON value, and `$(cat …)` puts
the file's contents in the command:

```bash
coho entry put @roundabout-second-opinion --set "citations=$(cat entries/citations/roundabout-second-opinion.json)"
```

```bash
coho entry put @elm-street-drainage --set "citations=$(cat entries/citations/elm-street-drainage.json)"
```

The Elm Street post cites the federal culvert design manual and ASCE's guideline for
investigating existing utilities, the standard behind "walk the line with a camera".

Read a post back:

```bash
coho -o json entry get @roundabout-second-opinion
```

Each citation now has two keys you did not write. `_id` is the item's identity, which
stays the same when you edit the item or move it in the list. `_type` says which
component it is: `citation`, filled in because the field holds no other.

```json
"citations": [
  { "_id": "01a1…", "_type": "citation", "authors": "Robinson, B. W., et al.", "year": 2000, … },
  { "_id": "01a1…", "_type": "citation", "authors": "Rodegerdts, L., et al.", "year": 2010, … }
]
```

Coho checks each item against `citation` when the post is saved. A citation with
`"year": "2000"`, a string, is refused with `VALIDATION_FAILED` at
`/citations/0/year`: the field, the item's place in the list, and the item's field.

## 5. Regenerate the library

In `blog-content`, pull and generate, as on page 4:

```bash
cd ~/workarea/blog-content
```

```bash
./gradlew cohoPull cohoGenerate
```

There is a new class, `Citation.java`, for the component, deriving from `ItemBase`, which
gives it `getId()` and `getType()`:

```java
/** Citation. A repeater item, stored in the entry that holds it. */
public final class Citation extends ItemBase
{
    …
    /** Authors */
    public String getAuthors()

    /** Year */
    public long getYear()
    …
}
```

And `BlogPost` holds a list of them:

```java
/** Citations */
public List<Citation> getCitations()
```

Compare it with `getTags()`, a list of links, each of which may be a stub:

```java
public List<Linked<Tag>> getTags()
```

## 6. Bring the new library into the service

There is nothing to install. The service builds the library from its folder (page 3, step 2),
so the next time it starts it has the library's new code, `Citation` included.

## 7. Write one citation

Create `src/main/java/com/example/blog/api/Citations.java`. It writes a citation as authors,
year, title, source and link, each ending with a full stop, and gives its parts as well, for a
front end that lays them out itself:

```java
package com.example.blog.api;

import com.yourorg.blogcontent.coho.Citation;
import java.util.ArrayList;
import java.util.List;
import org.jspecify.annotations.Nullable;

/** One citation, in a simplified ASCE author-date style: Authors. Year. Title. Source. URL. */
public final class Citations
{
    private Citations()
    {
    }

    /**
     * A citation: written out as a reference list shows it, and in its parts.
     *
     * @param text Authors. Year. Title. Source. URL.
     */
    public record CitationOut(String text, String authors, long year, String title, @Nullable String source, @Nullable String url)
    {
    }

    public static CitationOut cite(Citation citation)
    {
        List<String> parts = new ArrayList<>(List.of(sentence(citation.getAuthors()), citation.getYear() + ".", sentence(citation.getTitle())));
        if (citation.getSource() != null)
        {
            parts.add(sentence(citation.getSource()));
        }
        if (citation.getUrl() != null)
        {
            parts.add(citation.getUrl());
        }
        return new CitationOut(
            String.join(" ", parts),
            citation.getAuthors(),
            citation.getYear(),
            citation.getTitle(),
            citation.getSource(),
            citation.getUrl());
    }

    /** Ends a part of the citation with a full stop, unless it already has one, as "et al." does. */
    private static String sentence(String text)
    {
        return text.endsWith(".") ? text : text + ".";
    }
}
```

ASCE's full style has more rules than this, such as quoting an article's title and
italicising its journal instead. For reports and guides like these, it reads correctly. A
front end that wants the title in italics has the parts to do it.

## 8. Add the inline repeater to the post

In `api/Api.java`, import the record, after the `ImageOut` import:

```java
import com.example.blog.api.Citations.CitationOut;
```

and add the citations to `PostOut`, last, after `downloads`:

```java
        List<DownloadOut> downloads,
        List<CitationOut> citations)
```

In `PostsController.java`, import `Citations`, after the `Assets` import:

```java
import com.example.blog.api.Citations;
```

and give the post its citations in the `post` route, last, after the downloads:

```java
            post.getDownloads().stream().map(file -> Assets.download(file)).toList(),
            post.getCitations().stream().map(citation -> Citations.cite(citation)).toList());
```

Put the repeater beside the tags repeater from page 3:

```java
            Linked.resolved(post.getTags()).stream().map(tag -> tag.getName()).toList(),
```

Both are a stream over a list on the post. Three things differ:

- **No `Linked.resolved`.** A tag is another entry, which may be deleted or beyond the depth
  the route asked for. A citation is part of the post, so it is always there.
- **No depth.** `ReadOptions.depth(1)` is what brings the tags. The citations would come at
  depth 0 too.
- **`getId()` means something else.** A tag's id is the tag entry's, the same on every post
  that links it. A citation's id is the item's, unique to this post.

## 9. Check the result

Restart the service, and ask for the roundabout post:

```bash
curl -s http://localhost:8080/posts/roundabout-second-opinion
```

Near its end there is a list of `citations`. The roundabout post's first reads:

> Robinson, B. W., et al. 2000. Roundabouts: An informational guide. FHWA-RD-00-067.
> Federal Highway Administration. https://www.fhwa.dot.gov/publications/research/safety/00067/

Now edit a tag, and then a citation, and watch what changes. From `cli-spring-blog`:

```bash
coho entry put @traffic --set 'name=Traffic engineering'
```

The roundabout post has the new tag name, and so would every post tagged `traffic`: they
link to that one entry, and no post changed. Set it back with `--set name=Traffic`.

```bash
coho entry put @elm-street-drainage --set "citations=$(cat entries/citations/roundabout-second-opinion.json)"
```

Only the Elm Street post changes. It now cites the roundabout guides, and the roundabout
post's citations are untouched: they were copied, not linked. Put the post's own
citations back with the command from step 4.

## How items behave on branches

An item's `_id` is what a merge matches on. On two branches, one author edits the first
citation and another adds a third: the merge takes both, because they touch different
items. Two edits to the same field of the same item are a conflict, as for any field.

`--set` replaces the whole list, and items sent without an `_id` are given new ones. To
edit one citation and keep its identity, read the post with `coho -o json entry get`,
change the item, and send the list back with its `_id`s.

## If something goes wrong

- **`type put` for `blogPost` fails with `SCHEMA_INVALID`, saying `citation` is a content
  type:** `citation` was put without `"kind": "component"`. A type's kind cannot change, so
  delete it with `coho type delete citation`, then put it again from the file.
- **`entry put` fails with `VALIDATION_FAILED` at `/citations/0/_type`, saying `citation`
  is not a component type on this ref:** step 2 is not done on the ref you are writing to.
  `coho type list` shows what is there.
- **`VALIDATION_FAILED` at a field of an item, such as `/citations/1/year`:** that
  citation does not match the component, for example a year written as a string, or a
  missing title.
- **`VALIDATION_FAILED` at `/citations`, saying a string was found:** the value was not
  JSON, so it arrived as text. The commands need a shell that expands `$(cat …)`, such as
  bash or zsh, and the double quotes around the whole `--set` value.
- **`cannot find symbol: class Citation`, or `method getCitations()`:** the library was
  generated before step 3, or from another ref. Run step 5 again.
- **`getCitations()` is a `List<RepeaterItem>`, not of `Citation`:** `cohoGenerate`
  generated before `citation` was on the ref, so the types were pulled before step 2. Run
  step 5 again.
- **A citation is missing, and the service's log says the post has an item of a type the
  code has no type for:** the field holds a component added after the library was
  generated. The library leaves out items it has no type for, rather than pass them off as
  citations. Regenerate the library.
- **`coho type delete citation` fails with `TYPE_IN_USE`:** `blogPost.citations` still
  holds it. Remove the field first, or pass `--confirm-destructive`, after which every
  post with citations is refused on its next save until they are removed.

Next: [Traits and inheritance](06_TRAITS_AND_INHERITANCE.md).
