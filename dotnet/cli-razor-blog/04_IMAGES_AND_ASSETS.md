# 4. Images and downloads

This page gives each blog post an image and a list of files to download. You upload the
files to Coho as assets, add two asset fields to the `blogPost` type, and link the posts to
the assets. Then the blog shows them with `CohoCms.Razor`: a small thumbnail on each post
in the list, a wide image across the top of each post, cropped around the part that
matters, and a link to download each file.

You need the blog from [Build the Razor Pages blog](03_APPLICATION.md), with its repeaters
in place. Asset slugs in `coho entry put` need `coho` 2026.1.0a18 or later: check with
`coho --version`.

The CLI steps run from inside this folder, `cli-razor-blog`, as on page 1. The files are in
the repository's `sample-assets` folder, two levels up:

```
coho-samples/
├── sample-assets/
│   ├── culvert.png                   a diagram of a culvert under a road
│   ├── roundabout.png                a diagram of a roundabout
│   └── roundabout-functionality.pdf  a guide to how a roundabout works
└── dotnet/cli-razor-blog/            where you run the commands
```

If you have already worked through the Node.js sample's page 4 in the same project, the
assets and fields are there: skip to step 4.

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
need `CohoCms.Codegen` and `CohoCms.Delivery` 0.1.0-alpha.3 or later, which a library
created on page 2 already has. If yours was created with an earlier `CohoCms.Templates`,
update both, in `YourOrg.BlogContent`:

```bash
cd ~/workarea/YourOrg.BlogContent
```

```bash
dotnet tool update cohocms.codegen --prerelease
dotnet add src/YourOrg.BlogContent package CohoCms.Delivery --prerelease
```

Then pull the types from `dev`, and generate:

```bash
dotnet coho-codegen pull && dotnet coho-codegen generate
```

`src/YourOrg.BlogContent/Coho/BlogPost.cs` now has the two fields:

```csharp
/// <summary>Image. Accepts image/*. Null where the asset it linked is gone.</summary>
public Asset? Image { get; init; }

/// <summary>Downloads. Accepts application/pdf.</summary>
public IReadOnlyList<Asset> Downloads { get; init; } = [];
```

Delivery embeds an asset in the entry that links it: its URLs, title, alt text, focal point,
and the file's media type, size and dimensions. So a post read with
`coho.BlogPost.BySlugAsync` already holds everything the page needs, with no request per
image. An image is `null` when the asset it linked was deleted, and a deleted download is
left out of the list.

## 5. Add the components to the site

In `BlogSite`, add `CohoCms.Razor`:

```bash
cd ../BlogSite
```

```bash
dotnet add package CohoCms.Razor --prerelease
```

It has a tag helper for MVC views and Razor pages, and a component for Blazor, of each of
two things. `<coho-image>` shows an image resized by Coho's CDN, and `<coho-asset-link>`
links to a file. They build their URLs from the embedded asset, so they need no request and
no credential.

Register its tag helpers for every page: add this line to the end of
`Pages/_ViewImports.cshtml`:

```cshtml
@addTagHelper *, CohoCms.Razor
```

`dotnet watch` picks up the regenerated library on its own, but a new package needs a
restart: press Ctrl+R in its window.

## 6. Show a thumbnail in the post list

Open `Pages/Shared/_PostCard.cshtml`, and add the thumbnail as the first thing in the
`<article>`, above the date:

```cshtml
<coho-image src="@Model.Image" width="160" height="120" fit="Fill" class="thumbnail" />
```

Save, and each post in the list has its image beside it, 160 by 120.

- **`fit="Fill"`** crops the image to exactly that shape, centred on its focal point.
  Without it, the image keeps its own shape, scaled to the width. `fit` takes the name of
  an `ImageFit`: `Scale`, `Fill`, `Crop`, `Thumb` or `Pad`.
- **The CDN does the resizing.** The `<img>` it renders asks for a 160 pixel wide image, and
  a 320 pixel one for high-density screens, in AVIF or WebP when the browser takes them.
