# 6. Traits and inheritance

Over the last five pages you built a content model and a site that reads it. Page 1 set up
the content types and entries: posts, authors and tags, with localized text, markdown and
references between them. Page 2 generated a typed client library from those types, and
page 3 used it to build a Razor Pages blog. Page 4 added images and downloads as assets, and
page 5 showed two kinds of list: links to other entries, and citations stored inside each
post.

So far every content type stands on its own: each declares every field it has. That is
fine for a handful of types, but a real model grows, relationships between types emerge, 
and types begin to share some of the same fields. 
Coho has two ways to share them, and this page introduces both:

- **Traits.** A trait is a named group of fields that any type can take, such as the
  title and description a page shows search engines. It says what a type **has**.
- **Inheritance.** A type can extend another, and have every field the other has, plus
  its own. It says what a type **is**: a kind of the type it extends, listed with it and
  linkable wherever it is.

You will use one of each. First, the post's search-engine fields move into a trait called
`seo`, which gains an SEO title along the way. Then a photo gallery becomes a new kind of
post: it has everything a post has, a list of photos besides, and it is listed among the
posts. The page ends by setting the two side by side, and when to reach for which.

You need the blog from [Reference repeaters and inline repeaters](05_REFERENCE_AND_INLINE_REPEATERS.md).
Traits and subtypes need `coho` 2026.1.0a20 or later (check with `coho --version`),
`CohoCms.Codegen` and `CohoCms.Delivery` 0.1.0-alpha.3 or later, and a Coho server that
has them. The CLI steps run from inside this folder, `cli-razor-blog`, as on page 1. If you
have already worked through the Node.js sample's page 6 in the same project, the trait and
the gallery are there: skip to step 7.

## 1. Make the SEO trait

A trait is a named group of fields. [`types/seo.json`](types/seo.json) has two, a title
and a description for search engines and link previews:

```json
{
  "_name": "SEO",
  "fields": [
    { "id": "seoTitle",        "name": "SEO title",           "type": "text",      "localized": true, "max": 60 },
    { "id": "seoDescription",  "name": "SEO description",     "type": "text",      "localized": true, "max": 160 }
  ]
}
```

`seoDescription` is the post's field from page 1, word for word: the same id, the same
kind, localized, and at most 160 characters. `seoTitle` is new. A trait has fields and
nothing else: no parent, and no traits of its own. Put it:

```bash
coho trait put --file types/seo.json
```

```bash
coho trait list
```

The `TAKEN BY` column is empty: no type takes it yet.

## 2. Move the post's SEO description into the trait

[`types/blogPost-with-seo.json`](types/blogPost-with-seo.json) is the type from page 5 with
two changes. It takes the trait, by naming it:

```json
"traits": ["seo"],
```

and its own `seoDescription` field is gone, because the trait gives it now. A field comes
from one place only, so a type that took `seo` and still declared `seoDescription` would be
refused with `FIELD_CONFLICT`.

Read the type for its ETag:

```bash
coho type get blogPost
```

Then put the new definition with that ETag:

```bash
coho type put --file types/blogPost-with-seo.json --if-match '<etag>'
```

There is no `--confirm-destructive`, and none is asked for. Read a post:

```bash
coho -o json entry get @roundabout-second-opinion
```

Its `seoDescription` is still there, as it was:

```json
"seoDescription": {
  "en-US": "Why roundabouts need a second check at peak flow, and why walking the junction still matters."
}
```

### Why nothing was lost

An entry stores each value under its field's id. It does not record which type, or which
trait, declared the field. So the posts did not change at all: the field they have a value
for moved from the post's own list to the trait's, under the same id.

Coho checks a change to a type by comparing every field the type has before and after:
its own, those it inherits, and those it takes from traits. Before, the post had
`seoDescription`, localized text of at most 160 characters. After, it still has exactly
that, now from `seo`. Nothing is removed, retyped or made required, so nothing needs
confirming. The post also has a new field, `seoTitle`, which is optional, so every post is
still valid.

