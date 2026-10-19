# 3. Build the Razor Pages blog

This page wires the client library into an ASP.NET Core Razor Pages blog. Razor pages list
the blog posts, and show each post with its author and tags, all through the library's
typed reads. The types catch a misspelled field or a missing reference while you build,
before the site ever calls Coho.

You need the client library from [Create the client library](02_CLIENT_LIBRARY.md), with
its code generated. The blog brings its own settings and token: the library's `.env` only
holds the token `coho-codegen pull` uses, and never goes with it.

The site starts from [razor-blog-starter](../razor-blog-starter/README.md), a Razor Pages
app whose layout, styles, pages and reads are already written. This page adds the two
things that are yours: the library, and the repeaters that show each post, tag and related
post.

Like `BlogTest`, the site lives beside the library, outside this repository:

```
~/workarea/
├── YourOrg.BlogContent/   the client library, from page 2
├── BlogTest/              the small program, from page 2
└── BlogSite/              the blog, from this page
```

## 1. Copy the starter

From the folder you cloned the samples into:

```bash
cp -R coho-samples/dotnet/razor-blog-starter ~/workarea/BlogSite
```

Here is what it holds. The arrows mark where the repeaters go:

```
BlogSite/
├── Program.cs                  the app: Razor Pages, and the Coho client
├── Content.cs                  the only mention of the library's name
├── Site.cs                     the site's name, its locale, and how dates look
├── Pages/
│   ├── Shared/_Layout.cshtml   around every page: the header, the footer and the title
│   ├── Shared/_PostCard.cshtml one post in a list
│   ├── Index.cshtml            the home page: the latest posts      ← a repeater
│   ├── Posts/Post.cshtml       a post, with its author and tags     ← two repeaters
│   └── NotFound.cshtml         what an unknown address shows
├── TagHelpers/
│   └── MarkdownTagHelper.cs    a markdown field, such as a post's body
└── wwwroot/site.css            the styles
```

Each page's reads are in the `.cshtml.cs` file beside it, such as `Index.cshtml.cs`.

## 2. Reference the library

While you develop, the site references the library's project, as `BlogTest` does:

```bash
cd ~/workarea/BlogSite
```

```bash
dotnet add reference ../YourOrg.BlogContent/src/YourOrg.BlogContent/YourOrg.BlogContent.csproj
```

This adds one line to `RazorBlogStarter.csproj`:

```xml
<ProjectReference Include="..\YourOrg.BlogContent\src\YourOrg.BlogContent\YourOrg.BlogContent.csproj" />
```

Building the site builds the library, so a regenerated library is in the site the next
time it builds, with nothing to install, and `dotnet watch` reloads it as soon as it is
generated. When the library is published to a NuGet feed,
this line becomes a package reference, `dotnet add package YourOrg.BlogContent`, and
nothing else in the site changes. If you use a different mechanism for local development
across several projects, such as a local feed, feel free to use it instead.

The site names the library in one file, `Content.cs`:

```csharp
global using YourOrg.BlogContent;
```

If you named the library something other than `YourOrg.BlogContent`, change it there.
Every page and view sees the library's types through that line.

## 3. Say where dev is

The site reads the same values as `BlogTest`: where `dev`'s content is, and the token to
read it with. ASP.NET Core reads user secrets in `Development`, which the starter's
`Properties/launchSettings.json` already sets. Turn them on, and copy `BlogTest`'s:

```bash
dotnet user-secrets init
```

```bash
dotnet user-secrets list --json --project ../BlogTest | sed '/^\/\//d' | dotnet user-secrets set
```

`list --json` prints them between two marker lines, which `sed` removes, and `set` reads
the rest. Check that the site has them:

```bash
dotnet user-secrets list
```

```
COHO_URL = https://api-dev.coho-cms.dev
COHO_ACCOUNT = <account-id>
COHO_PROJECT = <project-id>
COHO_REF = dev
COHO_LOCALE = en-US
COHO_PREVIEW_TOKEN = <preview-token>
```

Sharing `BlogTest`'s token is fine while you try things out. A real site gets a token of
its own, so each can be revoked without breaking the other. Create one with
`coho token create --role viewer --label "blog-site preview"`, and set it with
`dotnet user-secrets set COHO_PREVIEW_TOKEN <token>`.

The client is registered once, in `Program.cs`, and reads them from the site's
configuration:

```csharp
builder.Services.AddCoho();
```

Each page model asks for it in its constructor, as `Coho coho`. The pages render on the
server, so the token never reaches a visitor's browser.

## 4. Run it

```bash
dotnet watch
```

`dotnet watch` builds and runs the site, and reloads it as you save. Open
http://localhost:5080. You see the site's name and **Latest posts**, but no posts. The
page reads them, and nothing shows them yet. That is what the repeaters are for.

## 5. List the posts

A repeater shows each item of a list with the same markup. In Razor, it is a `@foreach`
over the list. Each page already reads its content, and marks the place for each repeater
with a `Repeater:` comment.

Open `Pages/Index.cshtml.cs`. It reads the posts, newest first:

