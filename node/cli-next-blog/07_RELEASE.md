# 7. Release the blog

So far the site has read `dev`: the newest saved content on the trunk, read live through
Coho with a project token. That is right while you build, since every change shows at
once. A published site needs the opposite: content that changes only when you decide to
release it.

This page releases the blog. You tag the trunk, which fixes its content as a release, and
promote the tag to `prod`. You create a delivery key that can read `prod` and nothing
else, and put it in a `.env.prod` file in the site. Then you build the site for
production, with its TypeScript compiled and its pages rendered ahead of time, and run it
on your own machine, the way a host would run it.

```
v0.0.x  the trunk ──── dev    live: the newest saved content, read through Coho
   │                          with a project token
   └── v0.0.1  a tag ── prod  fixed: the content as it was when tagged, read from
                              Coho's delivery service with a delivery key
```

You need the site from [Build the Next.js blog](03_APPLICATION.md), with the posts,
images, citations and gallery of pages 4 to 6, and Node.js 20.12 or later. Release
commands run from anywhere; the `coho` ones use the project and ref that `coho status`
shows, which should be `blog-sample` and `v0.0.x`.

## 1. Tag a release

A tag is a fixed point on a version branch. The trunk, `v0.0.x`, keeps changing as you
write to it, and `dev` with it. A tag never changes: it holds the content as it was when
you cut it. Cut the first one:

```bash
coho tag create v0.0.1 --branch v0.0.x --validate -m "First release: posts, authors, tags and a gallery"
```

```
tag     v0.0.1
branch  v0.0.x
at      214
```

`at` is the point on the trunk the tag holds, as a sequence number, not a time. Yours
differs.

`--validate` checks every entry at that point against its type first, and tags nothing if
one fails. Every write was checked when it was made, but a type changed later does not
check the entries it already has, so a release is the place to check them all. `-m` is the
release notes, which `coho tag list` shows beside each tag.

A tag cannot be changed or deleted, since it is the record of what was released. The name
is yours to choose: `v0.0.1`, `2026.11.1` and `launch` are all fine.

## 2. Promote it to prod

Tagging releases nothing yet. What a site reads is an **environment**, a name that points
at a tag, and `prod` points at nothing until you promote one to it:

```bash
coho promote prod v0.0.1 -m "First release of the blog"
```

The first time a tag is promoted, Coho builds its snapshot, the copy of its content that
delivery serves. The CLI shows `snapshot not ready; waiting…` while it builds, then:

```
environment  prod
tier         prod
target       v0.0.1
previous     -
warning: SKIPPED_TIER: 'v0.0.1' has not been promoted to any 'qa' or 'stage' environment
```

The warning is expected. The project has four environments in order, `dev`, `qa`, `stage`
and `prod`, and a team would promote a tag to `qa` and `stage` to check it before `prod`.
Each needs a permission of its own, so whoever may tag a release need not be able to
publish it. Skipping them is allowed, so a hotfix can go straight out, and the
promotion is kept in `prod`'s history with its reason, the `-m`.

`coho env list` shows where each environment points: `dev` at the trunk, `prod` at
`v0.0.1`.

## 3. Create a delivery key for prod

The site has read `dev` with a project token, through Coho itself. A published site reads
from Coho's **delivery service** instead: built for visitors' traffic, serving only
released content, and reading it with a **delivery key**. A delivery key cannot read `dev`,
a branch or anything unreleased, so a leaked one gives away only what the site already
shows.

Create one that can read `prod` and nothing else, and that expires in a year:

```bash
coho key create --label "blog-site prod" --ref prod --expires-in-days 365
```

```
id  01a2…
label  blog-site prod
refs  prod
expires  2027-11-07T09:00:00Z
Delivery key
coho_dk_AbCdEf…
This delivery key is shown once and cannot be retrieved again.
```

The key is the line under `Delivery key`, starting `coho_dk_`. As with the project token on
page 1, Coho keeps only a hash of it, so copy it now. Only the project's owner can create
delivery keys, and you are the owner of the project you created.

Read the posts with it, as page 1 did with the token. Put the project ID and the key in
shell variables first; `coho status` shows the ID:

```bash
PROJECT=<project-id>
KEY=<the coho_dk_ key>
```

```bash
curl -s -H "Authorization: Bearer $KEY" \
    "https://delivery.coho-cms.com/v1/projects/$PROJECT/prod/entries?type=blogPost&depth=1"
```

The answer has the same shape as the preview's on page 1, with `roots` and `entries`. The
address has no account in it, and names `prod` where the preview named `dev`.

## 4. Create `.env.prod`

The site reads its settings from the environment, so the same code reads `dev` on your
machine and `prod` in production. Page 3 put `dev`'s settings in `.env.local`. Put
`prod`'s in a file of their own, `.env.prod`, in the site's folder:

```bash
cd ~/workarea/blog-site
```

Create `.env.prod`, replacing `<project-id>` and `<delivery-key>` with your values:

```
# prod: released content, read from Coho's delivery service with a delivery key.
COHO_DELIVERY_URL=https://delivery.coho-cms.com
COHO_PROJECT=<project-id>
COHO_REF=prod
COHO_LOCALE=en-US
COHO_DELIVERY_KEY=<delivery-key>

# Next.js reads .env.local in a production build too, and its preview token would
# make the site read dev. A variable that is set, even to nothing, is never replaced
# by a file, and nothing counts as unset, so this keeps the token out.
COHO_PREVIEW_TOKEN=
```

`COHO_DELIVERY_URL` and `COHO_DELIVERY_KEY` take the place of `.env.local`'s `COHO_URL`
and `COHO_PREVIEW_TOKEN`. There is no `COHO_ACCOUNT`, since a delivery address names only
the project. The site's code does not change: `lib/coho.ts` passes the environment to
`configFromEnv`, which reads released content when it finds a delivery key.

The key is a secret, so `.env.prod` must never be committed. The starter's `.gitignore`
leaves it out. If you copied the starter before it did, add the line:

```bash
echo ".env.prod" >> .gitignore
```

Next.js would read a file named `.env.production` on its own, in every production build.
`.env.prod` is named for the environment it reads, and Next.js never reads it by itself:
`npm run build` and `npm run dev` go on reading `dev`, and a build reads `prod` only when
you ask, with the scripts in the next step.

## 5. Add the release scripts

Two scripts build and run the site with `.env.prod`. The starter has them. If you copied
it before it did, add them to `package.json`, under `scripts`:

```json
"build:prod": "node scripts/with-env.mjs .env.prod build",
"start:prod": "node scripts/with-env.mjs .env.prod start --port 3001"
```

and create `scripts/with-env.mjs`, which loads the file and then runs Next.js:

```js
import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';

const [file, ...args] = process.argv.slice(2);
process.loadEnvFile(file);

const next = createRequire(import.meta.url).resolve('next/dist/bin/next');
const { status } = spawnSync(process.execPath, [next, ...args], { stdio: 'inherit' });
process.exit(status ?? 1);
```

A variable already set in your shell wins over the file, as it does with Next.js's own
files. `node --env-file=.env.prod` would seem simpler, but Next.js passes it on to its
build workers through `NODE_OPTIONS`, where Node does not allow it, and the build stops.

## 6. Build the release

```bash
npm run build:prod
```

```
▲ Next.js 16.4.2 (Turbopack)
- Environments: .env.local
  Creating an optimized production build ...
✓ Compiled successfully in 188ms
  Running TypeScript ...
  Finished TypeScript in 561ms ...
  Collecting page data using 5 workers ...
✓ Generating static pages using 5 workers (6/6) in 678ms
  Finalizing page optimization ...

Route (app)                             Revalidate  Expire
┌ ○ /                                           1m      1y
├ ○ /_not-found                                 1m      1y
└   /posts/[slug]
  ├ ● /posts/roundabout-second-opinion          1m      1y
  ├ ● /posts/elm-street-drainage                1m      1y
  └ ● /posts/civil-works-from-above             1m      1y
```

The build compiles the TypeScript and checks its types, as on page 3, so a field the
library does not have fails here, not on the live site. Then it reads every post from
`prod` and renders each page to HTML ahead of time, into `.next`. `Revalidate 1m` is the
site's `revalidate`, from `app/layout.tsx`: once running, a page is rendered again with
fresh content at most once a minute.

`Environments: .env.local` names only the files Next.js read itself. It read `.env.local`
too, but every variable that would have mattered was already set from `.env.prod`.

## 7. Run it

```bash
npm run start:prod
```

```
▲ Next.js 16.4.2
- Local:         http://localhost:3001
✓ Ready in 76ms
```

Open http://localhost:3001. It is the same blog, read from `prod`. `next start` serves the
build in `.next` and compiles nothing, so it is ready at once and each page is already
rendered: this is what a host runs. It uses port 3001, so `npm run dev` can run beside
it on 3000, and you can compare the two. Stop it with Ctrl-C.

## 8. Release a change

Leave both running: `npm run start:prod` in one terminal and `npm run dev` in another.
Change the Elm Street post's summary on the trunk:

```bash
coho entry put @elm-street-drainage --set 'summary={"en-US":"Released in v0.0.2."}'
```

http://localhost:3000 shows the new summary on its next request, because `dev` follows the
trunk. http://localhost:3001 does not: `prod` still points at `v0.0.1`, which never
changes. Release it:

```bash
coho tag create v0.0.2 --branch v0.0.x --validate -m "Rewrite the Elm Street summary"
```

```bash
coho promote prod v0.0.2 --expected v0.0.1 -m "Elm Street summary"
```

`--expected v0.0.1` promotes only if `prod` still points at `v0.0.1`, so a release
someone else made in the meantime is never overwritten by accident.

Delivery serves the new tag within a few seconds, and the site picks it up within a minute,
with no new build. A page older than a minute is rendered again in the background when it
is next requested, so reload http://localhost:3001 once after a minute, then again to see
the new summary.

A new build is needed when the site's code changes, and when the content types do: a
release that adds a field needs the library regenerated with it, as on page 4, and the site
built again to show it.

## 9. Roll back

`v0.0.2` turns out to be a mistake. Point `prod` back at what it pointed at before:

```bash
coho rollback prod -m "Back to v0.0.1"
```

```
prod: v0.0.2 → v0.0.1
Roll back? [y/N]: y
environment  prod
tier         prod
target       v0.0.1
previous     v0.0.2
```

Within a minute the site shows the old summary again, still without a new build. Nothing
is lost: `v0.0.2` is still a tag, and `coho promote prod v0.0.2` would release it again.
`coho env history prod` lists every move, with its reason and who made it.

## Where to go from here

- **Deploy it.** A host sets the variables in `.env.prod` as its own secret settings, and
  runs `npm run build` and `npm run start`. Variables a host sets win over any file, and
  `.env.local` and `.env.prod` stay on your machine.
- **Give every deployment its own key.** `coho key list` shows the keys, and
  `coho key revoke <id>` stops one within a few seconds, without touching the others.
- **Open `prod` to everyone.** A blog's content is public anyway, so
  `coho key public prod` lets anyone read `prod` without a key. Leave the key in
  `.env.prod`: it still works, and the tags behind `prod` still need one.
- **Use the pipeline.** Promote each tag to `qa` and `stage` before `prod`, and give the
  people who check releases the `maintainer` or `release_manager` role.

## If something goes wrong

- **`tag create` fails with `TAG_CONTENT_INVALID`:** it lists the entries that fail, and
  what is wrong with each. Nothing was tagged: correct them on the trunk, and tag again.
- **`tag create` fails with `REF_NAME_TAKEN`:** a tag with that name exists already, and
  tags are never deleted. Choose the next name: `coho tag list` shows the ones used.
- **`promote` gives up with `SNAPSHOT_NOT_READY`:** the snapshot took longer to build than
  the CLI waits. Run the same command again: the build carries on in the meantime.
- **`promote` fails with `ENVIRONMENT_MOVED`:** `prod` no longer points where `--expected`
  says. `coho env show prod` shows where it does.
- **`key create` fails with `FORBIDDEN`, naming `delivery:keys`:** only the project's owner
  can create delivery keys. Ask the owner, or have them grant you the `owner` role.
- **`npm run build:prod` fails with `ENOENT` for `.env.prod`:** the file is not in the
  folder you ran it from. Run it in `blog-site`, beside `package.json`.
- **`process.loadEnvFile is not a function`:** Node.js is older than 20.12. Check with
  `node --version`.
- **`set COHO_PREVIEW_TOKEN to preview unreleased content, or COHO_DELIVERY_KEY to read
  released content, not both`:** `.env.prod` is missing the `COHO_PREVIEW_TOKEN=` line, or
  your shell has `COHO_PREVIEW_TOKEN` set. Check with `echo $COHO_PREVIEW_TOKEN`.
- **`COHO_DELIVERY_URL, COHO_PROJECT are needed to read released content`:** fill them in
  in `.env.prod`.
- **`KEY_REQUIRED`:** `COHO_DELIVERY_KEY` in `.env.prod` is empty.
- **`PROJECT_NOT_FOUND`:** the key is wrong, expired or revoked, for another project, or
  not for this ref, such as a key for `prod` reading `v0.0.1` directly. Delivery answers
  them all the same way on purpose, so a guessed key learns nothing. Check
  `COHO_DELIVERY_KEY` and `COHO_PROJECT`, and `coho key list`.
- **`REF_NOT_FOUND`:** nothing is promoted to `prod` (`coho env show prod`), or
  `COHO_REF` is misspelled.
- **`npm run start:prod` fails with `EADDRINUSE` on 3001:** it is running already, in
  another terminal.
- **The built site shows `dev`'s content:** it was built with `npm run build`, which reads
  `.env.local`. Build with `npm run build:prod`.
- **The site still shows the old content after a promotion:** reload after a minute, then
  again (step 8). `coho env show prod` shows which tag it serves.