`coho type get blogPost` now says `traits: seo`, and its fields table no longer lists
`seoDescription`: the table shows the fields the type declares itself, and that one is the
trait's.

### Refactoring into traits later is fine

You do not have to plan traits up front. Model the field where you first need it, and
move it into a trait when a second type needs it too, as this page just did. The move
keeps every value, as long as the trait's field matches the type's in these three ways:

- **The same id.** The id is what the values are stored under. A trait field called
  `metaDescription` is a different field, and the posts' `seoDescription` values would
  stay behind with nothing to read them. To rename a field, add the new one and copy the
  values across. Then mark the old one `"omitted": true`, which hides it and keeps its
  values, and remove it in a later change.
- **The same kind.** Text stays text.
- **Localization and `required` no looser or stricter than before.** If the trait's
  field is not localized, every post would lose all but one locale; if it is required,
  every post without a value would stop being valid. Coho refuses either with
  `DESTRUCTIVE_SCHEMA_CHANGE`, listing each change and how many entries it reaches, unless
  you confirm it. A different `max` is not destructive: a value that no longer fits is
  refused when that entry is next saved.

The same holds the other way: a field can move from a trait back into a type, or from one
trait into another. On a branch, the move shows in the diff as a change to the type and a
new trait, and merges like any other change to the model.

## 3. Give each post an SEO title

```bash
coho entry put @roundabout-second-opinion --set 'seoTitle={"en-US":"Roundabouts need a second opinion at peak flow"}'
```

```bash
coho entry put @elm-street-drainage --set 'seoTitle={"en-US":"What we found under Elm Street"}'
```

`seoTitle` is localized, so its value is an object of locales, as for `summary` on page 1.
Search engines cut titles off at about 60 characters, hence the trait's `max`.

## 4. Upload the gallery's photos

The gallery shows five cutaways from the repository's `sample-assets/gallery` folder:

```
coho-samples/
└── sample-assets/
    └── gallery/
        ├── 01_dam.png              an arch dam and its reservoir
        ├── 02_canal_lock.png       a canal lock and a container port
        ├── 03_interchange.png      a motorway interchange
        ├── 04_river_town.png       a town on a walled river, and its bridges
        └── 05_treatment_plant.png  a wastewater treatment plant
```

Upload each with a title, alt text and focal point, as on page 4. A slug would come from
the filename, `01-dam`, so each command names a shorter one with `--slug`:

```bash
coho asset upload ../../sample-assets/gallery/01_dam.png \
    --slug dam --title "Arch dam and reservoir" \
    --alt "Cutaway of a concrete arch dam holding back a reservoir, with its spillway, a powerhouse and transmission lines below" \
    --focal 0.52,0.45
coho asset upload ../../sample-assets/gallery/02_canal_lock.png \
    --slug canal-lock --title "Canal lock and container port" \
    --alt "Cutaway of a canal where a lock lifts a container barge, with a container port beside it and a village across the water" \
    --focal 0.52,0.48
coho asset upload ../../sample-assets/gallery/03_interchange.png \
    --slug interchange --title "Motorway interchange" \
    --alt "Cutaway of a motorway interchange: an overpass, a roundabout at each end of the slip roads, and a solar farm beside it" \
    --focal 0.50,0.48
coho asset upload ../../sample-assets/gallery/04_river_town.png \
    --slug river-town --title "River town and its bridges" \
    --alt "Cutaway of a town on a walled river, crossed by an arch bridge and a cable-stayed bridge" \
    --focal 0.62,0.51
coho asset upload ../../sample-assets/gallery/05_treatment_plant.png \
    --slug treatment-plant --title "Wastewater treatment plant" \
    --alt "Cutaway of a wastewater treatment plant beside a river, with round clarifiers, aeration tanks and digesters" \
    --focal 0.53,0.48
```

`coho asset list` shows the five slugs: `dam`, `canal-lock`, `interchange`, `river-town`
and `treatment-plant`.

