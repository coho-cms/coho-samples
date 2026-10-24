# Installing the `coho` CLI

Every sample here uses the `coho` command line to sign in, create a project and load its
content. This page sets it up once; each sample's README then starts from `coho login`.

## 1. Install it

The CLI is a Python program, published on PyPI as
[`coho-cli`](https://pypi.org/project/coho-cli/). Install it with
[uv](https://docs.astral.sh/uv/), which keeps it in its own environment and downloads a
Python for it if you have none.

Install uv first, if `uv --version` does not answer:

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# or, on macOS: brew install uv
```

```powershell
# Windows
winget install --id=astral-sh.uv -e
# or: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then install the CLI, and put uv's command folder on your `PATH`:

```bash
uv tool install coho-cli
uv tool update-shell
```

Open a new terminal, so it sees the new `PATH`, and check:

```bash
coho --version
```

```
CohoCMS
a CohoWorks project · v2026.1.0a21
coho-management-sdk 2026.1.0a12
```

Your version may be newer.

### With pipx instead

If you already use [pipx](https://pipx.pypa.io/) and have Python 3.11 or later:

```bash
pipx install coho-cli
pipx ensurepath
```

The package is `coho-cli`. Do not `pip install coho`: that is an unrelated project.

## 2. Point it at Coho

The samples use Coho's development environment. Set it up as your default profile, so no
command needs a `-p` flag:

```bash
coho configure --url https://api-dev.coho-cms.dev \
    --oidc-domain https://auth-dev.coho-cms.dev --client-id coho-cli
```

The same command on one line, for PowerShell:

```powershell
coho configure --url https://api-dev.coho-cms.dev --oidc-domain https://auth-dev.coho-cms.dev --client-id coho-cli
```

## 3. Sign in

```bash
coho login
coho whoami
```

`coho login` opens Coho's sign-in page in your browser and keeps the tokens in your
operating system's keyring: Keychain on macOS, Credential Manager on Windows, the Secret
Service on Linux. `coho whoami` lists the accounts you belong to.

No account yet? `coho signup "Your organization"` opens the sign-up page; then run
`coho login`.

## Keeping it current

```bash
uv tool upgrade coho-cli      # or: pipx upgrade coho-cli
```

To remove it: `uv tool uninstall coho-cli` (or `pipx uninstall coho-cli`). Your profiles stay
in `~/.config/coho` until you delete them.

## If something goes wrong

| What you see | What to do |
|---|---|
| `coho: command not found`, or "not recognized" on Windows | Run `uv tool update-shell` (or `pipx ensurepath`), then open a new terminal. |
| `coho login` says there is no profile yet | Run the `coho configure` command in step 2. |
| The keyring errors or keeps prompting, as over SSH or on a server with no desktop | `coho configure --token-store file` keeps the tokens in a file only you can read instead. With no keyring at all, `coho` does that by itself. |
| Your browser does not open | `coho login --no-browser` prints the URL to open yourself. |

The full guide is in the CLI's own documentation:
[install](https://github.com/coho-cms/coho-cli/blob/HEAD/docs/install.md) and
[authentication](https://github.com/coho-cms/coho-cli/blob/HEAD/docs/authentication.md).
