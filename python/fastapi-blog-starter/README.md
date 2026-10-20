# FastAPI blog starter

A FastAPI web service for a blog, ready to read its posts from Coho and answer with JSON. The
routes, the response models and the reads are done. What is left is yours: your content
library, and the repeaters that build each list of posts, tags and related posts.

It is built for the content model in [cli-fastapi-blog](../cli-fastapi-blog/README.md), with
the `blogPost`, `teamMember` and `tag` types, and the client library from
[Create the client library](../cli-fastapi-blog/02_CLIENT_LIBRARY.md).
[Build the FastAPI service](../cli-fastapi-blog/03_APPLICATION.md) walks through setting it
up, step by step.

```
fastapi-blog-starter/
├── pyproject.toml          the service's packages: FastAPI, and markdown-it-py
├── app/
│   ├── main.py             the app: its routes, and the Coho client they read through
│   ├── content.py          the only mention of your library's name
│   ├── dependencies.py     how a route asks for the Coho client
│   ├── site.py             the site's name, its locale, and markdown as HTML
│   ├── schemas.py          what the API answers with
│   └── routes/
│       └── posts.py        the latest posts                    ← a repeater
│                           a post, with its author and tags    ← two repeaters
└── .env.example            the values the service reads
```

## In short

You need [uv](https://docs.astral.sh/uv/).

1. Copy this folder beside your library, such as `~/workarea/blog-api` next to
   `~/workarea/yourorg-blog-content`.
2. Add the library: `uv add --editable ../yourorg-blog-content`. If your library has
   another name than `yourorg-blog-content`, change it in `app/content.py`.
3. Copy `.env.example` to `.env`, which git ignores, and fill in `COHO_ACCOUNT`,
   `COHO_PROJECT` and a project token as `COHO_PREVIEW_TOKEN`. Copying `blog-test`'s is
   enough: `cp ../blog-test/.env .env`.
4. Run it, and open http://localhost:8000/docs:

   ```bash
   uv run --env-file .env fastapi dev app/main.py --reload-dir app --reload-dir ../yourorg-blog-content/src
   ```

5. Replace each `Repeater:` comment in `app/routes/posts.py`, and the empty list under it,
   with a list comprehension over its list. The tutorial has the code for each.
6. `uv run mypy` checks the service against the library's types.

The service imports the library from its folder, and `fastapi dev` watches both, so a
regenerated library reaches the running service with nothing to install. When the library is
published, the path becomes `uv add yourorg-blog-content`.
