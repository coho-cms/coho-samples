# Setting up an ASP.NET Core blog with the CLI

This sample walks through setting up a simple blog content model and wiring it into an
ASP.NET Core Razor Pages site. It starts with the content model: the content types, and a
few entries to read. Next it creates a client library with a strongly typed API, generated
from those types. Then it wires that library into Razor pages on the blog. It gives the
posts images and files to download, and last, a list of citations stored inside each post.

1. [Set up the content model](01_CONTENT.md)
2. [Create the client library](02_CLIENT_LIBRARY.md)
3. [Build the Razor Pages blog](03_APPLICATION.md)
4. [Images and downloads](04_IMAGES_AND_ASSETS.md)
5. [Reference repeaters and inline repeaters](05_REFERENCE_AND_INLINE_REPEATERS.md)

The model shows the main things Coho does: content types, a closed list of choices,
localized text, markdown, references between entries, assets, and component types for
the items of a repeater. It is the same model as the
[Node.js sample](../../node/cli-next-blog/README.md)'s, so one Coho project serves both.

```
cli-razor-blog/
└── entries/
    ├── tags/           three tags
    ├── team-members/   two authors
    ├── blog-posts/     two posts, linked to the authors and tags
    └── citations/      two citations for each post, from page 5
```

## Before you start

You need:

- the `coho` CLI, and a Coho account. Every command in this sample uses the default
  profile, so none of them needs a `-p` flag.
- the [.NET 10 SDK](https://dotnet.microsoft.com/download). Check with `dotnet --version`.

Every command on page 1 runs from inside this folder. Start by moving into it:

```bash
git clone https://github.com/coho-cms/coho-samples.git
cd coho-samples/dotnet/cli-razor-blog
```

Sign in to the default profile. This opens a browser:

```bash
coho login
```

If `coho login` reports that there is no profile yet, set one up with `coho configure`,
then run `coho login` again.

Check who you are:

```bash
coho whoami
```

This lists the accounts you belong to. If you belong to more than one, add
`--account <name-or-id>` to the commands that follow, or set `COHO_ACCOUNT`.

Next: [Set up the content model](01_CONTENT.md).
