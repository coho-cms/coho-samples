# 4. Images and downloads

This page gives each blog post an image and a list of files to download. You upload the
files to Coho as assets, add two asset fields to the `blogPost` type, and link the posts to
the assets. Then the service gives them out as URLs Coho's CDN serves: a small thumbnail with
each post in the list, a wide image for the top of each post, cropped around the part that
matters, and a link to download each file.

You need the service from [Build the Spring Boot service](03_APPLICATION.md), with its
repeaters in place.

The CLI steps run from inside this folder, `cli-spring-blog`, as on page 1. The files are in
the repository's `sample-assets` folder, two levels up:

```
coho-samples/
├── sample-assets/
│   ├── culvert.png                   a diagram of a culvert under a road
│   ├── roundabout.png                a diagram of a roundabout
│   └── roundabout-functionality.pdf  a guide to how a roundabout works
└── java/cli-spring-blog/          where you run the commands
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

`BlogPost.java` now has the two fields:

```java
/** Image. Accepts image/*. Null where the asset it linked is gone. */
public @Nullable Asset getImage()

/** Downloads. Accepts application/pdf. */
public List<Asset> getDownloads()
```

Delivery embeds an asset in the entry that links it: its URLs, title, alt text, focal point,
and the file's media type, size and dimensions. So a post read with
`coho.blogPost().bySlug(…)` already holds everything the service needs, with no request per
image. An image is null when the asset it linked was deleted, and a deleted download is left
out of the list.

## 5. Build the images and the downloads

An `Asset` builds its own URLs, with no request and no credential. Three methods do it:

- **`asset.image(options)`** is the image resized by Coho's CDN. `ImageOptions.fill(width,
  height)` crops it to exactly that shape, centred on its focal point; `ImageOptions.width(…)`
  keeps its shape. `withFormat(ImageFormat.AUTO)` lets the CDN send AVIF or WebP to a browser
  that takes them.
- **`asset.srcsetDensities(options, densities)`** is a `srcset` of the same image at each
  pixel density, such as 1x and 2x for high-density screens.
- **`asset.download()`** is the original file, asked for as a download, under its own name.

The service gives them out in its own shapes. In `blog-api`, create
`src/main/java/com/example/blog/api/Assets.java`:

```java
package com.example.blog.api;

import com.cohocms.delivery.Asset;
import com.cohocms.delivery.AssetFile;
import com.cohocms.delivery.ImageFormat;
import com.cohocms.delivery.ImageOptions;
import java.util.List;
import org.jspecify.annotations.Nullable;

/** Images and downloads, as the API gives them: URLs Coho's CDN serves, built from each asset. */
public final class Assets
{
    private Assets()
    {
    }

    /**
     * An image, cropped to a size by Coho's CDN around its focal point.
     *
     * @param src The image at width × height.
     * @param srcset The same at 1x and 2x, for high-density screens.
     */
    public record ImageOut(String src, String srcset, int width, int height, @Nullable String alt)
    {
    }

    /**
     * A file to download.
     *
     * @param url Asks the CDN to send the file as a download, under its own name.
     */
    public record DownloadOut(String title, String url, @Nullable String mediaType, @Nullable Long byteSize)
    {
    }

    /** An asset as an image of exactly width × height, or null when there is none. */
    public static @Nullable ImageOut image(@Nullable Asset asset, int width, int height)
    {
        if (asset == null)
        {
            return null;
        }
        ImageOptions crop = ImageOptions.fill(width, height).withFormat(ImageFormat.AUTO);
        return new ImageOut(asset.image(crop), asset.srcsetDensities(crop, List.of(1.0, 2.0)), width, height, asset.getAlt());
    }

    /** An asset as a file to download, titled with its title, or its filename. */
    public static DownloadOut download(Asset asset)
    {
        AssetFile file = asset.getFile();
        String title = asset.getTitle() != null ? asset.getTitle() : file != null && file.getFilename() != null ? file.getFilename() : "Download";
        return new DownloadOut(title, asset.download(), file != null ? file.getMediaType() : null, file != null ? file.getByteSize() : null);
    }
}
```

- **The CDN does the resizing.** The URLs ask it for an image of the size given, and twice
  that for high-density screens. It makes each size once, and caches it.
- **Alt text comes from the asset**, so a front end can put it on the `<img>` as it is.
- **A post with no image** has null for it, and a front end shows none.

## 6. Give a thumbnail with each post in the list

Open `api/Api.java`. Import the two records, before the `java.time` import:

```java
import com.example.blog.api.Assets.DownloadOut;
import com.example.blog.api.Assets.ImageOut;
```

Add a thumbnail to `PostSummary`, as its last component, after `boolean featured`:

```java
        boolean featured,
        @Nullable ImageOut thumbnail)
```

Then in `PostsController.java`, import `Assets`, after the `AuthorOut` import:

```java
import com.example.blog.api.Assets;
```

and give `summary` the thumbnail, as its last argument:

```java
            Boolean.TRUE.equals(post.getFeatured()),
            Assets.image(post.getImage(), 160, 120));
```

Restart the service, and each post in `/posts` has its thumbnail, 160 by 120, cropped around
its focal point. Each new component goes last, here and on the pages that follow, so each
record and the call that builds it stay in the same order.

## 7. Add a wide image to the post

In `Api.java`, add `hero` to `PostOut`, as its last component, after `List<PostLink> related`:

```java
        List<PostLink> related,
        @Nullable ImageOut hero)
```

In the `post` route, give it the image, as the last argument:

```java
            Linked.resolved(post.getRelated()).stream().map(related -> link(related)).toList(),
            Assets.image(post.getImage(), 800, 200));
```

The post now has a band for its top, 800 by 200, cropped from the image around its focal
point: the roundabout's central island, and the culvert's pipe.

## 8. List the downloads

In `Api.java`, add the downloads to `PostOut`, after `hero`:

```java
        @Nullable ImageOut hero,
        List<DownloadOut> downloads)
```

In the `post` route, after the hero:

```java
            Assets.image(post.getImage(), 800, 200),
            post.getDownloads().stream().map(file -> Assets.download(file)).toList());
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
- **`cannot find symbol: method getImage()`:** the library was generated before the type
  changed. Run step 4 again.
- **`constructor PostSummary in record PostSummary cannot be applied to given types`:** the
  record and the call that builds it have different components. Check that each new one is
  last in both.
- **A route fails with `This asset has no URL`:** the image is in the entry, but without its
  URLs, so `dev` is not delivering embedded assets. The Coho server needs a release that
  delivers them.
- **No thumbnail, and no error:** check that the post links an image (`coho entry get
  @elm-street-drainage`), and that you restarted the service after regenerating.

Next: [Reference repeaters and inline repeaters](05_REFERENCE_AND_INLINE_REPEATERS.md).
