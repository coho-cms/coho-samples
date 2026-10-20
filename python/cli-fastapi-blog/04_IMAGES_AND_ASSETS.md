# 4. Images and downloads

This page gives each blog post an image and a list of files to download. You upload the
files to Coho as assets, add two asset fields to the `blogPost` type, and link the posts to
the assets. Then the service gives them out as URLs Coho's CDN serves: a small thumbnail with
each post in the list, a wide image for the top of each post, cropped around the part that
matters, and a link to download each file.

You need the service from [Build the FastAPI service](03_APPLICATION.md), with its repeaters
in place.

The CLI steps run from inside this folder, `cli-fastapi-blog`, as on page 1. The files are in
the repository's `sample-assets` folder, two levels up:

```
coho-samples/
├── sample-assets/
│   ├── culvert.png                   a diagram of a culvert under a road
│   ├── roundabout.png                a diagram of a roundabout
│   └── roundabout-functionality.pdf  a guide to how a roundabout works
└── python/cli-fastapi-blog/          where you run the commands
```

If you have already worked through the Node.js or .NET sample's page 4 in the same project,
the assets and fields are there: skip to step 4.

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

The library's types come from the content types, so it needs generating again. In
`yourorg-blog-content`, pull the types from `dev`, and generate:

```bash
cd ~/workarea/yourorg-blog-content
```

```bash
uv run coho-codegen pull && uv run coho-codegen generate
```

`fastapi dev`, still running in `blog-api`, sees the library change, and restarts the
service with it.

`src/yourorg_blog_content/coho/blog_post.py` now has the two fields:

```python
image: runtime.Asset | None = None
"""Image. Accepts image/*. None where the asset it linked is gone."""

downloads: list[runtime.Asset] = []
"""Downloads. Accepts application/pdf."""
```

Delivery embeds an asset in the entry that links it: its URLs, title, alt text, focal point,
and the file's media type, size and dimensions. So a post read with
`coho.blog_post.by_slug` already holds everything the service needs, with no request per
image. An image is `None` when the asset it linked was deleted, and a deleted download is
left out of the list.

## 5. Build the images and the downloads

An `Asset` builds its own URLs, with no request and no credential. Three methods do it:

- **`asset.image(width=…, height=…, fit=…, format=…)`** is the image resized by Coho's CDN.
  `fit="fill"` crops it to exactly that shape, centred on its focal point. Without it, the
  image keeps its own shape, scaled to the width. `format="auto"` lets the CDN send AVIF or
  WebP to a browser that takes them.
- **`asset.srcset(…)`** is a `srcset` of the same image at several sizes, such as 1x and 2x
  for high-density screens.
- **`asset.download()`** is the original file, asked for as a download, under its own name.

The service gives them out in its own shapes. In `blog-api`, create `app/assets.py`:

```python
"""Images and downloads, as the API gives them: URLs Coho's CDN serves, built from each asset."""

from __future__ import annotations

from coho_delivery_sdk import Asset
from pydantic import BaseModel


class ImageOut(BaseModel):
    """An image, cropped to a size by Coho's CDN around its focal point."""

    src: str
    """The image at `width` × `height`."""
    srcset: str
    """The same at 1x and 2x, for high-density screens."""
    width: int
    height: int
    alt: str | None


class DownloadOut(BaseModel):
    """A file to download."""

    title: str
    url: str
    """Asks the CDN to send the file as a download, under its own name."""
    media_type: str | None
    byte_size: int | None


def image(asset: Asset | None, width: int, height: int) -> ImageOut | None:
    """An asset as an image of exactly `width` × `height`, or None when there is none."""
    if asset is None:
        return None
    return ImageOut(
        src=asset.image(width=width, height=height, fit="fill", format="auto"),
        srcset=asset.srcset(width=width, height=height, fit="fill", format="auto", densities=[1, 2]),
        width=width,
        height=height,
        alt=asset.alt,
    )


def download(asset: Asset) -> DownloadOut:
    """An asset as a file to download, titled with its title, or its filename."""
    file = asset.file
    return DownloadOut(
        title=asset.title or (file.filename if file else None) or "Download",
        url=asset.download(),
        media_type=file.media_type if file else None,
        byte_size=file.byte_size if file else None,
    )
```