- **Alt text comes from the asset.** Pass `alt` to override it, or `alt=""` for a purely
  decorative image.
- **A post with no image** renders no `<img>`, and its card keeps its old layout.

The starter's stylesheet places `.thumbnail` on the right of the card.

## 7. Add a wide image to the post

Open `Pages/Posts/Post.cshtml`, and add the image at the top of the `<header>`, above the
title:

```cshtml
<coho-image src="@post.Image" width="800" height="200" fit="Fill" loading="eager" class="hero" />
```

The post now opens with a band across the top, 800 by 200, cropped from the image around
its focal point: the roundabout's central island, and the culvert's pipe. It loads straight
away, with `loading="eager"`, because it is at the top of the page; images further down load
as they scroll into view. On a narrow screen, the stylesheet scales it to fit.

## 8. List the downloads

In the same file, add a list of the post's downloads after the author's box, before
**Related posts**:

```cshtml
@if (post.Downloads.Count > 0)
{
    <section class="downloads">
        <h2>Downloads</h2>
        <ul>
            @foreach (var file in post.Downloads)
            {
                <li>
                    <coho-asset-link asset="@file" />
                </li>
            }
        </ul>
    </section>
}
```

The roundabout post now lists **How a roundabout works**. The link's text is the asset's
title. Content inside `<coho-asset-link>` replaces it, and a file with no title shows its
filename. The link asks the CDN to send the file as a download, under its own name. Add
`download="false"` to open it in the browser instead. The Elm Street post has no downloads,
so it has no **Downloads** section.

## 9. Check the result

Open http://localhost:5080. Both posts have a thumbnail. Open each post: it starts with its
wide image, and the roundabout post lists its guide under **Downloads**.

The URLs are the CDN's, built from the asset. Your browser's developer tools show the hero's
`src`, something like:

```
https://assets-dev.coho-cms.dev/<project-id>/i/<hash>/roundabout.png?w=800&h=200&fit=fill&fm=auto&fx=0.5&fy=0.52
```

`w` and `h` are the size, `fit=fill` the crop, `fm=auto` the format, and `fx`/`fy` the focal
point. The CDN caches each size it makes, and the same `Image()`, `Srcset()` and
`Download()` methods are on `Asset` for anywhere a tag helper does not fit, such as a CSS
background or a social card.

## 10. Update the culvert image

The culvert's focal point, 0.5,0.6, is too far down: the crop cuts off the top of the pipe.
Move it to the centre of the image:

```bash
coho asset put culvert --focal 0.5,0.5
```

Then refresh the page. The new focal point is in the asset the next time the page reads the
post, and the CDN makes the new crop on its first request.

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
- **`BlogPost` has no `Image` property:** the library was generated before the type changed,
  or with a `CohoCms.Codegen` older than 0.1.0-alpha.3. Run step 4 again.
- **`<coho-image>` is in the page's HTML as it was written, not as an `<img>`:** the tag
  helpers are not registered, or the package is not installed, and the build does not say
  which. Check `@addTagHelper *, CohoCms.Razor` in `Pages/_ViewImports.cshtml`, and that
  `RazorBlogStarter.csproj` references `CohoCms.Razor` (step 5). Then press Ctrl+R in the
  `dotnet watch` window.
- **`'ImageFit' does not contain a definition for 'fill'`:** `fit` takes the name of an `ImageFit` as C# writes it,
  `Fill`, with a capital.
- **The page fails with `This asset has no URL`:** the image is in the entry, but without its
  URLs, so `dev` is not delivering embedded assets. The Coho server needs a release that
  delivers them.
- **No thumbnail, and no error:** check that the post links an image (`coho entry get
  @elm-street-drainage`), and that the site has the regenerated library: press Ctrl+R in
  the `dotnet watch` window.

Next: [Reference repeaters and inline repeaters](05_REFERENCE_AND_INLINE_REPEATERS.md).
