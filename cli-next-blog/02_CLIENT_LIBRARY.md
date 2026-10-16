# 2. Create the client library

A site reads this content through a client library: a TypeScript package with an
interface for each content type, generated from this project's types. This page creates
the library from the `v1.0.1` release cut in [Set up the content model](01_CONTENT.md),
generates its typed API, and checks that it can read the content on `qa` and `dev`. Last,
you write a small program of your own that uses the library, and point it at either
environment without changing its code.

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
- `COHO_REF`: `qa`, the environment that key reads.

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

## 6. List what is not released yet

`qa` holds a release. `dev` follows the trunk, so it holds whatever was saved last,
released or not. Delivery serves only releases, so the library reads `dev` live through
Coho instead, with the project token from step 2 rather than the delivery key:

```bash
npm run catalog -- --preview
```

```
Unreleased content on dev:

  blogPost     Blog post         2
  tag          Tag               3
  teamMember   Team member       2

  7 entries in 3 types
```

The counts match `qa`, because nothing has been saved on the trunk since `v1.0.1`. Create
or change an entry and run it again: `dev` shows it at once, and `qa` only once it is
released and promoted. A site previews the same way, with a project token of its own in
place of its delivery key; the library's README shows how.

## 7. Write your own code

A site or service uses the library the way any program does: it imports it, and hands it
its environment. The library reads no files. Whatever runs the program puts the variables
in the environment: a `.env.dev` or `.env.qa` file for where things are, and the platform
for secrets. So the same code reads `qa` in one deployment and `dev` in another.

Try it with a small program beside the library. First build the library, so a program can
import it:

```bash
npm run build
```

Create the program's folder, and install the library into it, with the delivery package
the library is built on:

```bash
mkdir ../blog-try && cd ../blog-try
```

```bash
npm init -y && npm pkg set type=module
```

```bash
npm install ../blog-content @coho-cms/delivery@alpha
```

Save this as `posts.ts`. It lists the blog posts, newest first, with each one's author,
from whichever environment it is given:

```ts
import { configFromEnv, createCoho, isResolved } from '@your-org/blog-content';

// Released content or a preview, and which ref: the environment decides, not the code.
const coho = createCoho(configFromEnv(process.env));

// depth: 1 brings each post's author, tags and related posts in the same request.
const posts = await coho.blogPost.list({ order: '-publishedAt', depth: 1 });

console.log(`Blog posts on ${process.env.COHO_REF}:\n`);
for (const post of posts.items) {
  const author = post.author !== undefined && isResolved(post.author) ? post.author.fullName : 'no author';
  console.log(`  ${post.publishedAt.slice(0, 10)}  ${post.title}, by ${author}`);
  console.log(`              ${post.summary}\n`);
}
```

The types come from the library, so a misspelled field such as `post.autor` is an error in
your editor rather than an `undefined` at runtime.

## 8. Say where each environment is

Each environment gets a file of its own, saying where its content is. Neither holds a
secret, so a real project commits them. Create `.env.dev`, replacing the placeholders with
the account and project IDs from `coho status`:

```
# dev: unreleased content, read live through Coho.
COHO_URL=https://api-dev.coho-cms.dev
COHO_ACCOUNT=<account-id>
COHO_PROJECT=<project-id>
COHO_REF=dev
COHO_LOCALE=en-US
```

And `.env.qa`:

```
# qa: a release, read from delivery.
COHO_DELIVERY_URL=https://delivery-dev.coho-cms.dev
COHO_PROJECT=<project-id>
COHO_REF=qa
COHO_LOCALE=en-US
```

`dev` needs Coho's URL and the account, because it is read through Coho. `qa` needs only
delivery's URL. `COHO_LOCALE` picks the translation of localized fields, such as the titles.

## 9. Run it against dev and qa

Each environment also needs a credential, and that is never written to a file: where the
program runs, the platform injects it into the environment as a secret. Here, you set it
on the command line, for one run.

`dev` reads with a project token. Create one for this program, rather than reusing the
library's `COHO_TOKEN`, which only pulls types and is never deployed:

```bash
coho token create --role viewer --label "blog-try preview"
```

Run the program against `dev`. `--env-file` makes Node load the file into the environment
before the program starts, as a host does. A variable already set, such as the token, is
kept:

```bash
COHO_PREVIEW_TOKEN=<preview-token> node --env-file=.env.dev posts.ts
```

```
Blog posts on dev:

  2026-10-01  What the drainage survey found under Elm Street, by Tom Okafor
              The corrected summary.

  2026-09-15  Why every roundabout needs a second opinion, by Priya Shah
              A roundabout that looks right on paper can still jam at rush hour. Here is how we check.
```

Then against `qa`, with the delivery key from step 12 of
[Set up the content model](01_CONTENT.md):

```bash
COHO_DELIVERY_KEY=<delivery-key> node --env-file=.env.qa posts.ts
```

It lists the same posts, under `Blog posts on qa`, because `v1.0.1` holds everything saved
so far. The code did not change: the environment chose a preview through Coho with a
token, or a release from delivery with a key.

## 10. See dev and qa differ

Change a post on the trunk:

```bash
coho entry put <elm-street-post-id> --set 'summary={"en-US":"Changed after v1.0.1."}'
```

Run both commands from step 9 again. `dev` shows the new summary at once. `qa` still shows
`The corrected summary.`, and will until a new tag is cut and promoted to it, as in step 11
of [Set up the content model](01_CONTENT.md).

## If something goes wrong

- **`npm run pull` fails with `401` or `403`:** check `COHO_TOKEN` in `.env`. It must be a
  project token for this project.
- **`npm run pull` fails with `404`:** the Coho server predates the type model. It needs a
  build that serves `…/refs/{ref}/type-model`.
- **`npm run catalog` fails:** a key made for `qa` reads only `qa`, so set
  `COHO_REF=qa`. `PROJECT_NOT_FOUND` means the key is for another project, or
  `project` in `coho.config.json` is wrong.
- **`npm run catalog -- --preview` fails with `PROJECT_NOT_FOUND`:** `COHO_TOKEN` is for
  another project, or `account` or `project` in `coho.config.json` is wrong. With
  `UNAUTHENTICATED`, the token has expired or been revoked: create another.
- **`posts.ts` fails with `Cannot find module …/blog-content/dist/index.js`:** the library
  is not built. Run `npm run build` in `blog-content`.
- **`posts.ts` fails with `COHO_DELIVERY_URL is needed to read released content` on `dev`:**
  no preview token reached the environment, so the library took the run for a release.
  `dev` reads with `COHO_PREVIEW_TOKEN=` on the command line, not the delivery key.
- **`posts.ts` fails with `set COHO_PREVIEW_TOKEN … or COHO_DELIVERY_KEY …, not both`:** one
  of them is exported in your shell, so both reached the program. A deployment holds only
  its own. Run `unset COHO_PREVIEW_TOKEN COHO_DELIVERY_KEY`, then try again.
- **`posts.ts` fails with `UNAUTHENTICATED` on `dev`, or `PROJECT_NOT_FOUND` on `qa`:** the
  credential is wrong, expired or revoked, or for another project. On `dev`, also check
  `COHO_ACCOUNT` and `COHO_PROJECT` in `.env.dev`; on `qa`, `COHO_PROJECT` in `.env.qa`.

Next: [Build the Next.js blog](03_APPLICATION.md).
