# 6. Traits and inheritance

The blog has one kind of entry with a page of its own, the post. This page shares fields
two ways. First, a **trait**: the post's search-engine fields move into a group of their
own, `seo`, which any type can take, and the group gains an SEO title. Then a
**subtype**: a photo gallery is a new kind of post, with everything a post has and a list
of photos besides, and it is listed among the posts.

You need the blog from [Reference repeaters and inline repeaters](05_REFERENCE_AND_INLINE_REPEATERS.md).
Traits and subtypes need `coho` 2026.1.0a20 or later (check with `coho --version`),
`@coho-cms/codegen` and `@coho-cms/delivery` 0.1.0-alpha.8 or later, and a Coho server
that has them. The CLI steps run from inside this folder, `cli-next-blog`, as on page 1.

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
coho asset upload ../../sample-assets/gallery/01_dam.png --slug dam --title "Arch dam and reservoir" \
    --alt "Cutaway of a concrete arch dam holding back a reservoir, with its spillway, a powerhouse and transmission lines below" \
    --focal 0.52,0.45
```

```bash
coho asset upload ../../sample-assets/gallery/02_canal_lock.png --slug canal-lock --title "Canal lock and container port" \
    --alt "Cutaway of a canal where a lock lifts a container barge, with a container port beside it and a village across the water" \
    --focal 0.52,0.48
```

```bash
coho asset upload ../../sample-assets/gallery/03_interchange.png --slug interchange --title "Motorway interchange" \
    --alt "Cutaway of a motorway interchange: an overpass, a roundabout at each end of the slip roads, and a solar farm beside it" \
    --focal 0.50,0.48
```

```bash
coho asset upload ../../sample-assets/gallery/04_river_town.png --slug river-town --title "River town and its bridges" \
    --alt "Cutaway of a town on a walled river, crossed by an arch bridge and a cable-stayed bridge" \
    --focal 0.62,0.51
```

```bash
coho asset upload ../../sample-assets/gallery/05_treatment_plant.png --slug treatment-plant --title "Wastewater treatment plant" \
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

In `blog-content`, update the generator and the runtime to 0.1.0-alpha.8 or later, then
pull, generate and pack:

```bash
cd ~/workarea/blog-content
```

```bash
npm install -D @coho-cms/codegen@alpha @coho-cms/delivery@alpha
```

```bash
npm run pull && npm run generate
```

```bash
npm pack
```

There are two new files. `src/coho/Seo.ts` is the trait, as an interface of its own:

```ts
/** SEO. A trait: fields that every type with it has. Take it to accept an entry of any of them. */
export interface Seo
{
    /** SEO title. Absent where the locale has no translation. */
    readonly seoTitle?: string;

    /** SEO description. Absent where the locale has no translation. */
    readonly seoDescription?: string;
}
```

Every type with the trait extends it, the post and the gallery alike:

```ts
export interface BlogPost extends runtime.EntryBase<"blogPost">, Seo
```

`src/coho/PhotoGallery.ts` is the gallery, with every field it has, its own `photos` last:

```ts
/** Photo gallery. Extends BlogPost, and has every field it has. Has the trait Seo. */
export interface PhotoGallery extends runtime.EntryBase<"photoGallery">, Seo
{
    …
    /** Photos. Accepts image/*. */
    readonly photos: readonly runtime.Asset[];
}
```

And `BlogPost.ts` gains a union of every kind of post:

```ts
export type AnyBlogPost = BlogPost | PhotoGallery;
```

`coho.blogPost` now reads `AnyBlogPost`: its lists hold galleries, and `bySlug` finds one,
because Coho lists a type with its subtypes. `coho.photoGallery` reads galleries alone.

## 8. Install the library, and follow the compiler

In `blog-site`, install the new tarball and the new runtime:

```bash
cd ../blog-site
```

```bash
npm install ../blog-content/your-org-blog-content-0.1.0.tgz @coho-cms/delivery@alpha
```

Open `lib/coho.ts`, and pass on the new types:

```ts
export type { AnyBlogPost, BlogPost, Citation, PhotoGallery, Seo, Tag, TeamMember } from '@your-org/blog-content';
```

Now ask TypeScript what the gallery changed:

```bash
npx tsc --noEmit
```

```
app/page.tsx(14,29): error TS2322: Type 'AnyBlogPost' is not assignable to type 'BlogPost'.
  Type 'PhotoGallery' is not assignable to type 'BlogPost'.
    Types of property '_type' are incompatible.
      Type '"photoGallery"' is not assignable to type '"blogPost"'.
```