## 5. Define the photo gallery

A gallery has everything a post has: a title, a body, an author, tags, citations, the
SEO fields. It also has photos. Rather than copy the post's thirteen fields into a new
type, [`types/photoGallery.json`](types/photoGallery.json) **extends** `blogPost`:

```json
{
  "_name": "Photo gallery",
  "extends": "blogPost",
  "fields": [
    { "id": "photos",          "name": "Photos",              "type": "asset",     "required": true, "many": true, "max": 24, "accept": ["image/*"] }
  ]
}
```

`fields` lists only what the gallery adds. Everything else it inherits, including the
`seo` trait, because a subtype has its parent's traits. Put it:

```bash
coho type put --file types/photoGallery.json
```

```bash
coho type get photoGallery
```

It says `extends: blogPost`, and its fields table has only `photos`.

A gallery **is** a post. That means three things, which are the point of inheritance:

- **It is listed with the posts.** `coho entry list -t blogPost` lists every post and every
  gallery. A list of `photoGallery` has only galleries.
- **A link to a post can be a gallery.** `related` links to `blogPost`, so a post's related
  posts can include a gallery, with no change to the post type.
- **It must keep the post's promises.** Anything you can count on in a post holds for a
  gallery: a gallery cannot drop `title`, or make `body` optional. It can tighten what it
  inherits, for example with `"overrides": { "title": { "max": 80 } }`, but never loosen it.

## 6. Create a gallery

[`entries/photo-galleries/civil-works-from-above.json`](entries/photo-galleries/civil-works-from-above.json)
has the gallery's text, and its SEO title and description. The links go in with `--set`,
by slug, as on page 4. `photos` is required, so it is set in the same command:

```bash
coho entry create -t photoGallery -f entries/photo-galleries/civil-works-from-above.json \
    --set author=@tom-okafor --set 'tags=["@project-notes"]' --set image=@dam \
    --set 'photos=["@dam","@canal-lock","@interchange","@river-town","@treatment-plant"]'
```

`author`, `tags` and `image` are fields the gallery inherits; `photos` is its own. List the
posts:

```bash
coho entry list -t blogPost
```

There are three: the two posts, and the gallery.

## 7. Regenerate the library

In `YourOrg.BlogContent`, pull and generate, as on page 5:

```bash
cd ~/workarea/YourOrg.BlogContent
```

```bash
dotnet coho-codegen pull && dotnet coho-codegen generate
```

Then build it:

```bash
dotnet build
```

`dotnet watch` hands the new code to the running site by itself, but only in memory. An
editor such as Rider or Visual Studio reads the library's types from its last build, so
until you build it, a Razor page shows a new type, such as `PhotoGallery`, as unknown, even though
the site compiles and runs.

There are two new files. `src/YourOrg.BlogContent/Coho/ISeo.cs` is the trait, as an
interface of its own:

```csharp
/// <summary>SEO. A trait: fields every type with it has. Take it to accept an entry of any of them.</summary>
public interface ISeo
{
    /// <summary>SEO title. Null where the locale has no translation.</summary>
    string? SeoTitle { get; }

    /// <summary>SEO description. Null where the locale has no translation.</summary>
    string? SeoDescription { get; }
}
```

Every type with the trait implements it. `BlogPost` does, and it is no longer `sealed`,
because another type extends it:

```csharp
/// <summary>Blog post. Has the trait ISeo.</summary>
public record BlogPost : EntryBase, ISeo
```

`src/YourOrg.BlogContent/Coho/PhotoGallery.cs` is the gallery. Its record derives from
`BlogPost`, so it declares only what it adds, and has everything else from its parent,
`ISeo` included:

```csharp
/// <summary>Photo gallery. Extends BlogPost, and has every field it has.</summary>
public sealed record PhotoGallery : BlogPost
{
    …
    /// <summary>Photos. Accepts image/*.</summary>
    public IReadOnlyList<Asset> Photos { get; init; } = [];
}
```

