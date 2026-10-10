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
```

```bash
coho type put --file types/teamMember.json
```

```bash
coho type put --file types/blogPost.json
```

Check that all three are there:

```bash
coho type list
```

## 5. Create the tags

```bash
coho entry create -t tag -f entries/tags/traffic.json
```

```bash
coho entry create -t tag -f entries/tags/drainage.json
```

```bash
coho entry create -t tag -f entries/tags/project-notes.json
```

## 6. Create the team members

```bash
coho entry create -t teamMember -f entries/team-members/priya-shah.json
```

```bash
coho entry create -t teamMember -f entries/team-members/tom-okafor.json
```

## 7. Create the blog posts

The posts are created without their links. Step 9 adds those once you have the IDs.

```bash
coho entry create -t blogPost -f entries/blog-posts/roundabout-second-opinion.json
```

```bash
coho entry create -t blogPost -f entries/blog-posts/elm-street-drainage.json
```

Each entry's slug comes from its `_name`, so the posts become `roundabout-second-opinion`
and `elm-street-drainage`.

## 8. Get the IDs

References hold entry IDs, not slugs. Read the IDs with JSON output, because the table
can shorten them. Don't worry, you won't have to do this all the time, this is just to show
you how linking works behind the scenes. 

```bash
coho -o json entry list -t teamMember
```

```bash
coho -o json entry list -t tag
```

```bash
coho -o json entry list -t blogPost
```

Note the `id` for:

- Priya Shah and Tom Okafor
- Traffic, Drainage and Project notes
- Why every roundabout needs a second opinion, which is the `roundabout-second-opinion` post

## 9. Link the posts

Replace each `<…>` with an ID from step 8. The value after `--set` is JSON, so a list
goes in quotes.

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

You will see this warning when you promote to `qa`:

```
warning: SKIPPED_TIER: 'v1.0.1' has not been promoted to any 'dev' environment
```

It is expected in this sample. A tag can only move to a snapshot environment, and `dev` is a
live one, so the release never goes through a `dev` step before `qa`.

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

## 15. Test delivery in the browser

A browser cannot send the `Authorization` header from the address bar. So for browser-only
testing, make `qa` readable without a key:

```bash
coho key public qa
```

This replaces the whole list of readable environments, and anyone with the address below can
read `qa` from now on. The content is sample content, so this is safe for testing. Undo it
with `coho key public` and no argument. Keys and tags are not affected: a tag still needs a
key when you address it directly.

Open these in the browser, replacing `<project-id>`:

```
https://delivery-dev.coho-cms.dev/v1/projects/<project-id>/qa/entries?type=blogPost&locale=en-US
```

```
https://delivery-dev.coho-cms.dev/v1/projects/<project-id>/qa/entries/<elm-street-post-id>
```

You should see JSON with the two blog posts. Each entry has its `slug` at the top level and
its content under `fields`.

To check the key from a terminal, which is the way your website will use it:

```bash
curl -H "Authorization: Bearer <key>" https://delivery-dev.coho-cms.dev/v1/projects/<project-id>/qa/entries
```

Without the header the same address returns `401`.

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
- **Delivery returns `401` with `KEY_REQUIRED`:** send the key in the `Authorization` header,
  or make `qa` readable without one for browser testing (step 15).
- **Delivery returns `404` with `PROJECT_NOT_FOUND`:** the key belongs to another project, or
  the project ID is wrong. Check it against `coho status`.
