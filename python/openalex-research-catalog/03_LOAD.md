# 3. Load it

This page sends the batches `convert` wrote to the project's trunk, `v0.0.x`.

## 1. Choose who loads it

`catalog.py` posts each batch to Coho's import, `…/refs/{ref}/backup`. That is not a CLI
command, so the script finds a credential itself, in this order:

- **A project token**, if `COHO_TOKEN` is set. One project, one role, and an expiry.
- **You**, signed in with `coho login`. The script reads the same sign-in the CLI keeps,
  for the same profile, and refreshes it as the CLI does, so a load longer than an hour
  carries on.

Signed in is the shorter way, and needs nothing more if you have at least the `author`
role on the project, which you do if you created it. Skip to step 2.

A token is for a load you want to keep apart from your own access: one that runs
unattended, or that someone without a login of their own runs for you. Loading entries
needs nothing above `author`, so give it no more:

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
project, and the current ref. The first time, `uv` also installs the Coho SDK, which `load`
uses to sign in; the other steps need nothing beyond the standard library. Each batch is
one transaction, so it lands whole or not at all, and each one it lands is written to
`data/loaded.txt`:

```
Loading into research-catalog on v0.0.x as you: 0 of 36 batches already in.
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

If you loaded as yourself, there is nothing to tidy up. If you made a token, it has nothing
left to do once the load is done:

```bash
coho token list
coho token revoke <token-id>
unset COHO_TOKEN
```

Next: [Explore it](04_EXPLORE.md).
