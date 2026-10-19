# Razor Pages blog starter

An ASP.NET Core Razor Pages blog, ready to read its posts from Coho. The layout, the styles,
the pages and the reads are done. What is left is yours: the reference to your content
library, and the repeaters that show each post, tag and related post on the page.

It is built for the content model in [cli-razor-blog](../cli-razor-blog/README.md), with the
`blogPost`, `teamMember` and `tag` types, and the client library from
[Create the client library](../cli-razor-blog/02_CLIENT_LIBRARY.md).
[Build the Razor Pages blog](../cli-razor-blog/03_APPLICATION.md) walks through setting it
up, step by step.

```
razor-blog-starter/
├── Program.cs                  the app: Razor Pages, and the Coho client
├── Content.cs                  the only mention of your library's name
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

## In short

1. Copy this folder beside your library, such as `~/workarea/BlogSite` next to
   `~/workarea/YourOrg.BlogContent`.
2. Reference the library's project:
   `dotnet add reference ../YourOrg.BlogContent/src/YourOrg.BlogContent/YourOrg.BlogContent.csproj`.
   If your library has another name than `YourOrg.BlogContent`, change it in `Content.cs`.
3. Put the Coho values in user secrets, which live outside the project, so they are never
   committed: `dotnet user-secrets init`, then `dotnet user-secrets set` for `COHO_URL`,
   `COHO_ACCOUNT`, `COHO_PROJECT`, `COHO_REF`, `COHO_LOCALE` and a project token as
   `COHO_PREVIEW_TOKEN`. Copying `BlogTest`'s is enough:
   `dotnet user-secrets list --json --project ../BlogTest | sed '/^\/\//d' | dotnet user-secrets set`.
4. `dotnet watch`, open http://localhost:5080, then replace each `Repeater:` comment with
   a `@foreach` over its list. The tutorial has the code for each.

The site builds the library from its project, and `dotnet watch` watches both, so a
regenerated library reaches the running site with nothing to install. When the library is
published, the project reference becomes `dotnet add package YourOrg.BlogContent`.
