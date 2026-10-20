# 2. Create the client library

Now we'll build a client library to have more convenient access to the content from our own
codebase. This creates a standalone Python package that gets its configuration from the app
that uses it. You will want to set this up as its own project that can be updated as your
content model changes, published to a package index, and installed by all of the projects
which need access to your content.

This step in the tutorial will create the new library, generate its types from `dev`, and run
some tests to make sure it can access your Coho content. `dev` follows the head of the trunk,
which is where your development work is most likely to be. Then you'll write a small program
of your own that uses the library, and point it at `dev` without changing its code.

After that, we'll show how you can create your own content branch, point your program at
that branch, and when you're happy with the content changes, merge that into the version branch.

Everything on this page uses two credentials: your `coho login`, for the CLI, and project
tokens, for the library and your own code. Releasing content to `qa` and reading it with a
delivery key, the way a published service does, is a later tutorial.

## 1. Create a project token

The library reads its types with a project token. Create one that can only read, and copy
it somewhere safe; it is shown once:

```bash
coho token create --role viewer --label "blog-content library"
```

As on page 1, the token is the line under `Project token`, starting `coho_pt_`, and it is
shown only this once: see [Finding your token](01_CONTENT.md#finding-your-token) if you
lose it. A token belongs to one project, so it is all the library needs to know which
project it is for: there are no account or project IDs to copy.

The token from page 1's preview would work here too. A token of its own for each use
means each can be revoked without breaking the others.

## 2. Create the library

Create the library in a folder of its own, outside this repository, such as `~/workarea`.
`coho-codegen create` makes the library's folder, `yourorg-blog-content`, from the library
template, and names the package after it. `uvx` runs `coho-codegen` without installing it:

```bash
cd ~/workarea
uvx coho-codegen create yourorg-blog-content
cd yourorg-blog-content
```

The package is `yourorg-blog-content`, and Python imports it as `yourorg_blog_content`. Set
it up: `uv sync` makes the library's virtual environment, `.venv`, and installs the Coho
packages into it, `coho-codegen` among them, at the version the library pins:

```bash
uv sync
```

Then point the library at your project:

```bash
uv run coho-codegen init --url https://api-dev.coho-cms.dev --ref dev
```

It asks for the project token from step 1. Paste it; it is not shown as you do. Coho says
which account and project the token is for, and the library is set up for them:

```
Updated coho.config.json.
It reads blog-sample, in <your account>, with the token in .env.
```

The token goes in `.env`, which the library's `.gitignore` keeps out of git.

## 3. Generate the typed API

Fetch the types from `dev`, and generate the library's code from them:

```bash
uv run coho-codegen pull
```

```bash
uv run coho-codegen generate
```

`generate` warns that the types came from a branch, whose types can change. That is
expected while you develop: the library's types follow `dev`, so they change when `dev`
does. It is a reminder for later. When you publish the library for other projects to
install, generate it from a tag, so a published version always means the same types.

There is now a module for each content type in `src/yourorg_blog_content/coho`, such as
`blog_post.py`. Each holds a Pydantic model of the type:

```python
class BlogPost(runtime.EntryBase):
    """Blog post"""

    type: Literal["blogPost"] = Field(alias="_type")

    title: str | None = None
    """Title. None where the locale has no translation."""
    …
    published_at: datetime = Field(alias="publishedAt")
    """Published at"""

    author: runtime.Linked[TeamMember] | None = None
    """Author"""

    tags: list[runtime.Linked[Tag]] = []
    """Tags"""
    …
```

Each field has its Python name, `published_at`, and keeps Coho's, `publishedAt`, as its
alias. `title` can be `None`, because it is localized, and a locale with no translation has
no title. `published_at` cannot: every post has one. Run the library's tests, and check its
types with `mypy`:

```bash
uv run pytest
```

```bash
uv run mypy
```

## 4. List the content

List the content the library can read on `dev`:

```bash
uv run tools/catalog.py --preview
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
`tools/catalog.py`, a development tool, which is not in the package, so it is never
published. A service uses the same typed reads, such as
`coho.blog_post.list(order="-publishedAt")`.

## 5. Write your own code

A service or a script uses the library the way any program does: it installs it, and hands
it its configuration. The library reads no files and no environment. Whatever runs the
program supplies the values: on your machine, a `.env` file; on a host, the platform's
settings and secrets. So the same code reads `dev` on your machine and a branch in a preview
deployment.

Try it with a small program beside the library. Create it with `uv init`, and add the
library to it:

```bash
cd ..
uv init --app blog-test
cd blog-test
uv add --editable ../yourorg-blog-content
```

`--editable` installs the library from its folder, so the program sees the library's code
as it is now, and as it is the next time you generate it, with nothing to reinstall.

Replace `main.py` with this. It lists the blog posts, newest first, with each one's author,
from whichever ref it is given:

```python
import os

from coho_delivery_sdk import config_from_env
from yourorg_blog_content import Coho, TeamMember

# What to read, and with which credential: the environment decides, not the code.
coho = Coho(config_from_env(os.environ))

# Depth 1 brings each post's author, tags and related posts in the same request.
posts = coho.blog_post.list(order="-publishedAt", depth=1)

print(f"Blog posts on {coho.content.config.ref}:\n")
for post in posts.items:
    author = post.author.full_name if isinstance(post.author, TeamMember) else "no author"
    print(f"  {post.published_at:%Y-%m-%d}  {post.title}, by {author}")
    print(f"              {post.summary}\n")
```

`config_from_env` comes from `coho-delivery-sdk`, which the library installed. It reads the
`COHO_*` variables from the environment you hand it, and the library's `Coho` client reads
with them. The types come from the library, so a misspelled field such as `post.autor` is
an error in your editor rather than a surprise at runtime.

`post.author` is one of three things: the `TeamMember` it links to, `None` when the post has
no author, or an `Unresolved` stub when Coho could not follow the link, such as one to a
deleted entry, or beyond the depth you asked for. `isinstance` asks for the first.

## 6. Say where dev is

The program needs a credential to read `dev`. Create a project token for it, rather than
reusing the library's `COHO_TOKEN`. They could be the same token, but the library's stays
with the library, while this one goes wherever the program runs, so each can be revoked
without breaking the other:

```bash
coho token create --role viewer --label "blog-test preview"
```

Copy the token from under `Project token`, as before.

Keep the program's settings in a `.env` file. First, tell git never to commit it, since it
will hold the token. `uv init` made the program a git repository, with a `.gitignore`:

```bash
echo .env >> .gitignore
```

Then create `.env` with these lines. Replace the placeholders with the `account` and
`project` that `coho-codegen init` wrote into the library's `coho.config.json`, and with the
token:

```
COHO_URL=https://api-dev.coho-cms.dev
COHO_ACCOUNT=<account-id>
COHO_PROJECT=<project-id>
COHO_REF=dev
COHO_LOCALE=en-US
COHO_PREVIEW_TOKEN=<preview-token>
```

`COHO_URL` is Coho's own address, the one the CLI uses. `COHO_LOCALE` picks the
translation of localized fields, such as the titles.

## 7. Run it against dev

`uv run --env-file .env` sets the variables in `.env` for the program, and nothing else:

```bash
uv run --env-file .env main.py
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
coho --ref feature/spring-update entry put @elm-street-drainage \
    --set 'summary={"en-US":"Rewritten on a branch."}'
```

Point the program at the branch. A variable set in the shell wins over the same one in
`.env`, so nothing else changes:

```bash
COHO_REF=feature/spring-update uv run --env-file .env main.py
```

The Elm Street post now shows `Rewritten on a branch.` Run the command from step 7 again:
`dev` still shows `The corrected summary.` If you are a developer working on your own branch
for a while, set `COHO_REF` to your branch in `.env` until you're done.

If a branch changes a content type, generate the library's types from it too. In
`yourorg-blog-content`:

```bash
uv run coho-codegen pull --ref feature/spring-update && uv run coho-codegen generate
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

- **`uvx coho-codegen` says it cannot find the package:** check `uv --version`, and update
  uv with `uv self update`, or as you installed it.
- **`coho-codegen create` says the folder is not empty:** a library of that name is already
  there. Pick another name, or remove the folder.
- **`uv run coho-codegen` is not found:** run `uv sync` in the library's folder first. The
  tool is installed in the library's own environment, so it runs only there.
- **`init` says `Coho refused the token`:** with `401`, the token is mistyped, revoked or
  expired: create another. With `404`, check `--url`: it is Coho's own address. Nothing is
  written when the token is refused, so run it again as it was.
- **`pull` fails with `401` or `403`:** check `COHO_TOKEN` in `.env`. It must be a project
  token for this project.
- **`pull` fails with `404`:** the Coho server predates the type model. It needs a build
  that serves `…/refs/{ref}/type-model`.
- **The catalog fails with `PROJECT_NOT_FOUND`:** `COHO_TOKEN` is for another project, or
  `account` or `project` in `coho.config.json` is wrong. With `UNAUTHENTICATED`, the token
  has expired or been revoked: create another.
- **`main.py` fails with `COHO_DELIVERY_URL, COHO_PROJECT, COHO_REF are needed to read
  released content`:** the program saw none of the values. Run it with
  `uv run --env-file .env`, from the `blog-test` folder, where `.env` is.
- **`COHO_DELIVERY_URL is needed to read released content`:** no preview token reached the
  program, so it took the run for a release. Check `COHO_PREVIEW_TOKEN` in `.env`.
- **`COHO_ACCOUNT is needed to read a preview`, or another value:** add it to `.env`
  (step 6).
- **`UNAUTHENTICATED` or `PROJECT_NOT_FOUND`:** the token is wrong, expired or revoked, or
  for another project. Also check `COHO_ACCOUNT` and `COHO_PROJECT` in `.env`.
- **`REF_NOT_FOUND` on the branch:** check the branch name in `COHO_REF` against
  `coho branch list`.
- **`ModuleNotFoundError: No module named 'yourorg_blog_content'`:** the library is not
  installed in `blog-test`. Run `uv add --editable ../yourorg-blog-content` (step 5).

Next: [Build the FastAPI service](03_APPLICATION.md).
