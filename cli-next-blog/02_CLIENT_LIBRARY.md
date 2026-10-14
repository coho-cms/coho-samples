# 2. Create the client library

A site reads this content through a client library: a TypeScript package with an
interface for each content type, generated from this project's types. This page creates
the library from the `v1.0.1` release cut in [Set up the content model](01_CONTENT.md),
generates its typed API, and checks that it can read the content on `qa`.

You need the delivery key from step 12 of [Set up the content model](01_CONTENT.md).
Run the first command from inside the `cli-next-blog` folder.

## 1. Create the library

The library tooling is in testing, so its releases are alphas on npm, reached with
`@alpha`. `coho status` shows the URL, account and project the library needs. Create the
library beside this repository, replacing the three placeholders:

```bash
npm create coho@alpha ../../blog-content -- --name @your-org/blog-content --url <url> --account <account-id> --project <project-id> --ref v1.0.1
```

This copies the library template, sets it up for this project, and installs it. Move into it:

```bash
cd ../../blog-content
```

## 2. Create a project token

The library reads its types with a project token. Create one that can only read, and copy
it somewhere safe; it is shown once:

```bash
coho token create --role viewer --label "blog-content library"
```

## 3. Fill in the settings

Copy the example settings:

```bash
cp .env.example .env
```

Then fill in `.env`. It is in `.gitignore`, so it stays out of commits:

- `COHO_TOKEN`: the project token from step 2.
- `COHO_DELIVERY_URL`: `https://delivery-dev.coho-cms.dev`.
- `COHO_DELIVERY_KEY`: the delivery key you created for `qa`.
- `COHO_DELIVERY_REF`: `qa`, the environment that key reads.

## 4. Generate the typed API

Fetch the types from `v1.0.1`, and generate the library's code from them:

```bash
npm run pull
```

```bash
npm run generate
```

## 5. List the content

List the content the library can read:

```bash
npm run catalog
```

You should see every content type, and how many entries each has on `qa`:

```
Content on qa:

  blogPost     Blog post         2
  tag          Tag               3
  teamMember   Team member       2

  7 entries in 3 types
```

The counting is the library's `catalog` function, in `src/catalog.ts`, and a site uses the
typed reads beside it the same way, such as `coho.blogPost.list({ order: '-publishedAt' })`.
The library's README covers releasing it and using it from a site.

## If something goes wrong

- **`npm run pull` fails with `401` or `403`:** check `COHO_TOKEN` in `.env`. It must be a
  project token for this project.
- **`npm run pull` fails with `404`:** the Coho server predates the type model. It needs a
  build that serves `…/refs/{ref}/type-model`.
- **`npm run catalog` fails:** a key made for `qa` reads only `qa`, so set
  `COHO_DELIVERY_REF=qa`. `PROJECT_NOT_FOUND` means the key is for another project, or
  `project` in `coho.config.json` is wrong.

Next: [Build the Next.js blog](03_APPLICATION.md).