- **The CDN does the resizing.** The URLs ask it for an image of the size given, and twice
  that for high-density screens. It makes each size once, and caches it.
- **Alt text comes from the asset**, so a front end can put it on the `<img>` as it is.
- **A post with no image** has `None` for it, and a front end shows none.

## 6. Give a thumbnail with each post in the list

Open `app/schemas.py`. Import the two models at the top, after the `pydantic` import:

```python
from app.assets import DownloadOut, ImageOut
```

Add a thumbnail to `PostSummary`, after `featured`:

```python
    thumbnail: ImageOut | None
```

Then in `app/routes/posts.py`, import the two functions, after `from app import site`:

```python
from app.assets import download, image
```

and give `summary` the thumbnail, after `featured=…`:

```python
        thumbnail=image(post.image, 160, 120),
```

Save, and each post in `/posts` has its thumbnail, 160 by 120, cropped around its focal point.

## 7. Add a wide image to the post

In `app/schemas.py`, add `hero` to `PostOut`, as its second field, after `slug`:

```python
    hero: ImageOut | None
```

In the `post` route, give it the image, after `slug=post.slug,`:

```python
        hero=image(post.image, 800, 200),
```

The post now has a band for its top, 800 by 200, cropped from the image around its focal
point: the roundabout's central island, and the culvert's pipe.

## 8. List the downloads

In `app/schemas.py`, add the downloads to `PostOut`, after `body_html`:

```python
    downloads: list[DownloadOut]
```

In the `post` route, after `body_html=…`:

```python
        downloads=[download(file) for file in post.downloads],
```

The roundabout post now lists **How a roundabout works**, with its size and media type. The
title is the asset's; a file with no title shows its filename. The Elm Street post has no
downloads, so its list is empty.

Run `uv run mypy` once you're done. It checks the new code against the library's types: a
download read from `post.download`, say, rather than `post.downloads`, is an error there.

## 9. Check the result

```bash
curl -s http://localhost:8000/posts/roundabout-second-opinion
```

The URLs are the CDN's, built from the asset. The hero's `src` is something like:

```
https://assets-dev.coho-cms.dev/<project-id>/i/<hash>/roundabout.png?w=800&h=200&fit=fill&fm=auto&fx=0.5&fy=0.52
```

`w` and `h` are the size, `fit=fill` the crop, `fm=auto` the format, and `fx`/`fy` the focal
point. Open it in a browser to see the crop. The same methods build a URL anywhere one
is needed, such as a social card or a CSS background.

## 10. Update the culvert image

The culvert's focal point, 0.5,0.6, is too far down: the crop cuts off the top of the pipe.
Move it to the centre of the image:

```bash
coho asset put culvert --focal 0.5,0.5
```

Then ask for the Elm Street post again. The new focal point is in the asset the next time
the service reads the post, so its `fx` and `fy` change, and the CDN makes the new crop on
its first request.

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
- **`--set image=@roundabout` is stored as the text `@roundabout`:** the type change in
  step 2 has not been saved. Check `coho type get blogPost`.
- **`"BlogPost" has no attribute "image"`:** the library was generated before the type
  changed. Run step 4 again.
- **A route fails with `This asset has no URL`:** the image is in the entry, but without its
  URLs, so `dev` is not delivering embedded assets. The Coho server needs a release that
  delivers them.
- **No thumbnail, and no error:** check that the post links an image (`coho entry get
  @elm-street-drainage`), and that the service restarted with the regenerated library: stop
  it with Ctrl+C, and start it again.

Next: [Reference repeaters and inline repeaters](05_REFERENCE_AND_INLINE_REPEATERS.md).