`coho.BlogPost` still reads `BlogPost`, and a gallery is one: its lists hold galleries, and
`BySlugAsync` finds one, because Coho lists a type with its subtypes. `coho.PhotoGallery`
reads galleries alone.

## 8. Build the site, and see what still compiles

`dotnet watch`, still running in `BlogSite`, picks up the new library. A change to a
record's base type is one it cannot apply while the site runs, so it offers to restart:
accept, or press Ctrl+R. Then build, to see what the gallery changed:

```bash
cd ../BlogSite
```

```bash
dotnet build
```

It succeeds, with nothing to fix. The home page's list can now hold a gallery, and
`_PostCard` takes a `BlogPost`, but a `PhotoGallery` **is** a `BlogPost`: a C# subclass,
with every property the card reads. That is what inheritance promises, in the content
model and in the code alike.

The card can still tell a gallery apart. In `Pages/Shared/_PostCard.cshtml`, mark a gallery
in the list: add this after the **Featured** badge:

```cshtml
@if (Model is PhotoGallery gallery)
{
    <span class="badge">@gallery.Photos.Count photos</span>
}
```

`Model is PhotoGallery gallery` checks the post's record type, and gives you the gallery,
so `gallery.Photos` is there, and a list. `Model.Photos` does not compile: a post has no
photos.

## 9. Write the page's metadata against the trait

The post page sets its title and description from the post. Write that once, against the
trait rather than the post, so that it works for anything with SEO fields. Open `Site.cs`,
and add this method to the class:

```csharp
/// <summary>
/// A page's title and description for search engines, from any entry with the SEO trait:
/// its own SEO fields where it has them, and what the page shows where it does not.
/// </summary>
public (string? Title, string? Description) SeoMetadata(ISeo entry, string? title, string? description)
{
    return (entry.SeoTitle ?? title, entry.SeoDescription ?? description);
}
```

In `Pages/Posts/Post.cshtml`, use it at the top, in place of the two lines that set
`ViewData["Title"]` and `ViewData["Description"]`:

```cshtml
var (title, description) = Site.SeoMetadata(post, post.Title, post.Summary);
ViewData["Title"] = title;
ViewData["Description"] = description;
```

`SeoMetadata` takes an `ISeo`, so it takes a post or a gallery, and it would take a team
member too if `teamMember` took the trait: nothing about it knows what a post is.

## 10. Show the photos

Galleries share the post's page: `coho.BlogPost.BySlugAsync` finds them. In
`Pages/Posts/Post.cshtml`, add the photos before the downloads:

```cshtml
@if (post is PhotoGallery gallery)
{
    <section class="gallery">
        <h2>Photos</h2>
        <ul>
            @foreach (var photo in gallery.Photos)
            {
                <li>
                    <coho-image src="@photo" width="400" height="300" fit="Fill" />
                </li>
            }
        </ul>
    </section>
}
```

The same check as on the card: inside it, `gallery` is the `PhotoGallery`. Each photo is an
asset, drawn by `<coho-image>` as on page 4, cropped to 400 × 300 around its focal point.
The starter's stylesheet lays the photos out as a grid. If you copied the starter before
this page was written, copy `wwwroot/site.css` from
[razor-blog-starter](../razor-blog-starter/wwwroot/site.css) again.

## 11. Check the result

Open http://localhost:5080. **Civil works, from above** is the newest post, with the dam as
its thumbnail and a **5 photos** badge. Open it: the post's usual page, with author and
tags, and a grid of the five cutaways before the end.

The browser tab shows its SEO title, **Five civil works, cut open · Field notes**, not its
title, and the roundabout post's tab starts **Roundabouts need a second opinion at peak
flow**. Both come from `SeoMetadata`, through the one trait.

## Inheritance or a trait?

Both put fields in one place and give them to several types. They answer different
questions.

