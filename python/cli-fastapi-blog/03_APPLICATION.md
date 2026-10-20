# 3. Build the FastAPI service

This page wires the client library into a FastAPI web service for the blog. Its routes list
the blog posts, and give each post with its author and tags, as JSON, all through the
library's typed reads. The types catch a misspelled field or a missing reference while you
build, before the service ever calls Coho.

You need the client library from [Create the client library](02_CLIENT_LIBRARY.md), with
its code generated. The service brings its own settings and token: the library's `.env` only
holds the token `coho-codegen pull` uses, and never goes with it.

The service starts from [fastapi-blog-starter](../fastapi-blog-starter/README.md), a FastAPI
app whose routes, response models and reads are already written. This page adds the two
things that are yours: the library, and the repeaters that build each list of posts, tags
and related posts.

Like `blog-test`, the service lives beside the library, outside this repository:

```
~/workarea/
├── yourorg-blog-content/   the client library, from page 2
├── blog-test/              the small program, from page 2
└── blog-api/               the service, from this page
```

## 1. Copy the starter

From the folder you cloned the samples into:

```bash
cp -R coho-samples/python/fastapi-blog-starter ~/workarea/blog-api
```

Here is what it holds. The arrows mark where the repeaters go:

```
blog-api/
├── pyproject.toml          the service's packages: FastAPI, and markdown-it-py
├── app/
│   ├── main.py             the app: its routes, and the Coho client they read through
│   ├── content.py          the only mention of the library's name
│   ├── dependencies.py     how a route asks for the Coho client
│   ├── site.py             the site's name, its locale, and markdown as HTML
│   ├── schemas.py          what the API answers with
│   └── routes/
│       └── posts.py        the latest posts                    ← a repeater
│                           a post, with its author and tags    ← two repeaters
└── .env.example            the values the service reads
```

## 2. Add the library

While you develop, the service installs the library from its folder, as `blog-test` does:

```bash
cd ~/workarea/blog-api
```

```bash
uv add --editable ../yourorg-blog-content
```

This adds the library to `pyproject.toml`'s dependencies, and says where it is:

```toml
[tool.uv.sources]
yourorg-blog-content = { path = "../yourorg-blog-content", editable = true }
```

The service imports the library's code from its folder, so a regenerated library is in the
service the next time it starts, with nothing to install. When the library is published to
a package index, `uv add yourorg-blog-content` replaces the path, and nothing else in the
service changes. If you use a different mechanism for local development across several
projects, such as a workspace, feel free to use it instead.

The service names the library in one file, `app/content.py`:

```python
from yourorg_blog_content import *  # noqa: F403  every content type, and the clients
```

If you named the library something other than `yourorg-blog-content`, change it there.
Every other module imports the library's types from `app.content`.

## 3. Say where dev is

The service reads the same values as `blog-test`: where `dev`'s content is, and the token to
read it with. Copy `blog-test`'s `.env`:

```bash
cp ../blog-test/.env .env
```

The starter's `.gitignore` already keeps `.env` out of git. Its `.env.example` lists the
values, for whoever sets the service up next.

Sharing `blog-test`'s token is fine while you try things out. A real service gets a token of
its own, so each can be revoked without breaking the other. Create one with
`coho token create --role viewer --label "blog-api preview"`, and put it in `.env` as
`COHO_PREVIEW_TOKEN`.

The client is made once, when the service starts, in `app/main.py`:

```python
async with AsyncCoho(config_from_env(os.environ)) as coho:
    app.state.coho = coho
    yield
```

`AsyncCoho` is the library's client for async code, such as FastAPI's routes: the same reads
as `Coho`, awaited. Each route asks for it with a parameter, `coho: Coho`, which
`app/dependencies.py` declares. The service runs on the server, so the token never reaches
whoever calls it.

## 4. Run it

```bash
uv run --env-file .env fastapi dev app/main.py --reload-dir app --reload-dir ../yourorg-blog-content/src
```

`fastapi dev` runs the service, and restarts it as you save. The `--reload-dir`s say what to
watch: the service's code, and the library's, so a regenerated library restarts it too.
Open http://localhost:8000/docs. FastAPI lists every route there, with what it answers, and
**Try it out** calls it.

Ask for the posts, there or with `curl`:

```bash
curl -s http://localhost:8000/posts
```

```json
[]
```

The route reads the posts, and nothing puts them in its answer yet. That is what the
repeaters are for.

## 5. List the posts

A repeater builds the same thing for each item of a list. In Python, it is a list
comprehension over the list. Each route already reads its content, and marks the place for
each repeater with a `Repeater:` comment.

Open `app/routes/posts.py`. `latest_posts` reads the posts, newest first:

```python
# Newest first. Depth 1 brings each post's author and tags in the same request.
posts = await coho.blog_post.list(order="-publishedAt", depth=1)
```

Replace the `Repeater:` comment, and the `return []` under it, with a summary of each post:

```python
return [summary(post) for post in posts.items]
```