The home page's list of posts can now hold a gallery, and `PostCard` takes only a
`BlogPost`. That is the one place to change: everything the card reads, a gallery has too.
Open `components/post-card.tsx`, and take any kind of post:

```tsx
import { isResolved, type AnyBlogPost } from '@/lib/coho';
```

```tsx
export function PostCard({ post }: { post: AnyBlogPost }) {
```

While you are there, mark a gallery in the list. Add this after the **Featured** badge:

```tsx
{post._type === 'photoGallery' && <span className="badge">{post.photos.length} photos</span>}
```

`post._type === 'photoGallery'` narrows `post` to a `PhotoGallery`, so `post.photos` is
there, and a list. Outside the check, `post.photos` does not compile: a post has no photos.
Run `npx tsc --noEmit` again. It prints nothing.

## 9. Write the page's metadata against the trait

The post page sets its title and description from the post. Write that once, against the
trait rather than the post, so that it works for anything with SEO fields. Open
`lib/site.ts`, add two imports at the top:

```ts
import type { Metadata } from 'next';
import type { Seo } from '@/lib/coho';
```

and add this at the end:

```ts
/**
 * A page's title and description for search engines, from any entry with the SEO trait:
 * its own SEO fields where it has them, and what the page shows where it does not.
 */
export function seoMetadata(entry: Seo, fallback: { title?: string; description?: string }): Metadata {
  return {
    title: entry.seoTitle ?? fallback.title,
    description: entry.seoDescription ?? fallback.description,
  };
}
```

In `app/posts/[slug]/page.tsx`, import it beside `formatDate`:

```tsx
import { formatDate, seoMetadata } from '@/lib/site';
```

and use it in `generateMetadata`:

```tsx
return seoMetadata(post, { title: post.title, description: post.summary });
```

`seoMetadata` takes a `Seo`, so it takes a post or a gallery, and it would take a team
member too if `teamMember` took the trait: nothing about it knows what a post is.

## 10. Show the photos

Galleries share the post's page: `coho.blogPost.bySlug` finds them. In
`app/posts/[slug]/page.tsx`, add the photos before the downloads:

```tsx
{post._type === 'photoGallery' && (
  <section className="gallery">
    <h2>Photos</h2>
    <ul>
      {post.photos.map((photo) => (
        <li key={photo.id}>
          <CohoImage src={photo} width={400} height={300} fit="fill" />
        </li>
      ))}
    </ul>
  </section>
)}
```

The same narrowing as on the card: inside the check, `post` is a `PhotoGallery`. Each
photo is an asset, drawn by `CohoImage` as on page 4, cropped to 400 × 300 around its
focal point.

The starter's stylesheet lays the photos out in a grid. If you copied the starter before
this page was written, add these rules to the end of `app/globals.css`:

```css
.gallery {
  margin-top: 3rem;
}

.gallery h2 {
  margin-block: 0 0.75rem;
  color: var(--muted);
  font-size: 0.875rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.gallery ul {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(12rem, 1fr));
  gap: 0.75rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.gallery img {
  display: block;
  width: 100%;
  height: auto;
}
```

## 11. Check the result

Restart `npm run dev`, and open the home page. **Civil works, from above** is the newest
post, with the dam as its thumbnail and a **5 photos** badge. Open it: the post's usual
page, with author and tags, and a grid of the five cutaways before the end.

The browser tab shows its SEO title, **Five civil works, cut open · Field notes**,
not its title, and the roundabout post's tab starts **Roundabouts need a second opinion
at peak flow**.
Both come from `seoMetadata`, through the one trait.

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
| In TypeScript | `AnyBlogPost`, narrowed on `_type` | the interface `Seo`, which every type with it extends |
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
- **`npx tsc --noEmit` says `post.photos` does not exist on `BlogPost`:** `post.photos` is
  outside a `post._type === 'photoGallery'` check, where `post` may be a plain post.
- **The gallery is not in the home page's list:** the library was generated before step 5,
  or from another ref. Run step 7 again, and reinstall the tarball.
- **The gallery is in the list, but its page is a 404:** the site runs
  `@coho-cms/delivery` older than 0.1.0-alpha.8, whose `bySlug` on `blogPost` keeps only
  plain posts. Install `@coho-cms/delivery@alpha` in `blog-site`, as in step 8.
- **`coho trait delete seo` fails with `TRAIT_IN_USE`:** `blogPost` takes it. No flag
  overrides this, since a type whose trait is gone could not be read: remove `seo` from
  the type's `traits` first, after giving it back its own `seoDescription`.
- **`coho type delete blogPost` fails with `TYPE_IN_USE`, naming `photoGallery`:** a type
  others extend is not deleted while they do.
