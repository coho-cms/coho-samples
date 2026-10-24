# Setting up a Spring Boot blog service with the CLI

This sample walks through setting up a simple blog content model and serving it from a Spring
Boot web service. It starts with the content model: the content types, and a few entries to
read. Next it creates a client library with a strongly typed API, generated from those types
as Java classes. Then it wires that library into a Spring Boot service that answers with JSON.
It gives the posts images and files to download, and a list of citations stored inside each
post. Last, it shares fields two ways: an SEO trait any type can take, and a photo gallery
that is a kind of post.

1. [Set up the content model](01_CONTENT.md)
2. [Create the client library](02_CLIENT_LIBRARY.md)
3. [Build the Spring Boot service](03_APPLICATION.md)
4. [Images and downloads](04_IMAGES_AND_ASSETS.md)
5. [Reference repeaters and inline repeaters](05_REFERENCE_AND_INLINE_REPEATERS.md)
6. [Traits and inheritance](06_TRAITS_AND_INHERITANCE.md)

The service has no pages of its own. It answers with JSON, for a front end, an app or another
service to show, and documents every route at `/swagger-ui.html`, where you can try each one.

The model shows the main things Coho does: content types, a closed list of choices,
localized text, markdown, references between entries, assets, component types for the
items of a repeater, a trait, and a type that extends another. It is the same model as the
other samples', such as the [Node.js sample](../../node/cli-next-blog/README.md)'s, so one
Coho project serves them all.

```
cli-spring-blog/
├── types/                the content types, as JSON
└── entries/
    ├── tags/             three tags
    ├── team-members/     two authors
    ├── blog-posts/       two posts, linked to the authors and tags
    ├── citations/        two citations for each post, from page 5
    └── photo-galleries/  a gallery, a kind of post, from page 6
```

## Before you start

You need:

- the `coho` CLI and a Coho account. [Installing the `coho` CLI](../../INSTALLING.md) sets it up, once for every
  sample. Every command in this sample uses the default profile, so none of them needs
  a `-p` flag.
- a JDK, 21 or later. Check with `java -version`. You don't need Gradle: each project
  brings its own Gradle wrapper, `./gradlew`.
- `git`, to copy the library template.

Every command on page 1 runs from inside this folder. Start by moving into it:

```bash
git clone https://github.com/coho-cms/coho-samples.git
cd coho-samples/java/cli-spring-blog
```

Sign in to the default profile. This opens a browser:

```bash
coho login
```

If `coho login` reports that there is no profile yet, run the `coho configure` command in
[Installing the `coho` CLI](../../INSTALLING.md#2-point-it-at-coho), then `coho login` again.

Check who you are:

```bash
coho whoami
```

This lists the accounts you belong to. If you belong to more than one, add
`--account <name-or-id>` to the commands that follow, or set `COHO_ACCOUNT`.

Next: [Set up the content model](01_CONTENT.md).