|  | Inheritance: `"extends": "blogPost"` | A trait: `"traits": ["seo"]` |
|---|---|---|
| Says | a gallery **is** a post | a post **has** SEO fields |
| How many | one parent | any number of traits |
| Listed with | its parent: `coho entry list -t blogPost` includes galleries | nothing: there is no list of "things with SEO" |
| Links | a link to `blogPost` accepts a gallery | no link can name a trait |
| May change what it gets | tighten an inherited field, never loosen it | tighten a trait's field, never loosen it |
| In C# | a record deriving from `BlogPost`, matched with `is PhotoGallery` | the interface `ISeo`, which every type with it implements |
| A change to it reaches | the parent's subtypes, and their entries | every type that takes it, their subtypes, and their entries |

Ask **"is it a kind of …?"** A gallery is a kind of post: it belongs in the post list, a
reader expects it among the posts, and a "related posts" link to it makes sense. So it
extends `blogPost`.

Ask **"does it have …?"** A team member's page needs a search title and description too,
but a team member is not a post: it must not appear in the post list, or be offered as a
related post. So it would take `seo`, not extend `blogPost`. Making it extend `blogPost`
just to get the fields is the classic mistake, and Coho's rules make it costly on purpose:
it would also have to carry a post's required `body`, `layout` and `publishedAt`.

A type has one parent, so a design that seems to want two is usually one parent and some
traits: a gallery is a post, and has SEO, and could also have a `location` trait shared
with team members' office pages. Keep inheritance shallow, one or two levels; Coho refuses
more than three. Traits have no levels at all.

Either way, a change shows how far it reaches before it lands. Making `seoTitle`
required, for example, is refused with the types it would reach, `blogPost` and
`photoGallery`, and how many entries lack a value, until you confirm it.

## If something goes wrong

- **`type put` for `blogPost` fails with `FIELD_CONFLICT` on `seoDescription`:** the type
  still declares the field the trait now gives. Put
  [`types/blogPost-with-seo.json`](types/blogPost-with-seo.json), which leaves it out.
- **`type put` for `blogPost` fails with `SCHEMA_INVALID`, saying `seo` is not a trait on
  this ref:** step 1 is not done on the ref you are writing to. `coho trait list` shows
  what is there.
- **`type put` for `blogPost` is refused with `DESTRUCTIVE_SCHEMA_CHANGE`:** the trait's
  `seoDescription` differs from the post's in a way that would cost content, for example
  it is not localized, or it is required. Make it match the post's, and put the trait
  again with `coho trait put --file types/seo.json --if-match '<etag>'`.
- **`entry create` fails with `VALIDATION_FAILED` at `/author`, or stores `@tom-okafor` as
  text:** the CLI is older than 2026.1.0a20, which looks up a slug only in the fields a type
  declares itself, not those it inherits. Update it, or pass the team member's id.
- **`entry create` fails with `VALIDATION_FAILED` at `/photos`:** a gallery needs at least
  one photo, and each must be an image. `coho asset list` shows the slugs.
- **`The type or namespace name 'PhotoGallery' could not be found`, or `ISeo`:** the
  library was generated before step 5, or from another ref. Run step 7 again.
- **`'BlogPost' does not contain a definition for 'Photos'`:** `Photos` is read outside an
  `is PhotoGallery` check, where the post may be a plain post.
- **The gallery is not in the home page's list:** the library was generated before step 5,
  or from another ref. Run step 7 again, then restart `dotnet watch` with Ctrl+R.
- **The gallery is in the list, but its page is a 404:** the library runs on a
  `CohoCms.Delivery` older than 0.1.0-alpha.3, whose `BySlugAsync` on `BlogPost` keeps only
  plain posts. Update it in `YourOrg.BlogContent`, as on page 4, and generate again.
- **`coho trait delete seo` fails with `TRAIT_IN_USE`:** `blogPost` takes it. No flag
  overrides this, since a type whose trait is gone could not be read: remove `seo` from
  the type's `traits` first, after giving it back its own `seoDescription`.
- **`coho type delete blogPost` fails with `TYPE_IN_USE`, naming `photoGallery`:** a type
  others extend is not deleted while they do.
