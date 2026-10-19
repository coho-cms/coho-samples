# 4. Images and downloads

This page gives each blog post an image and a list of files to download. You upload the
files to Coho as assets, add two asset fields to the `blogPost` type, and link the posts to
the assets. Then the blog shows them with `@coho-cms/react`: a small thumbnail on each post
in the list, a wide image across the top of each post, cropped around the part that
matters, and a link to download each file.

You need the blog from [Build the Next.js blog](03_APPLICATION.md), with its repeaters in
place. Asset slugs in `coho entry put` need `coho` 2026.1.0a18 or later: check with
`coho --version`.

The CLI steps run from inside this folder, `cli-next-blog`, as on page 1. The files are in
the repository's `sample-assets` folder, two levels up:

```
coho-samples/
├── sample-assets/
│   ├── culvert.png                   a diagram of a culvert under a road
│   ├── roundabout.png                a diagram of a roundabout
│   └── roundabout-functionality.pdf  a guide to how a roundabout works
└── node/cli-next-blog/               where you run the commands
```

## 1. Upload the files

An asset is a file Coho stores and serves from its own CDN, with a slug, a title, alt text
for images, and a focal point: where a crop centres. Upload the two images, each with
its alt text and focal point:

```bash
coho asset upload ../../sample-assets/roundabout.png --title "Roundabout anatomy" \
    --alt "Diagram of a single-lane roundabout, with its central island, splitter islands and crossings" \
    --focal 0.5,0.52
```

```bash
coho asset upload ../../sample-assets/culvert.png --title "Culvert through a road embankment" \
    --alt "Cutaway of a road embankment, showing the culvert pipe that carries a stream under the road" \
    --focal 0.5,0.6
```

The focal point is a pair of fractions, across and down: `0.5,0.52` is the middle of the
roundabout's central island. Then upload the PDF. A PDF has no alt text or focal point,
just a title:

```bash
coho asset upload ../../sample-assets/roundabout-functionality.pdf --title "How a roundabout works"
```

Each upload says what it stored, and warns that asset URLs are public: anyone with the URL
can open the file, even one only a draft links to. Each slug comes from the filename, so the
assets are `roundabout`, `culvert` and `roundabout-functionality`. List them:

```bash
coho asset list
```

## 2. Add asset fields to the type

[`types/blogPost-with-assets.json`](types/blogPost-with-assets.json) is the `blogPost` type
from page 1, with two fields added at the end:

```json
{ "id": "image",     "name": "Image",     "type": "asset", "accept": ["image/*"] },
{ "id": "downloads", "name": "Downloads", "type": "asset", "many": true, "max": 5, "accept": ["application/pdf"] }
```

An `asset` field links assets, as a `reference` field links entries. `accept` says which
media types it takes: any image for `image`, and only PDFs for `downloads`. `many` makes
`downloads` a list, of at most five.

The type already exists, so Coho needs to know you are changing the version you last saw. This ensures
that no one else sneaks in and makes a change while you're not looking. 

Read the type, and note its ETag:

```bash
coho type get blogPost
```

Then put the new definition, passing that ETag as it is shown, quotes and all:

```bash
coho type put --file types/blogPost-with-assets.json --if-match '<etag>'
```

Adding fields changes no entry: the posts simply have no image or downloads yet.

## 3. Link the posts to the assets

Name each asset by its slug, with an `@`, as you named entries on page 1. The CLI looks the
slug up among the assets, because the field is an asset field:

```bash
coho entry put @roundabout-second-opinion --set image=@roundabout \
    --set 'downloads=["@roundabout-functionality"]'
```

```bash
coho entry put @elm-street-drainage --set image=@culvert
```

Coho checks each link against the field's `accept`, using the media type it found in the
file, not its name. Linking the PDF as an `image` is refused with `VALIDATION_FAILED`.

## 4. Regenerate the library

The library's types come from the content types, so it needs generating again. Asset fields
need `@coho-cms/codegen` and `@coho-cms/delivery` 0.1.0-alpha.6 or later. In
`blog-content`, update both:

```bash
cd ~/workarea/blog-content
```

```bash
npm install -D @coho-cms/codegen@alpha @coho-cms/delivery@alpha
```

Then pull the types from `dev`, generate, and pack the library again, as on page 3:

```bash
npm run pull && npm run generate
```

```bash
npm pack
```

`src/coho/BlogPost.ts` now has the two fields:

```ts
/** Image. Accepts image/*. */
readonly image?: runtime.Asset | null;

/** Downloads. Accepts application/pdf. */
readonly downloads?: readonly runtime.Asset[];
```

Delivery embeds an asset in the entry that links it: its URLs, title, alt text, focal point,
and the file's media type, size and dimensions. So a post read with `coho.blogPost.bySlug`
already holds everything the page needs, with no request per image. An image is `null`
when the asset it linked was deleted, and a deleted download is left out of the list.

## 5. Add the components to the site

In `blog-site`, install the new tarball, and `@coho-cms/react` with the version of
`@coho-cms/delivery` it is built on:

```bash
cd ../blog-site
```

```bash
npm install ../blog-content/your-org-blog-content-0.1.0.tgz @coho-cms/react@alpha @coho-cms/delivery@alpha
```

Restart `npm run dev`, so it picks up the new library.

