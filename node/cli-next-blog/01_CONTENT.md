# 1. Set up the content model

This page builds the content model and sets up some sample content for the blog. You create a project, add three content types
(`tag`, `teamMember` and `blogPost`), and load a few entries by hand. Then you link the
entries to each other, preview them on `dev`, and fix a mistake. Releasing content to `qa`
and reading it with a delivery key, the way a published website does, is a later tutorial.

Sign in first, as described under [Before you start](README.md#before-you-start).

Every command on this page runs from inside the `cli-next-blog` folder. Start by moving
into it, from where you cloned the samples:

```bash
cd coho-samples/node/cli-next-blog
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

The posts are created without their links. Step 6 adds those.

```bash
coho entry create -t blogPost -f entries/blog-posts/roundabout-second-opinion.json
coho entry create -t blogPost -f entries/blog-posts/elm-street-drainage.json
```

Each entry's slug comes from its `_name`, so the posts become `roundabout-second-opinion`
and `elm-street-drainage`.

## 6. Link the posts

Name each entry by its slug, with an `@` in front: `@priya-shah` is the entry whose slug
is `priya-shah`. A reference holds the ID of the entry it points to, so the CLI looks each
slug up on the current ref and writes that ID, and the server then checks that the entry
is of a type the field allows. The value after `--set` is JSON, so a list goes in quotes.
Note that the @ reference results in a separate lookup from the CLI into the management API.
If you are writing a large migration script, you will likely want to get the ID once and pass
that in rather than using the @<slug> shortcut for all calls. 

Link the roundabout post to Priya and to the Traffic tag:

```bash
coho entry put @roundabout-second-opinion --set author=@priya-shah --set 'tags=["@traffic"]'
```

Link the Elm Street post to Tom, to the Drainage and Project notes tags, and to the
roundabout post as a related read:

```bash
coho entry put @elm-street-drainage --set author=@tom-okafor \
    --set 'tags=["@drainage","@project-notes"]' \
    --set 'related=["@roundabout-second-opinion"]'
```

## 7. Check the result

Show one of the linked posts:

```bash
coho entry get @elm-street-drainage
```

The `author`, `tags` and `related` fields now hold the IDs of the entries you named.
`coho entry list -t tag` shows which ID belongs to which slug.

## 8. Preview on dev

`dev` is a live environment. It points at the newest saved content on the trunk, `v0.0.x`,
not at a tag. Use it to see what the entries look like as you work.

Find the account and project IDs in the output of `coho status`.

Sign in to the dev site first. Open this address in the browser. If it shows an error,
open `https://api-dev.coho-cms.dev/auth/login` and sign in, then try again:

```
https://api-dev.coho-cms.dev/api/v1/me
```

Then open the blog posts from `dev`, replacing `<account-id>` and `<project-id>`:

```
https://api-dev.coho-cms.dev/api/v1/accounts/<account-id>/projects/<project-id>/preview/dev/entries?type=blogPost&depth=1
```

`depth=1` includes each post's author, tags and related posts in the same response.
Without it, those references are listed under `unresolved` with the reason `depth`. To
show one entry by its slug, replace `entries?type=blogPost` with
`entries-by-slug/elm-street-drainage?depth=1`.
Preview responses come through your signed-in session, so the browser needs nothing else.

The response lists entries in two places. `roots` holds the IDs of the entries the
request asked for: here, every blog post, in the order the list is sorted. A request for
one entry has one root. `entries` holds every root and every entry reached from one
within `depth`, keyed by ID, each once. It is a map, so it has no order, and it cannot
tell a post you asked for from an author it links to. `roots` is how you know: start
from it, and look each ID up in `entries`. The authors and tags are in `entries` but not
in `roots`. The roundabout post is a root even though Elm Street links to it as related,
because the request asked for it too.

This is not how you will normally access content, we have much
more convenient methods, but it's worth knowing a few of the lower level API calls just to understand
what's happening behind the curtains.

## 9. Fix a mistake

A fix is saved on the trunk like any other change, and `dev` shows it straight away. For
example, to correct the summary of the Elm Street post:

```bash
coho entry put @elm-street-drainage --set 'summary={"en-US":"The corrected summary."}'
```

`--set` reads the current entry, changes only that field, and writes it back. Check the
change in the dev preview from step 8.

## If something goes wrong

- **`SLUG_CONFLICT` or `INTERNAL_NAME_CONFLICT` on create:** the entry already exists.
  List it with `coho entry list -t <type>`, and delete it with
  `coho entry delete @<slug>` if you want to load it again.
- **`ENTRY_NOT_FOUND` for an `@` name:** no entry on the ref has that slug. Check the
  `SLUG` column of `coho entry list -t <type>`. A slug is looked up on a branch or an
  environment on one, such as `dev`; on a tag, use the ID.
- **`VALIDATION_FAILED`:** the message names the field that is wrong. The most common
  cause is a `layout` or `disciplines` value that is not in the type's list.
- **`type put` says the type exists:** pass the ETag from `coho type get <slug>` with
  `--if-match`, or add `--force` to overwrite it.
- **A reference is rejected:** check that the entry you named is of the right type.
  Authors must be `teamMember` entries, and tags must be `tag` entries.
- **`VERSION_CONFLICT` on `entry put --set`:** someone else saved the entry between the read
  and the write. Run the command again.
- **The dev preview returns `401`:** sign in at `https://api-dev.coho-cms.dev/auth/login`,
  then load the address again.

Next: [Create the client library](02_CLIENT_LIBRARY.md).