```csharp
// Newest first. Depth 1 brings each post's author and tags in the same request.
var posts = await coho.BlogPost.ListAsync(new() { Order = BlogPost.SortBy.PublishedAt.Descending, Depth = 1 }, cancellationToken);
Posts = posts.Items;
```

In `Pages/Index.cshtml`, replace the `Repeater:` comment with the `_PostCard` partial for
each post:

```cshtml
@foreach (var post in Model.Posts)
{
    <li>
        <partial name="_PostCard" model="post" />
    </li>
}
```

Save, and the page shows both posts, each with its date, its author and its summary. The
roundabout post is marked **Featured**.

`Pages/Shared/_PostCard.cshtml` shows how a card reads the author: the post was read with
`Depth = 1`, so `post.Author?.Value` is the team member itself.

## 6. Show a post's tags and related posts

Open a post. It shows its title, its author and its body, with a box about the author.
`Pages/Posts/Post.cshtml.cs` reads it by its slug, again with `Depth = 1`, so its tags and
related posts come in the same request.

In `Pages/Posts/Post.cshtml`, replace the first `Repeater:` comment, under the title, with
the post's tags:

```cshtml
@foreach (var tag in post.Tags.Resolved())
{
    <li>@tag.Name</li>
}
```

Replace the second, under **Related posts**, with a link to each related post:

```cshtml
@foreach (var related in post.Related.Resolved())
{
    <li>
        <a asp-page="/Posts/Post" asp-route-slug="@related.Slug">@related.Title</a>
    </li>
}
```

The Elm Street post now shows the Drainage and Project notes tags, and links to the
roundabout post. The roundabout post has no related posts, so it has no **Related posts**
section.

`Resolved()` is there because a reference is not always an entry. `post.Tags` is a list of
`Linked<Tag>`: each is the tag, or a stub Coho could not follow, such as a link to a
deleted tag. `Resolved()` leaves the stubs out, and gives you the tags themselves.

## 7. Let the types catch a mistake

The types come from the library, so the site knows every field. In the tags repeater,
change `tag.Name` to `tag.Nmae`. Your editor marks it straight away, and a build fails,
because Razor pages are compiled with the rest of the site:

```bash
dotnet build
```

```
Pages/Posts/Post.cshtml(28,26): error CS1061: 'Tag' does not contain a definition for 'Nmae' and no accessible extension method 'Nmae' accepting a first argument of type 'Tag' could be found (are you missing a using directive or an assembly reference?)
```

The same goes for a field removed from a content type: once the library is regenerated
without it, every read of it fails the site's build, not a page in production. Change it
back to `tag.Name`.

## 8. When the library changes

The site builds the library from its project, so a change to the library reaches the site
with nothing to install. `dotnet watch` watches the library's files as well as the site's:
regenerate the library, for example because a content type changed, and the running site
picks up the new code. A change it cannot apply while the site runs, it offers to restart
for; press Ctrl+R in its window to restart it yourself at any time.

## Where to go from here

- **Make it yours.** The site's name is in `Site.cs`, and the styles are in
  `wwwroot/site.css`. A post's `layout` field sets its width: `wide` and `landing` are
  wider.
- **Read more content** through `Coho` in a page model. An author page, for example, would
  read `coho.TeamMember.BySlugAsync(slug)`.
- **Publish it.** In production, a page is rendered again at most once a minute (output
  caching, in `Program.cs`). A published site reads released content with a delivery key,
  rather than `dev` with a token, set as the host's environment variables rather than user
  secrets. That is a later tutorial.

## If something goes wrong

- **`The type or namespace name 'YourOrg' could not be found`:** the library is not
  referenced (step 2), or it has another name: change the name in `Content.cs`.
- **`Coho: COHO_DELIVERY_URL, COHO_PROJECT, COHO_REF are needed to read released
  content`:** the site read no user secrets. Run `dotnet user-secrets list` in `BlogSite`;
  if it shows none, copy them again (step 3). Run the site with `dotnet watch` or
  `dotnet run`, which use `Properties/launchSettings.json`, so it runs in `Development`.
- **`COHO_DELIVERY_URL is needed to read released content`:** no preview token reached the
  configuration, so the site took the run for a release. Check `COHO_PREVIEW_TOKEN` with
  `dotnet user-secrets list`, then restart `dotnet watch`.
- **`COHO_ACCOUNT, COHO_PROJECT are needed to read a preview`:** set them with
  `dotnet user-secrets set` (step 3).
- **`UNAUTHENTICATED` or `PROJECT_NOT_FOUND`:** the token is wrong, expired or revoked, or
  for another project. Also check `COHO_ACCOUNT` and `COHO_PROJECT`.
- **The page shows no posts, and no error:** check the repeater in `Pages/Index.cshtml`
  (step 5). If it is there, check that `dev` has posts:
  `dotnet run --project tools/Catalog -- --preview` in `YourOrg.BlogContent`.
- **The site still shows the old library after a change:** press Ctrl+R in the
  `dotnet watch` window to restart it, as in step 8.
- **`Failed to bind to address http://127.0.0.1:5080: address already in use`:** another
  copy of the site is still running. Stop it, or change `applicationUrl` in
  `Properties/launchSettings.json`.

Next: [Images and downloads](04_IMAGES_AND_ASSETS.md).
