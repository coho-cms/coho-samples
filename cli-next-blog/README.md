# Setting up a Next.js blog with the CLI

This sample walks through setting up a simple blog content model and wiring it into a
Next.js app. It starts with the content model: the content types, and a few entries to read.
Next it creates a client library with a strongly typed API, generated from those types.
Last, it wires that library into React templates on a Next.js blog.

1. [Set up the content model](01_CONTENT.md)
2. [Create the client library](02_CLIENT_LIBRARY.md)
3. [Build the Next.js blog](03_APPLICATION.md)

The model shows the main things Coho does: content types, a closed list of choices,
localized text, markdown, and references between entries.

```
cli-next-blog/
├── types/          content type definitions (tag, teamMember, blogPost)
└── entries/
    ├── tags/           three tags
    ├── team-members/   two authors
    └── blog-posts/     two posts, linked to the authors and tags
```

## Before you start

You need the `coho` CLI installed, and an account. Every command in this sample uses the
default profile, so none of them needs a `-p` flag.

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

When you are signed in, start with [Set up the content model](01_CONTENT.md).
