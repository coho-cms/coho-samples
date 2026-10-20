# 2. Create the client library

Now we'll build a client library to have more convenient access to the content from
our own codebase. This creates a standalone .NET library that gets its configuration from
the app that uses it. You will want to set this up as its own project that can be updated
as your content model changes, published to a NuGet feed, and referenced by all of the
projects which need access to your content.

This step in the tutorial will create the new library, generate its types from `dev`, and run
some tests to make sure it can access your Coho content. `dev` follows the head of the trunk,
which is where your development work is most likely to be. Then you'll write a small program
of your own that uses the library, and point it at `dev` without changing its code.

After that, we'll show how you can create your own content branch, point your program at
that branch, and when you're happy with the content changes, merge that into the version branch.

Everything on this page uses two credentials: your `coho login`, for the CLI, and project
tokens, for the library and your own code. Releasing content to `qa` and reading it with a
delivery key, the way a published website does, is a later tutorial.

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

Install the library template from NuGet:

```bash
dotnet new install CohoCms.Templates
```

Create the library in a folder of its own, outside this repository, such as
`~/workarea`. `dotnet new` makes the library's folder, `YourOrg.BlogContent`, and names
the solution, the project and its namespace after it:

```bash
cd ~/workarea
dotnet new coho-library -n YourOrg.BlogContent
cd YourOrg.BlogContent
```

The library's tool, `coho-codegen`, is a local tool, pinned in `.config/dotnet-tools.json`.
Restore it, then point the library at your project:

```bash
dotnet tool restore
```

```bash
dotnet coho-codegen init --url https://api-dev.coho-cms.dev --ref dev
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
dotnet coho-codegen pull
```

```bash
dotnet coho-codegen generate
```

`generate` warns that the types came from a branch, whose types can change. That is
expected while you develop: the library's types follow `dev`, so they change when `dev`
does. It is a reminder for later. When you publish the library for other projects to
reference, generate it from a tag, so a published version always means the same types.

There is now a record for each content type in `src/YourOrg.BlogContent/Coho`, such as
`BlogPost.cs`. Build the library, and run its tests:

```bash
dotnet build
```

```bash
dotnet test
```

## 4. List the content

List the content the library can read on `dev`:

```bash
dotnet run --project tools/Catalog -- --preview
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
`tools/Catalog`, a development tool, never packed or published, so it is not part of the
library. A site uses the same typed reads, such as
`coho.BlogPost.ListAsync(new() { Order = BlogPost.SortBy.PublishedAt.Descending })`.

## 5. Write your own code

A site or service uses the library the way any program does: it references it, and hands
it its configuration. The library reads no files. Whatever runs the program supplies the
values: on your machine, user secrets; on a host, the platform's settings and secrets. So
the same code reads `dev` on your machine and a branch in a preview deployment.

Try it with a small program beside the library. Create a console app, and reference the
library's project, with `Microsoft.Extensions.Hosting` for its configuration:

```bash
cd ..
dotnet new console -o BlogTest
cd BlogTest
dotnet add reference ../YourOrg.BlogContent/src/YourOrg.BlogContent/YourOrg.BlogContent.csproj
dotnet add package Microsoft.Extensions.Hosting
```

Replace `Program.cs` with this. It lists the blog posts, newest first, with each one's
author, from whichever ref it is given:

```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using YourOrg.BlogContent;

// What to read, and with which credential: configuration decides, not the code.
var builder = Host.CreateApplicationBuilder(args);
builder.Logging.SetMinimumLevel(LogLevel.Warning);
builder.Services.AddCoho();
using var host = builder.Build();
var coho = host.Services.GetRequiredService<Coho>();

// Depth 1 brings each post's author, tags and related posts in the same request.
var posts = await coho.BlogPost.ListAsync(new() { Order = BlogPost.SortBy.PublishedAt.Descending, Depth = 1 });

