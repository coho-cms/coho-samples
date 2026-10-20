# 1. Set up the content model

This page builds the content model and sets up some sample content for the blog. You create a project, add three content types
(`tag`, `teamMember` and `blogPost`), and load a few entries by hand. Then you link the
entries to each other, preview them on `dev`, and fix a mistake. Releasing content to `qa`
and reading it with a delivery key, the way a published website does, is a later tutorial.

Sign in first, as described under [Before you start](README.md#before-you-start).

This page is the same as the Node.js sample's. If you have already worked through
[that one](../../node/cli-next-blog/01_CONTENT.md), your `blog-sample` project is ready:
skip to [Create the client library](02_CLIENT_LIBRARY.md).

Every command on this page runs from inside the `cli-ktor-blog` folder. Start by moving
into it, from where you cloned the samples:

```bash
cd coho-samples/kotlin/cli-ktor-blog
```

From here, paths are relative to `cli-ktor-blog`, so `types/tag.json` means this folder's
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

Reading `dev` needs a credential. Your `coho login` belongs to the CLI, and the portal's
sign-in belongs to the portal's pages, so a read of your own takes a **project token**.
Create one that can only read:

```bash
coho token create --role viewer --label "dev preview"
```

### Finding your token

The token is the line under `Project token`, starting `coho_pt_`:

```
id  01a1…
label  dev preview
role  viewer
expires  2027-01-18T09:00:00Z
Project token
coho_pt_AbCdEf…
This project token is shown once and cannot be retrieved again.
```

Copy it now, and keep it somewhere safe, such as your password manager. Coho stores only
a hash of it, so neither the CLI nor the portal can show it again. If you lose it,
`coho token list` shows its id under `TOKEN`: revoke it with `coho token revoke <id>`, and
create another. A token works for 90 days unless you pass `--expires`.

### Read the posts

The read also names the account and project by their IDs. `coho status` shows both, each
as a name followed by its ID in parentheses. Put the three values in shell variables, so the
commands that follow can use them without pasting the token into each one:

```bash
ACCOUNT=<account-id>
PROJECT=<project-id>
TOKEN=<the coho_pt_ token>
```

Then read the blog posts from `dev`, through Coho's preview:

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
    "https://api-dev.coho-cms.dev/api/v1/accounts/$ACCOUNT/projects/$PROJECT/preview/dev/entries?type=blogPost&depth=1"
```

Don't worry - this is just an example of how to make a raw API call. We'll get into the SDK in the next step
or two. 

Passing `depth=1` includes each post's author, tags and related posts in the
same response. Without it, those references are listed under `unresolved` with the reason
`depth`. To show one entry by its slug, replace `entries?type=blogPost` with
`entries-by-slug/elm-street-drainage`.

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

`--set` reads the current entry, changes only that field, and writes it back. Run the
`curl` from step 8 again to see the change on `dev`.

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
- **The preview `curl` returns `401` with `UNAUTHENTICATED`:** no token reached Coho.
  Check that `TOKEN` is set in this shell (`echo $TOKEN` prints it) and that the command
  says `Bearer $TOKEN`. A new terminal starts without the variables: set them again.
- **The preview `curl` returns `404` with `PROJECT_NOT_FOUND`:** the token is mistyped,
  revoked or expired, or it belongs to another project; or `ACCOUNT` or `PROJECT` is wrong.
  Compare them with `coho status`, and create another token if you have lost this one.
- **Opening the preview address in a browser says `401`, even when you are signed in to
  the portal:** a browser's sign-in belongs to the portal at `app-dev.coho-cms.dev`, and is
  never sent to `api-dev`. Read the preview with `curl` and a token, as in step 8.

Next: [Create the client library](02_CLIENT_LIBRARY.md).