`@coho-cms/react` has two components. `<CohoImage>` shows an image resized by Coho's CDN,
and `<CohoAssetLink>` links to a file. They build their URLs from the embedded asset, so
they need no request and no credential, and they work in server components like these
pages.

## 6. Show a thumbnail in the post list

Open `components/post-card.tsx`. Import the component at the top:

```tsx
import { CohoImage } from '@coho-cms/react';
```

Then add the thumbnail as the first thing in the `<article>`, above the date:

```tsx
<CohoImage src={post.image} width={160} height={120} fit="fill" className="thumbnail" />
```

Save, and each post in the list has its image beside it, 160 by 120.

- **`fit="fill"`** crops the image to exactly that shape, centred on its focal point.
  Without it, the image keeps its own shape, scaled to the width.
- **The CDN does the resizing.** The `<img>` it renders asks for a 160 pixel wide image, and
  a 320 pixel one for high-density screens, in AVIF or WebP when the browser takes them.
- **Alt text comes from the asset.** Pass `alt` to override it, or `alt=""` for a purely
  decorative image.
- **A post with no image** renders no `<img>`, and its card keeps its old layout.

The starter's stylesheet places `.thumbnail` on the right of the card.

## 7. Add a wide image to the post

Open `app/posts/[slug]/page.tsx`, and import both components:

```tsx
import { CohoAssetLink, CohoImage } from '@coho-cms/react';
```

Add the image at the top of the `<header>`, above the title:

```tsx
<CohoImage src={post.image} width={800} height={200} fit="fill" loading="eager" className="hero" />
```

The post now opens with a band across the top, 800 by 200, cropped from the image around
its focal point: the roundabout's central island, and the culvert's pipe. It loads straight
away, with `loading="eager"`, because it is at the top of the page; images further down load
as they scroll into view. On a narrow screen, the stylesheet scales it to fit.

## 8. List the downloads

In the same file, add a list of the post's downloads after the author's box, before
**Related posts**:

```tsx
{post.downloads && post.downloads.length > 0 && (
  <section className="downloads">
    <h2>Downloads</h2>
    <ul>
      {post.downloads.map((file) => (
        <li key={file.id}>
          <CohoAssetLink asset={file} />
        </li>
      ))}
    </ul>
  </section>
)}
```

The roundabout post now lists **How a roundabout works**. The link's text is the asset's
title. Children of `<CohoAssetLink>` replace it, and a file with no title shows its
filename. The link asks the CDN to send the file as a download, under its own name. Pass
`download={false}` to open it in the browser instead. The Elm Street post has no downloads,
so it has no **Downloads** section.

## 9. Check the result

Open http://localhost:3000. Both posts have a thumbnail. Open each post: it starts with its
wide image, and the roundabout post lists its guide under **Downloads**.

The URLs are the CDN's, built from the asset. Your browser's developer tools show the hero's
`src`, something like:

```
https://assets-dev.coho-cms.dev/<project-id>/i/<hash>/roundabout.png?w=800&h=200&fit=fill&fm=auto&fx=0.5&fy=0.52
```

`w` and `h` are the size, `fit=fill` the crop, `fm=auto` the format, and `fx`/`fy` the focal
point. The CDN caches each size it makes, and the same `imageUrl`, `srcset` and
`downloadUrl` functions are in `@coho-cms/delivery` for anywhere a component does not fit,
such as a CSS background or a social card.

## 10. Update the culvert image

Note that for the culvert image, we set the focal point at 0.5,0.6. This really was way too far down. 

So let's update it to relocate the focal point to the center of the image. 

```bash
coho asset put culvert --focal 0.5,0.5
```
Then refresh the page. It will take a split second for the new focal point to re-render and voila, it's 
changed. 

## If something goes wrong

- **`asset upload` says `ASSET_TYPE_NOT_ALLOWED`:** Coho stores images, video, audio and
  PDF. The media type comes from the file's contents, not its name.
- **`type put` says the type exists:** pass `--if-match` with the ETag from
  `coho type get blogPost`. With `VERSION_CONFLICT`, the type changed since you read it:
  read it again.
- **`type put` fails with `SCHEMA_INVALID` naming `accept`:** each value must be a media type
  Coho stores, such as `application/pdf`, or `image/*`, `video/*` or `audio/*`. `image/jpg`
  is a common typo for `image/jpeg`.
- **`entry put` says `ASSET_NOT_FOUND`:** no asset on the ref has that slug. Check the
  slugs with `coho asset list`.
- **`entry put` fails with `VALIDATION_FAILED`:** the asset's media type is not one the field
  accepts, such as the PDF linked as the `image`.
- **`--set image=@roundabout` is stored as the text `@roundabout`:** the CLI is older than
  2026.1.0a18, or the type change in step 2 has not been saved. Check `coho --version`, and
  `coho type get blogPost`.
- **`BlogPost` has no `image` field:** the library was generated before the type changed, or
  with a `@coho-cms/codegen` older than 0.1.0-alpha.6. Run step 4 again, then install the new
  tarball in the site.
- **The page fails with `This asset has no URL`:** the image is in the entry, but without its
  URLs, so `dev` is not delivering embedded assets. The Coho server needs a release that
  delivers them.
- **No thumbnail, and no error:** check that the post links an image (`coho entry get
  @elm-street-drainage`), and that the site shows the new library: restart `npm run dev`.

Next: [Reference repeaters and inline repeaters](05_REFERENCE_AND_INLINE_REPEATERS.md).