Save, and the service restarts. Ask for the posts again: both are there, each with its
date, its author and its summary. The roundabout post has `"featured": true`.

`summary`, further down the file, shows how a post's author is read: the post was read with
`depth=1`, so `post.author` is the team member itself, and `isinstance(post.author,
TeamMember)` is true.

## 6. Give a post's tags and related posts

Ask for a post:

```bash
curl -s http://localhost:8000/posts/elm-street-drainage
```

It has its title, its author with a short bio, and its body, both as the markdown it was
written in and as HTML. Its `tags` and `related` are empty. The `post` route reads the post
by its slug, again with `depth=1`, so its tags and related posts come in the same request.

In `post`, replace the first `Repeater:` comment, and the `tags=[]` under it, with the name
of each tag:

```python
tags=[tag.name for tag in resolved(post.tags)],
```

Replace the second, and `related=[]`, with a link to each related post:

```python
related=[link(related) for related in resolved(post.related)],
```

`resolved` comes from the library, like the types. Add it to the import at the top of the
file:

```python
from app.content import BlogPost, TeamMember, resolved
```

The Elm Street post now has the Drainage and Project notes tags, and links to the
roundabout post. The roundabout post has no related posts, so its `related` is empty.

`resolved` is there because a reference is not always an entry. `post.tags` is a list of
`Linked[Tag]`: each is the tag, or a stub Coho could not follow, such as a link to a deleted
tag. `resolved` leaves the stubs out, and gives you the tags themselves.

## 7. Let the types catch a mistake

The types come from the library, so your editor knows every field. In the tags repeater,
change `tag.name` to `tag.nmae`. An editor that checks types, such as VS Code with Pylance
or PyCharm, marks it straight away. So does `mypy`, which the starter has as a development
tool:

```bash
uv run mypy
```

```
app/routes/posts.py:41: error: "Tag" has no attribute "nmae"  [attr-defined]
Found 1 error in 1 file (checked 8 source files)
```

Python itself would only find out when the route ran, and answered with a 500. The same goes
for a field removed from a content type: once the library is regenerated without it,
`mypy` fails on every read of it, not a request in production. Run it before you commit, and
in CI. Change it back to `tag.name`.

## 8. When the library changes

The service imports the library from its folder, so a change to the library reaches the
service with nothing to install. `fastapi dev` watches the library's code as well as the
service's: regenerate the library, for example because a content type changed, and the
service restarts with the new code.

## Where to go from here

- **Make it yours.** The site's name is in `app/site.py`, and what the API answers with is
  in `app/schemas.py`. The service answers with models of its own, rather than the
  library's, so its shape changes only when you change it, not whenever a content type does.
  A post's `layout` says how wide a front end should show it: `wide` and `landing` are wider.
- **Read more content** through `coho` in a route. An author route, for example, would read
  `await coho.team_member.by_slug(slug)`.
- **Publish it.** A published service reads released content with a delivery key, rather
  than `dev` with a token, set as the host's environment variables rather than a `.env`
  file, and runs with `fastapi run`. The client caches what delivery sends as long as
  delivery says it may. That is a later tutorial.

## If something goes wrong

- **`ModuleNotFoundError: No module named 'yourorg_blog_content'`:** the library is not
  added (step 2), or it has another name: change the name in `app/content.py`.
- **The service fails to start with `Coho: COHO_DELIVERY_URL, COHO_PROJECT, COHO_REF are
  needed to read released content`:** it saw none of the values. Run it with
  `uv run --env-file .env`, from `blog-api`, and check that `.env` is there (step 3).
- **`COHO_DELIVERY_URL is needed to read released content`:** no preview token reached the
  service, so it took the run for a release. Check `COHO_PREVIEW_TOKEN` in `.env`, then
  stop the service with Ctrl+C and start it again: `fastapi dev` reads `.env` only when it
  starts.
- **`COHO_ACCOUNT, COHO_PROJECT are needed to read a preview`:** add them to `.env`
  (step 3).
- **A route answers `502` with `UNAUTHENTICATED` or `PROJECT_NOT_FOUND`:** the token is
  wrong, expired or revoked, or for another project. Also check `COHO_ACCOUNT` and
  `COHO_PROJECT`. The service answers `502` whenever Coho refuses a read, with Coho's code.
- **The posts are an empty list, and no error:** check the repeater in `latest_posts`
  (step 5). If it is there, check that `dev` has posts:
  `uv run tools/catalog.py --preview` in `yourorg-blog-content`.
- **`mypy` says `Module "app.content" has no attribute "BlogPost"`:** the library has no
  generated code yet, or has another name: run page 2's step 3, or change the name in
  `app/content.py`.
- **The service still has the old library after a change:** check that it runs with
  `--reload-dir ../yourorg-blog-content/src` (step 4), or stop it with Ctrl+C and start it
  again.
- **`[Errno 48] Address already in use`:** another copy of the service is still running.
  Stop it, or add `--port 8001`.

Next: [Images and downloads](04_IMAGES_AND_ASSETS.md).
