# 1. Set up the content model

This page builds the content model and sets up some sample contet for the blog. You create a project, add three content types
(`tag`, `teamMember` and `blogPost`), and load a few entries by hand. Then you link the
entries to each other and preview them on `dev`. Last, you cut a release, promote it to
`qa`, and read it with a delivery key, the way a website will.

Sign in first, as described under [Before you start](README.md#before-you-start).

Every command on this page runs from inside the `cli-next-blog` folder. Start by moving
into it:

```bash
cd cli-next-blog
```

From here, paths are relative to `cli-next-blog`, so `types/tag.json` means this folder's
`types` directory.

## 1. Create a project

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

## 2. Create the content types

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

## 3. Create the tags

```bash
coho entry create -t tag -f entries/tags/traffic.json
coho entry create -t tag -f entries/tags/drainage.json
coho entry create -t tag -f entries/tags/project-notes.json
```

## 4. Create the team members

```bash
coho entry create -t teamMember -f entries/team-members/priya-shah.json
coho entry create -t teamMember -f entries/team-members/tom-okafor.json
```

## 5. Create the blog posts

The posts are created without their links. Step 7 adds those once you have the IDs.

```bash
coho entry create -t blogPost -f entries/blog-posts/roundabout-second-opinion.json
coho entry create -t blogPost -f entries/blog-posts/elm-street-drainage.json
```

Each entry's slug comes from its `_name`, so the posts become `roundabout-second-opinion`
and `elm-street-drainage`.

## 6. Get the IDs

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

## 7. Link the posts

Replace each `<…>` with an ID from step 6. The value after `--set` is JSON, so a list
goes in quotes. You won't usually link entries by hand like this. It is here to show how
linking works behind the scenes.

Link the roundabout post to Priya and to the Traffic tag:

```bash
coho entry put <roundabout-post-id> --set author=<priya-shah-id> --set 'tags=["<traffic-id>"]'
```

Link the Elm Street post to Tom, to the Drainage and Project notes tags, and to the
roundabout post as a related read:

```bash
coho entry put <elm-street-post-id> --set author=<tom-okafor-id> --set 'tags=["<drainage-id>","<project-notes-id>"]' --set 'related=["<roundabout-post-id>"]'
```

## 8. Check the result

Show one of the linked posts:

```bash
coho entry get <elm-street-post-id>
```

The `author`, `tags` and `related` fields should now hold the IDs you set.

## 9. Preview on dev

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

## 10. Fix a mistake

Tags never change, so a fix goes on the trunk and then into a new tag. `dev` shows the fix
straight away. `qa` keeps the old tag until you cut a new one (step 11).

For example, to correct the summary of the Elm Street post:

```bash
coho entry put <elm-street-post-id> --set 'summary={"en-US":"The corrected summary."}'
```

`--set` reads the current entry, changes only that field, and writes it back. Check the
change in the dev preview from step 9.

## 11. Cut a release for QA

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

## 12. Get a delivery key

A website reads published content with a delivery key, sent in the `Authorization` header.
Create one for `qa`:

```bash
coho key create --label "blog-sample qa" --ref qa
```

The key is shown once and only its hash is stored. Copy it somewhere safe now. Do not put
it in a web address, a commit or a chat. The [client library](02_CLIENT_LIBRARY.md) uses
it too.

To find a key's ID later, so you can revoke it, list the keys in JSON:

```bash
coho -o json key list
```

```bash
coho key revoke <key-id>
```

## 13. Test delivery with curl

Read `qa` the way your website will: with the key from step 12 in the `Authorization`
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

You should see JSON with the two blog posts. Each entry has its `slug` at the top level and
its content under `fields`. If you have `jq` installed, add `| jq` to the end of a command
to make the output easier to read.

Show one post:

```bash
curl -H "Authorization: Bearer $COHO_KEY" "https://delivery-dev.coho-cms.dev/v1/projects/<project-id>/qa/entries/<elm-street-post-id>"
```

Without the header the same address returns `401`:

```bash
curl -i "https://delivery-dev.coho-cms.dev/v1/projects/<project-id>/qa/entries"
```

If it returns `200` instead, `qa` was made readable without a key at some point. Turn that
off with `coho key public` and no argument.

## If something goes wrong

- **`SLUG_CONFLICT` or `INTERNAL_NAME_CONFLICT` on create:** the entry already exists.
  List it with `coho entry list -t <type>`, and delete it with `coho entry delete <id>`
  if you want to load it again.
- **`VALIDATION_FAILED`:** the message names the field that is wrong. The most common
  cause is a `layout` or `disciplines` value that is not in the type's list.
- **`type put` says the type exists:** pass the ETag from `coho type get <slug>` with
  `--if-match`, or add `--force` to overwrite it.
- **A reference is rejected:** check that the ID came from the list in step 6, and that
  the entry is of the right type. Authors must be `teamMember` entries, and tags must be
  `tag` entries.
- **`VERSION_CONFLICT` on `entry put --set`:** someone else saved the entry between the read
  and the write. Run the command again.
- **The dev preview returns `401`:** sign in at `https://api-dev.coho-cms.dev/auth/login`,
  then load the address again.
- **`INVALID_PROMOTION_TARGET` when promoting to `dev`:** `dev` is live and only points at
  the trunk. Promote a tag to `qa`, `stage` or `prod` instead.
- **Delivery returns `401` with `KEY_REQUIRED`:** send the key in the `Authorization` header
  (step 13). If you used `read -s`, check that `COHO_KEY` is set in the same terminal:
  `echo ${#COHO_KEY}` prints its length without showing it.
- **Delivery returns `404` with `PROJECT_NOT_FOUND`:** the key belongs to another project, or
  the project ID is wrong. Check it against `coho status`.

Next: [Create the client library](02_CLIENT_LIBRARY.md).
