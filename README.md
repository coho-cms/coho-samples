# Coho samples

Welcome! This is the place to start with [Coho](https://github.com/coho-cms): tutorials,
best practices, and getting-started projects that show how to bring Coho content into the
languages and frameworks you already use.

Coho is managed content infrastructure, branch-native: your content and your content
model are versioned together. You change both on a branch, review the diff, merge it, cut
a release, and promote that release through environments such as `dev`, `qa` and `prod`.
These samples show what that looks like from the code that reads your content.

## Start here

New to Coho? Start with **[Setting up a Next.js blog with the CLI](node/cli-next-blog/README.md)**.
In six short steps it goes from nothing to a working site:

1. **[Set up the content model](node/cli-next-blog/01_CONTENT.md)**: content types, a few
   entries, localized text, markdown, and references between entries.
2. **[Create the client library](node/cli-next-blog/02_CLIENT_LIBRARY.md)**: a TypeScript
   package with a typed API, generated from those content types.
3. **[Build the Next.js blog](node/cli-next-blog/03_APPLICATION.md)**: React pages that read
   the content through that library.
4. **[Images and downloads](node/cli-next-blog/04_IMAGES_AND_ASSETS.md)**: files uploaded as
   assets, linked from the posts, and shown as resized images and download links.
5. **[Reference repeaters and inline repeaters](node/cli-next-blog/05_REFERENCE_AND_INLINE_REPEATERS.md)**:
   a list of entries each post links to, beside a list of citations stored in the post.
6. **[Traits and inheritance](node/cli-next-blog/06_TRAITS_AND_INHERITANCE.md)**: the
   posts' SEO fields moved into a trait any type can take, and a photo gallery that is a
   kind of post.

Working in .NET? **[Setting up an ASP.NET Core blog with the CLI](dotnet/cli-razor-blog/README.md)**
takes the same six steps, with a C# library and a Razor Pages site.

## Samples by language

| Language | Sample | What it shows |
|---|---|---|
| **Node.js and TypeScript** | [cli-next-blog](node/cli-next-blog/README.md) | A content model built with the CLI, a generated typed client library, and a Next.js blog |
| **.NET** | [cli-razor-blog](dotnet/cli-razor-blog/README.md) | The same content model, a generated typed C# library, and an ASP.NET Core Razor Pages blog |
| **Python** | 🔜 Coming | |

Each sample is self-contained: its own folder, its own README, and steps numbered in the
order you take them. Commands run from inside the sample's folder, and each README says
what you need before you start.

## What you'll pick up along the way

- **Model content as code.** Content types are JSON files you keep in your repository and
  review like any other change.
- **Read content with types.** A client library generated from your content model catches
  a removed field at build time, not in production.
- **Preview before you release.** Read `dev` or a branch with a project token while you
  work, and released content with a delivery key in production, from the same code.
- **Keep credentials where they belong.** Each sample shows which token goes where, and
  keeps every secret on the server.

## Before you start

You need the [`coho` CLI](https://github.com/coho-cms/coho-cli) and a Coho account. Each
sample's README walks through signing in. Then clone this repository:

```bash
git clone https://github.com/coho-cms/coho-samples.git
```

## The tools these samples use

| Repository | What it is |
|---|---|
| [coho-cli](https://github.com/coho-cms/coho-cli) | The `coho` command line: sign in, create projects, and manage types, entries, branches and releases |
| [coho-delivery-sdk-typescript](https://github.com/coho-cms/coho-delivery-sdk-typescript) | The TypeScript delivery client, the code generator, and `npm create coho` |
| [coho-template-typescript](https://github.com/coho-cms/coho-template-typescript) | The starting point for a TypeScript content library |
| [coho-react](https://github.com/coho-cms/coho-react) | React components for images resized at the edge, and links to download assets |
| [coho-delivery-sdk-dotnet](https://github.com/coho-cms/coho-delivery-sdk-dotnet) | The .NET delivery client, the code generator, and `dotnet new coho-library` |
| [coho-template-dotnet](https://github.com/coho-cms/coho-template-dotnet) | The starting point for a .NET content library |
| [coho-razor](https://github.com/coho-cms/coho-razor) | Razor tag helpers and Blazor components for images and downloads |
| [coho-management-sdk-python](https://github.com/coho-cms/coho-management-sdk-python) | The Python management SDK: accounts, projects, branches, content, releases and delivery keys |

## Contributing

Found a step that didn't work, or have a sample you'd like to see? Open an issue. Samples
for more languages and frameworks are on the way, and requests help decide which comes
next.

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
