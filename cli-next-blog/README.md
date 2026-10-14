# Setting up a Next.js blog with the CLI

This is the content half of the demo. It creates the content model and loads a few
entries by hand, so a Next.js site has something to read. The model shows the main
things Coho does: content types, a closed list of choices, localized text, markdown,
and references between entries.

```
cli-next-blog/
├── types/          content type definitions (tag, teamMember, blogPost)
└── entries/
    ├── tags/           three tags
    ├── team-members/   two authors
    └── blog-posts/     two posts, linked to the authors and tags below
```

Every command below runs from inside this folder. Start by moving into it:

```bash
cd cli-next-blog
```

From here, paths are relative to `cli-next-blog`, so `types/tag.json` means this folder's `types` directory.

## 0. Before you start

You need the `coho` CLI installed, and an account. Every command below uses the default
profile, so none of them needs a `-p` flag.

## 1. Sign in

Sign in to the default profile. This opens a browser:

```bash
coho login
```

If `coho login` reports that there is no profile yet, set one up with `coho configure`,
then run `coho login` again.

## 2. Check who you are

```bash
coho whoami
```

This lists the accounts you belong to. If you belong to more than one, add
`--account <name-or-id>` to the commands that follow, or set `COHO_ACCOUNT`.

## 3. Create a project

Project names must be unique within the account. If `blog-sample` is taken, pick
another name and use it in the rest of this guide.

```bash
coho project create blog-sample
```

This creates the project with a trunk ref named `v0.0.x` and the environments `dev`,
`qa`, `stage` and `prod`. It also makes the project the current one.

Confirm the context the next commands will use:

```bash
coho status
```

## 4. Create the content types

Create the `tag` type first, then `teamMember`, then `blogPost`. `blogPost` refers to
both of the others, so they need to exist first.

The slug is built from `_name` in each file, so no slug argument is needed:
`Tag` becomes `tag`, `Team member` becomes `teamMember`, and `Blog post` becomes
`blogPost`.

```bash
coho type put --file types/tag.json
coho type put --file types/teamMember.json
coho type put --file types/blogPost.json
```

Check that all three are there:

```bash
coho type list
```

## 5. Create the tags

```bash
coho entry create -t tag -f entries/tags/traffic.json
coho entry create -t tag -f entries/tags/drainage.json
coho entry create -t tag -f entries/tags/project-notes.json
```

## 6. Create the team members

```bash
coho entry create -t teamMember -f entries/team-members/priya-shah.json
coho entry create -t teamMember -f entries/team-members/tom-okafor.json
```

## 7. Create the blog posts

The posts are created without their links. Step 9 adds those once you have the IDs.

```bash
coho entry create -t blogPost -f entries/blog-posts/roundabout-second-opinion.json
coho entry create -t blogPost -f entries/blog-posts/elm-street-drainage.json
```

Each entry's slug comes from its `_name`, so the posts become `roundabout-second-opinion`
and `elm-street-drainage`.

## 8. Get the IDs

References hold entry IDs, not slugs. Read the IDs with JSON output, because the table
can shorten them. 

```bash
coho -o json entry list -t teamMember
coho -o json entry list -t tag
coho -o json entry list -t blogPost
```

Note the `id` for:

- Priya Shah and Tom Okafor
- Traffic, Drainage and Project notes
- Why every roundabout needs a second opinion, which is the `roundabout-second-opinion` post

## 9. Link the posts

Replace each `<…>` with an ID from step 8. The value after `--set` is JSON, so a list
goes in quotes. Don't worry, you won't have to do this all the time, this is just to show
you how linking works behind the scenes. 

Link the roundabout post to Priya and to the Traffic tag:

```bash
coho entry put <roundabout-post-id> --set author=<priya-shah-id> --set 'tags=["<traffic-id>"]'
```

Link the Elm Street post to Tom, to the Drainage and Project notes tags, and to the
roundabout post as a related read:

```bash
coho entry put <elm-street-post-id> --set author=<tom-okafor-id> --set 'tags=["<drainage-id>","<project-notes-id>"]' --set 'related=["<roundabout-post-id>"]'
```

## 10. Check the result

Show one of the linked posts:

```bash
coho entry get <elm-street-post-id>
```

The `author`, `tags` and `related` fields should now hold the IDs you set.

## 11. Preview on dev

`dev` is a live environment. It points at the newest saved content on the trunk, `v0.0.x`,
not at a tag. Use it to see what the entries look like before you cut a release.

Find the account and project IDs in the output of `coho status`.

Sign in to the dev site first. Open this address in the browser. If it shows an error,
open `https://api-dev.coho-cms.dev/auth/login` and sign in, then try again:

```
https://api-dev.coho-cms.dev/api/v1/me
```

Then open the blog posts from `dev`, replacing `<account-id>` and `<project-id>`:

```
https://api-dev.coho-cms.dev/api/v1/accounts/<account-id>/projects/<project-id>/preview/dev/entries?type=blogPost
```

Add `/<entry-id>` to the end of the address to show one entry. Preview responses come
through the signed-in session, so they need no key.

## 12. Fix a mistake

Tags never change, so a fix goes on the trunk and then into a new tag. `dev` shows the fix
straight away. `qa` keeps the old tag until you cut a new one (step 13).

For example, to correct the summary of the Elm Street post:

```bash
coho entry put <elm-street-post-id> --set 'summary={"en-US":"The corrected summary."}'
```

