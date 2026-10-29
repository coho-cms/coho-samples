# 3. Load it

This page sends the batches `convert` wrote to the project's trunk, `v0.0.x`.

## 1. Make a token for the load

`catalog.py` posts each batch to Coho's import, `…/refs/{ref}/backup`. That is not a CLI
command, so the script needs a credential of its own. A project token is one: one project,
one role, and an expiry. Loading entries needs nothing above `author`, so give it no more:

```bash
coho token create --role author --label "OpenAlex load" --expires 7
```

The token is shown once, and only its hash is kept. Put it where `catalog.py` looks for it,
in this terminal only:

```bash
export COHO_TOKEN=<the token>
```

## 2. Load

```bash
uv run catalog.py load
```

`load` reads where to send the batches from `coho status`: the address, the account, the
project, and the current ref. Each batch is one transaction, so it lands whole or not at
all, and each one it lands is written to `data/loaded.txt`:

```
Loading into research-catalog on v0.0.x: 0 of 36 batches already in.
  0001.json: 1,000 created, 0 updated, 0 unchanged in …s
  0002.json: 1,000 created, 0 updated, 0 unchanged in …s
```

The first batches are topics, institutions, sources, and authors, and the works come
last, so when a work is written, what it links to is already there.

If it stops, for a refused batch or a closed laptop, run it again: it skips every batch in
`data/loaded.txt`. Running `convert` again clears that file, and loading again then reports
each entry as unchanged rather than writing it twice, because each entry's id comes from
its OpenAlex id.

To load somewhere other than the current ref, such as a branch you have created, name it:

```bash
uv run catalog.py load --ref openalex-import
```

## 3. Revoke the token

When the load is done, the token has nothing left to do:

```bash
coho token list
coho token revoke <token-id>
unset COHO_TOKEN
```

Next: [Explore it](04_EXPLORE.md).
