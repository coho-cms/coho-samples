# 4. Images and downloads

This page gives each blog post an image and a list of files to download. You upload the
files to Coho as assets, add two asset fields to the `blogPost` type, and link the posts to
the assets. Then the service gives them out as URLs Coho's CDN serves: a small thumbnail with
each post in the list, a wide image for the top of each post, cropped around the part that
matters, and a link to download each file.

You need the service from [Build the Ktor service](03_APPLICATION.md), with its
repeaters in place.

The CLI steps run from inside this folder, `cli-ktor-blog`, as on page 1. The files are in
the repository's `sample-assets` folder, two levels up:

```
coho-samples/
├── sample-assets/
│   ├── culvert.png                   a diagram of a culvert under a road
│   ├── roundabout.png                a diagram of a roundabout
│   └── roundabout-functionality.pdf  a guide to how a roundabout works
└── kotlin/cli-ktor-blog/          where you run the commands
```

If you have already worked through another sample's page 4 in the same project, the assets
and fields are there: skip to step 4.

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
`blog-content`, pull the types from `dev`, and generate:

```bash
cd ~/workarea/blog-content
```

```bash
./gradlew cohoPull cohoGenerate
```

`BlogPost.kt` now has the two fields:

```kotlin
/** Image. Accepts image/\*. Null where the asset it linked is gone. */
val image: Asset? = entry.asset("image")

/** Downloads. Accepts application/pdf. */
val downloads: List<Asset> = entry.assets("downloads")
```

Delivery embeds an asset in the entry that links it: its URLs, title, alt text, focal point,
and the file's media type, size and dimensions. So a post read with
`coho.blogPost.bySlugAsync(…)` already holds everything the service needs, with no request
per image. An image is null when the asset it linked was deleted, and a deleted download is
left out of the list.

## 5. Build the images and the downloads

An `Asset` builds its own URLs, with no request and no credential. Three methods do it:

- **`asset.image(options)`** is the image resized by Coho's CDN. `ImageOptions.fill(width,
  height)` crops it to exactly that shape, centred on its focal point; `ImageOptions(width =
  …)` keeps its shape. `withFormat(ImageFormat.AUTO)` lets the CDN send AVIF or WebP to a
  browser that takes them.
- **`asset.srcsetDensities(options, densities)`** is a `srcset` of the same image at each
  pixel density, such as 1x and 2x for high-density screens.
- **`asset.download()`** is the original file, asked for as a download, under its own name.

The service gives them out in its own shapes. In `blog-api`, create
`src/main/kotlin/com/example/blog/Assets.kt`:

```kotlin
package com.example.blog

import com.cohocms.delivery.Asset
import com.cohocms.delivery.ImageFormat
import com.cohocms.delivery.ImageOptions
import kotlinx.serialization.Serializable

// Images and downloads, as the API gives them: URLs Coho's CDN serves, built from each asset.

/** An image, cropped to a size by Coho's CDN around its focal point. */
@Serializable
data class ImageOut(
    /** The image at width × height. */
    val src: String,
    /** The same at 1x and 2x, for high-density screens. */
    val srcset: String,
    val width: Int,
    val height: Int,
    val alt: String?,
)

/** A file to download. */
@Serializable
data class DownloadOut(
    val title: String,
    /** Asks the CDN to send the file as a download, under its own name. */
    val url: String,
    val mediaType: String?,
    val byteSize: Long?,
)

/** An asset as an image of exactly [width] × [height], or null when there is none. */
fun image(asset: Asset?, width: Int, height: Int): ImageOut?
{
    asset ?: return null
    val crop = ImageOptions.fill(width, height).withFormat(ImageFormat.AUTO)
    return ImageOut(asset.image(crop), asset.srcsetDensities(crop, listOf(1.0, 2.0)), width, height, asset.alt)
}

/** An asset as a file to download, titled with its title, or its filename. */
fun download(asset: Asset) = DownloadOut(
    title = asset.title ?: asset.file?.filename ?: "Download",
    url = asset.download(),
    mediaType = asset.file?.mediaType,
    byteSize = asset.file?.byteSize,
)
```

- **The CDN does the resizing.** The URLs ask it for an image of the size given, and twice
  that for high-density screens. It makes each size once, and caches it.
- **Alt text comes from the asset**, so a front end can put it on the `<img>` as it is.
- **A post with no image** has null for it, and a front end shows none.

## 6. Give a thumbnail with each post in the list

Open `Api.kt`, and add a thumbnail to `PostSummary`, after `featured`:

```kotlin
    val featured: Boolean,
    val thumbnail: ImageOut?,
```

Then in `Posts.kt`, give `summary` the thumbnail, after `featured = …`:

```kotlin
        thumbnail = image(post.image, 160, 120),
```

Restart the service, and each post in `/posts` has its thumbnail, 160 by 120, cropped around
its focal point.

## 7. Add a wide image to the post

In `Api.kt`, add `hero` to `PostOut`, after `related`:

```kotlin
    val related: List<PostLink>,
    val hero: ImageOut?,
```

In the `/posts/{slug}` route, give it the image, after `related = …`:

```kotlin
                hero = image(post.image, 800, 200),
```

The post now has a band for its top, 800 by 200, cropped from the image around its focal
point: the roundabout's central island, and the culvert's pipe.

## 8. List the downloads

In `Api.kt`, add the downloads to `PostOut`, after `hero`:

```kotlin
    val hero: ImageOut?,
    val downloads: List<DownloadOut>,
```

In the route, after `hero = …`:

```kotlin
                downloads = post.downloads.map { download(it) },
```

The roundabout post now lists **How a roundabout works**, with its size and media type. The
title is the asset's; a file with no title shows its filename. The Elm Street post has no
downloads, so its list is empty.

## 9. Check the result

Restart the service, and ask for the roundabout post:

```bash
curl -s http://localhost:8080/posts/roundabout-second-opinion
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
- **`Unresolved reference 'image'`:** the library was generated before the type changed. Run
  step 4 again.
- **`No value passed for parameter 'thumbnail'`:** the class has a property the call does not
  give. Check both edits of the step.
- **A route fails with `This asset has no URL`:** the image is in the entry, but without its
  URLs, so `dev` is not delivering embedded assets. The Coho server needs a release that
  delivers them.
- **No thumbnail, and no error:** check that the post links an image (`coho entry get
  @elm-street-drainage`), and that you restarted the service after regenerating.

Next: [Reference repeaters and inline repeaters](05_REFERENCE_AND_INLINE_REPEATERS.md).