Console.WriteLine($"Blog posts on {builder.Configuration["COHO_REF"]}:\n");
foreach (var post in posts.Items)
{
    var author = post.Author?.Value?.FullName ?? "no author";
    Console.WriteLine($"  {post.PublishedAt:yyyy-MM-dd}  {post.Title}, by {author}");
    Console.WriteLine($"              {post.Summary}\n");
}
```

`AddCoho` comes from the library. It registers its client, `Coho`, configured from the
`COHO_*` values in the program's configuration. The types come from the library too, so a
misspelled field such as `post.Autor` is an error in your editor rather than a surprise at
runtime.

## 6. Say where dev is

The program needs a credential to read `dev`. Create a project token for it, rather than
reusing the library's `COHO_TOKEN`. They could be the same token, but the library's stays
with the library, while this one goes wherever the program runs, so each can be revoked
without breaking the other:

```bash
coho token create --role viewer --label "blog-test preview"
```

Copy the token from under `Project token`, as before.

Keep the program's settings in **user secrets**: a file in your home folder, outside the
project, so a token there can never be committed. Turn them on for the project, then set
where `dev`'s content is and the token. Replace the placeholders with the `account` and
`project` that `coho-codegen init` wrote into the library's `coho.config.json`, and with
the token:

```bash
dotnet user-secrets init
dotnet user-secrets set COHO_URL https://api-dev.coho-cms.dev
dotnet user-secrets set COHO_ACCOUNT <account-id>
dotnet user-secrets set COHO_PROJECT <project-id>
dotnet user-secrets set COHO_REF dev
dotnet user-secrets set COHO_LOCALE en-US
dotnet user-secrets set COHO_PREVIEW_TOKEN <preview-token>
```

`COHO_URL` is Coho's own address, the one the CLI uses. `COHO_LOCALE` picks the
translation of localized fields, such as the titles.

A program reads user secrets only when it runs in the `Development` environment, as it
does on your machine and never on a host. Say so in `Properties/launchSettings.json`,
which `dotnet run` reads. Create the folder and the file, named exactly that, with the `s`
in `Settings`:

```json
{
  "profiles": {
    "BlogTest": {
      "commandName": "Project",
      "environmentVariables": {
        "DOTNET_ENVIRONMENT": "Development"
      }
    }
  }
}
```

## 7. Run it against dev

```bash
dotnet run
```

```
Using launch settings from …/BlogTest/Properties/launchSettings.json...
Blog posts on dev:

  2026-10-01  What the drainage survey found under Elm Street, by Tom Okafor
              The corrected summary.

  2026-09-15  Why every roundabout needs a second opinion, by Priya Shah
              A roundabout that looks right on paper can still jam at rush hour. Here is how we check.
```

The first line says `dotnet run` found the launch settings, so the program runs in
`Development` and reads its user secrets. `dotnet run` builds the library too, because the
program references its project.

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

Point the program at the branch. An environment variable wins over a user secret, so
nothing else changes:

```bash
COHO_REF=feature/spring-update dotnet run
```

The Elm Street post now shows `Rewritten on a branch.` Run the command from step 7 again:
`dev` still shows `The corrected summary.` If you are a developer working on your own branch
for a while, set `COHO_REF` to your branch in the user secrets until you're done:
`dotnet user-secrets set COHO_REF feature/spring-update`.

If a branch changes a content type, generate the library's types from it too. In
`YourOrg.BlogContent`:

```bash
dotnet coho-codegen pull --ref feature/spring-update && dotnet coho-codegen generate
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

- **`dotnet new` says no template matches `coho-library`:** install the template first, as
  in step 2. `dotnet new list coho` shows whether it is installed.
- **`dotnet coho-codegen` is not found:** run `dotnet tool restore` in the library's folder.
  The tool is local to the library, so it runs only there.
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
- **`dotnet run` fails with `COHO_DELIVERY_URL, COHO_PROJECT, COHO_REF are needed to read
  released content`:** none of the user secrets were read, because the program did not run
  in `Development`. If the output does not start with `Using launch settings from`,
  `dotnet run` did not find the file: check that it is `Properties/launchSettings.json`,
  spelled exactly so, in the `BlogTest` folder. Then check that it sets
  `DOTNET_ENVIRONMENT` to `Development`, and that `dotnet user-secrets list` shows the
  values.
- **`dotnet run` fails with `COHO_DELIVERY_URL is needed to read released content`:** no
  preview token reached the configuration, so the program took the run for a release.
  Check `COHO_PREVIEW_TOKEN` with `dotnet user-secrets list`.
- **`COHO_ACCOUNT is needed to read a preview`, or another value:** set it with
  `dotnet user-secrets set` (step 6).
- **`UNAUTHENTICATED` or `PROJECT_NOT_FOUND`:** the token is wrong, expired or revoked, or
  for another project. Also check `COHO_ACCOUNT` and `COHO_PROJECT` in the user secrets.
- **`REF_NOT_FOUND` on the branch:** check the branch name in `COHO_REF` against
  `coho branch list`.

Next: [Build the Razor Pages blog](03_APPLICATION.md).
