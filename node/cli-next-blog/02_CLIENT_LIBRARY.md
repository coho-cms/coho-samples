# 2. Create the client library

Now we'll build a client library to have more convenient access to the content from
our own codebase. This process creates a standalone node package that gets its configuration
through environment variables. You will want to set this up as its own project that can be 
updated as your content model changes, deployed to a node package repository, and distributed 
as a dependency in all of the projects which need access to your content. 

This step in the tutorial will create the new project, generate its types from `dev`, and run
some tests to make sure it can access your coho content. `dev` follows the head of the trunk,
which is where your development work is most likely to be. Then you'll write a small program
of your own that uses the library, and point it at `dev` without changing its code.

After that, we'll show how you can create your own content branch, point your local environment to
that branch, and when you're happy with the content changes, merge that into the version branch.

Everything on this page uses two credentials: your `coho login`, for the CLI, and project
tokens, for the library and your own code. Releasing content to `qa` and reading it with a
delivery key, the way a published website does, is a later tutorial.

## 1. Create a project token

The library reads its types with a project token. Create one that can only read, and copy
it somewhere safe; it is shown once:

```bash
coho token create --role viewer --label "blog-content library"
```

A token belongs to one project, so it is all the library needs to know which project it
is for: there are no account or project IDs to copy.

## 2. Create the library

The library tooling is in testing, so its releases are alphas on npm, reached with
`@alpha`. Create the library in a folder of its own, outside this repository, such as
`~/workarea/blog-content`. `npm create coho` makes the folder, so it must not exist yet,
or be empty:

```bash
mkdir ~/workarea/blog-content
cd ~/workarea/blog-content
npm create coho@alpha . -- --name @your-org/blog-content \
    --url https://api-dev.coho-cms.dev --ref dev
```

It asks for the project token from step 1. Paste it; it is not shown as you do. Coho says
which account and project the token is for, and the library is set up for them:

```
Created @your-org/blog-content in …/workarea/blog-content, from the bundled template, on @coho-cms 0.1.0-alpha.4.
It reads blog-sample, in <your account>, with the token in .env.
```

## 3. Generate the typed API

Fetch the types from `dev`, and generate the library's code from them:

```bash
npm run pull
```

```bash
npm run generate
```

`generate` warns that the types came from a branch, whose types can change. That is
expected while you develop: the library's types follow `dev`, so they change when `dev`
does. It is a reminder for later. When you publish the library for other projects to
install, generate it from a tag, so a published version always means the same types.

## 4. List the content

List the content the library can read on `dev`:

```bash
npm run catalog -- --preview
```

You should see every content type, and how many entries each has:

```
Unreleased content on dev:

  blogPost     Blog post         2
  tag          Tag               3
  teamMember   Team member       2

  7 entries in 3 types
```

`--preview` reads live through Coho, with the project token in `.env`. The counting is in
`scripts/`, a development tool, not part of the published library. A site uses the same
typed reads, such as `coho.blogPost.list({ order: '-publishedAt' })`.

## 5. Write your own code

A site or service uses the library the way any program does: it imports it, and hands it
its environment. The library reads no files. Whatever runs the program puts the variables
in the environment: on your machine, a `.env.local` file; on a host, the platform's
settings and secrets. So the same code reads `dev` on your machine and a branch in a
preview deployment.

Try it with a small program beside the library. First build the library, so a program can
import it:

```bash
npm run build
```

Create the program's folder, and install the library into it, with `@coho-cms/delivery`,
the package the library is built on:

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
from whichever ref it is given:

```ts
import { configFromEnv } from '@coho-cms/delivery';
import { createCoho, isResolved } from '@your-org/blog-content';

// What to read, and with which credential: the environment decides, not the code.
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

## 6. Say where dev is

The program needs a credential to read `dev`. Create a project token for it, rather than
reusing the library's `COHO_TOKEN`. They could be the same token, but the library's stays
with the library, while this one goes wherever the program runs, so each can be revoked
without breaking the other:

```bash
coho token create --role viewer --label "blog-try preview"
```

Create `.env.local`, saying where `dev`'s content is and holding that token. Replace the
placeholders with the `account` and `project` that `npm create coho` wrote into the
library's `coho.config.json`, and with the token:

```
# dev: the head of the trunk, read live through Coho.
COHO_URL=https://api-dev.coho-cms.dev
COHO_ACCOUNT=<account-id>
COHO_PROJECT=<project-id>
COHO_REF=dev
COHO_LOCALE=en-US
COHO_PREVIEW_TOKEN=<preview-token>
```

`COHO_URL` is Coho's own address, the one the CLI uses. `COHO_LOCALE` picks the
translation of localized fields, such as the titles.

The token is a secret, so `.env.local` must never be committed. Add it to `.gitignore`
now, before the folder ever becomes a repository:

```bash
echo ".env.local" >> .gitignore
```

## 7. Run it against dev

Run the program. `--env-file` makes Node load the file into the environment before the
program starts, as a host does:

```bash
node --env-file=.env.local posts.ts
```

```
Blog posts on dev:

  2026-10-01  What the drainage survey found under Elm Street, by Tom Okafor
              The corrected summary.

  2026-09-15  Why every roundabout needs a second opinion, by Priya Shah
              A roundabout that looks right on paper can still jam at rush hour. Here is how we check.
```

## 8. Work on a content branch

A branch is your own copy of the content, where you can change things without touching
`dev`. Create one from the trunk:

```bash
coho branch create feature/spring-update --from v0.0.x
```

Change a post on the branch. `--ref` says which branch a command works on:

```bash
coho --ref feature/spring-update entry put @elm-street-drainage --set 'summary={"en-US":"Rewritten on a branch."}'
```

Point the program at the branch. A variable set on the command line wins over the one in
`.env.local`, so nothing else changes:

```bash
COHO_REF=feature/spring-update node --env-file=.env.local posts.ts
```

The Elm Street post now shows `Rewritten on a branch.` Run the command from step 7 again:
`dev` still shows `The corrected summary.` In a real project, a preview deployment of a
feature sets `COHO_REF` to its branch the same way.

If a branch changes a content type, generate the library's types from it too. In
`blog-content`:

```bash
npm run pull -- --ref feature/spring-update && npm run generate
```

## 9. Merge the branch

When you are happy with the change, see what merging it into the trunk would do:

```bash
coho diff v0.0.x feature/spring-update
```

Then merge it. `--reviewed` checks that nothing changed since that diff:

```bash
coho merge feature/spring-update --into v0.0.x -m "Rewrite the Elm Street summary" --reviewed
```

Run the command from step 7 again. `dev` follows the trunk, so it now shows
`Rewritten on a branch.` too.

Creating the branch made it the CLI's current ref. Now that it is merged, switch back to
the trunk, so the commands that follow work there again:

```bash
coho ref switch v0.0.x
```

`coho status` shows `v0.0.x` as the ref again.

## If something goes wrong

- **`npm create coho` says `Coho refused the token`:** with `UNAUTHENTICATED`, the token is
  mistyped, revoked or expired, or was created before Coho could look tokens up by
  themselves: create another. With `404`, check `--url`: it is Coho's own address. Nothing
  is created when the token is refused, so run it again as it was.
- **`npm run pull` fails with `401` or `403`:** check `COHO_TOKEN` in `.env`. It must be a
  project token for this project.
- **`npm run pull` fails with `404`:** the Coho server predates the type model. It needs a
  build that serves `…/refs/{ref}/type-model`.
- **`npm run catalog -- --preview` fails with `PROJECT_NOT_FOUND`:** `COHO_TOKEN` is for
  another project, or `account` or `project` in `coho.config.json` is wrong. With
  `UNAUTHENTICATED`, the token has expired or been revoked: create another.
- **`posts.ts` fails with `Cannot find module …/blog-content/dist/index.js`:** the library
  is not built. Run `npm run build` in `blog-content`.
- **`posts.ts` fails with `COHO_DELIVERY_URL is needed to read released content`:** no
  preview token reached the environment, so the library took the run for a release. Check
  `COHO_PREVIEW_TOKEN` in `.env.local`, and that the command has `--env-file=.env.local`.
- **`posts.ts` fails with `UNAUTHENTICATED` or `PROJECT_NOT_FOUND`:** the token is wrong,
  expired or revoked, or for another project. Also check `COHO_ACCOUNT` and `COHO_PROJECT`
  in `.env.local`.
- **`node` says `.env.local: not found`:** run the command from inside `blog-try`, where
  the file is.
- **`posts.ts` fails with `REF_NOT_FOUND` on the branch:** check the branch name in
  `COHO_REF` against `coho branch list`.

Next: [Build the Next.js blog](03_APPLICATION.md).