`--set` reads the current entry, changes only that field, and writes it back. Check the
change in the dev preview from step 11.

## 13. Cut a release for QA

A release is a tag on the trunk, promoted to an environment. Give each tag a name that has
not been used before. Here the next release after `v1.0.0` is `v1.0.1`:

```bash
coho tag create v1.0.1 --branch v0.0.x -m "Correct the Elm Street summary"
```

```bash
coho promote qa v1.0.1
```

`promote` waits until the release is ready, for up to five minutes. Check which tag `qa`
points at:

```bash
coho env show qa
```

`qa` is the first environment a tag can go to. `dev` follows the trunk rather than a tag, so
the release does not pass through it. If you promote a tag past an environment it could
have gone to, for example straight to `stage`, `promote` warns that a step was skipped. The
promotion still goes ahead.

## 14. Get a delivery key

A website reads published content with a delivery key, sent in the `Authorization` header.
Create one for `qa`:

```bash
coho key create --label "blog-sample qa" --ref qa
```

The key is shown once and only its hash is stored. Copy it somewhere safe now. Do not put
it in a web address, a commit or a chat.

To find a key's ID later, so you can revoke it, list the keys in JSON:

```bash
coho -o json key list
```

```bash
coho key revoke <key-id>
```

## 15. Test delivery with curl

Read `qa` the way your website will: with the key from step 14 in the `Authorization`
header. A browser cannot send that header from the address bar, so use `curl`.

Put the key in a shell variable first. `read -s` does not echo what you paste, which keeps
the key out of your screen and your shell history. Paste the key and press Enter:

```bash
read -rs COHO_KEY
```

List the blog posts, replacing `<project-id>`:

```bash
curl -H "Authorization: Bearer $COHO_KEY" "https://delivery-dev.coho-cms.dev/v1/projects/<project-id>/qa/entries?type=blogPost&locale=en-US"
```

Show one post:

```bash
curl -H "Authorization: Bearer $COHO_KEY" "https://delivery-dev.coho-cms.dev/v1/projects/<project-id>/qa/entries/<elm-street-post-id>"
```

You should see JSON with the two blog posts. Each entry has its `slug` at the top level and
its content under `fields`. If you have `jq` installed, add `| jq` to the end of a command
to make the output easier to read.

Without the header the same address returns `401`:

```bash
curl -i "https://delivery-dev.coho-cms.dev/v1/projects/<project-id>/qa/entries"
```

If it returns `200` instead, `qa` was made readable without a key at some point. Turn that
off with `coho key public` and no argument.

## 16. Generate a typed content library

A site reads this content through a content library: a TypeScript package with an
interface for each content type, generated from this project's types. This step creates
one from the `v1.0.1` release, and lists the content it can read.

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

The library reads its types with a project token. Create one that can only read, and copy
it somewhere safe; it is shown once:

```bash
coho token create --role viewer --label "blog-content library"
```

Copy the example settings:

```bash
cp .env.example .env
```

Then fill in `.env`. It is in `.gitignore`, so it stays out of commits:

- `COHO_TOKEN`: the project token you just created.
- `COHO_DELIVERY_URL`: `https://delivery-dev.coho-cms.dev`.
- `COHO_DELIVERY_KEY`: the delivery key from step 14.
- `COHO_DELIVERY_REF`: `qa`, the environment the key from step 14 reads.

Fetch the types from `v1.0.1`, and generate the library's code from them:

```bash
npm run pull
```

```bash
npm run generate
```

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

- **`SLUG_CONFLICT` or `INTERNAL_NAME_CONFLICT` on create:** the entry already exists.
  List it with `coho entry list -t <type>`, and delete it with `coho entry delete <id>`
  if you want to load it again.
- **`VALIDATION_FAILED`:** the message names the field that is wrong. The most common
  cause is a `layout` or `disciplines` value that is not in the type's list.
- **`type put` says the type exists:** pass the ETag from `coho type get <slug>` with
  `--if-match`, or add `--force` to overwrite it.
- **A reference is rejected:** check that the ID came from the list in step 8, and that
  the entry is of the right type. Authors must be `teamMember` entries, and tags must be
  `tag` entries.
- **`INVALID_PROMOTION_TARGET` when promoting to `dev`:** `dev` is live and only points at
  the trunk. Promote a tag to `qa`, `stage` or `prod` instead.
- **The dev preview returns `401`:** sign in at `https://api-dev.coho-cms.dev/auth/login`,
  then load the address again.
- **`VERSION_CONFLICT` on `entry put --set`:** someone else saved the entry between the read
  and the write. Run the command again.
- **Delivery returns `401` with `KEY_REQUIRED`:** send the key in the `Authorization` header
  (step 15). If you used `read -s`, check that `COHO_KEY` is set in the same terminal:
  `echo ${#COHO_KEY}` prints its length without showing it.
- **Delivery returns `404` with `PROJECT_NOT_FOUND`:** the key belongs to another project, or
  the project ID is wrong. Check it against `coho status`.
- **`npm run pull` fails with `401` or `403`:** check `COHO_TOKEN` in `.env`. It must be a
  project token for this project.
- **`npm run pull` fails with `404`:** the Coho server predates the type model. It needs a
  build that serves `…/refs/{ref}/type-model`.
- **`npm run catalog` fails:** a key made for `qa` reads only `qa`, so set
  `COHO_DELIVERY_REF=qa`. `PROJECT_NOT_FOUND` means the key is for another project, or
  `project` in `coho.config.json` is wrong.
