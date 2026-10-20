# 2. Create the client library

Now we'll build a client library to have more convenient access to the content from our own
codebase. This creates a standalone Java library that gets its configuration from the app
that uses it. You will want to set this up as its own project that can be updated as your
content model changes, published to a Maven repository, and used by all of the projects
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
Copy the [library template](https://github.com/coho-cms/coho-template-java) into a folder
named for the library, `blog-content`, and make it a repository of its own:

```bash
cd ~/workarea
git clone --depth 1 https://github.com/coho-cms/coho-template-java blog-content
cd blog-content
rm -rf .git && git init
```

The library is named after its folder, so it is `blog-content`. Put the token from step 1 in
the library's `.env`, which its `.gitignore` keeps out of git. Copy the example, and set
`COHO_TOKEN` in it with your editor:

```bash
cp .env.example .env
```

```
COHO_TOKEN=coho_pt_…
```

Then point the library at your project, and give it its package:

```bash
./gradlew cohoInit --args="--url https://api-dev.coho-cms.dev --ref dev --package com.yourorg.blogcontent"
```

The first run downloads Gradle and the library's packages, which takes a minute. Then Coho
says which account and project the token is for, and the library is set up for them:

```
Updated coho.config.json.
The library's package is com.yourorg.blogcontent.
It reads blog-sample, in <your account>, with the token in .env.
```

`--package` renames the template's package, `com.yourorg.content`, everywhere it appears:
the folders under `src`, the code, `build.gradle.kts` and `coho.config.json`.

## 3. Generate the typed API

Fetch the types from `dev`, and generate the library's code from them:

```bash
./gradlew cohoPull cohoGenerate
```

`cohoGenerate` warns that the types came from a branch, whose types can change. That is
expected while you develop: the library's types follow `dev`, so they change when `dev`
does. It is a reminder for later. When you publish the library for other projects to use,
generate it from a tag, so a published version always means the same types.

There is now a class for each content type in
`src/main/java/com/yourorg/blogcontent/coho`, such as `BlogPost.java`:

```java
/** Blog post */
public final class BlogPost extends EntryBase
{
    private final @Nullable String title;
    …
    private final OffsetDateTime publishedAt;
    private final @Nullable Linked<TeamMember> author;
    private final List<Linked<Tag>> tags;
    …

    /** Title. Null where the locale has no translation. */
    public @Nullable String getTitle()
    {
        return title;
    }
    …
}
```

`getTitle()` can return null, because the title is localized, and a locale with no
translation has no title. `getPublishedAt()` cannot: every post has one. `@Nullable` says
which is which, to your editor and to Kotlin. Build the library, and run its tests:

```bash
./gradlew build
```

## 4. List the content

List the content the library can read on `dev`:

```bash
./gradlew catalog --args=--preview
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
`src/tools`, a development tool, in a source set of its own, so it is never in the library.
A service uses the same typed reads, such as `coho.blogPost().list(…)`.

## 5. Write your own code

A service or a program uses the library the way any program does: it depends on it, and
hands it its configuration. The library reads no files and no environment. Whatever runs the
program supplies the values: on your machine, a `.env` file; on a host, the platform's
settings and secrets. So the same code reads `dev` on your machine and a branch in a preview
deployment.

Try it with a small program beside the library, `blog-test`. Make its folder, and give it
the library's Gradle wrapper:

```bash
cd ..
mkdir -p blog-test/src/main/java/blogtest
cd blog-test
cp -R ../blog-content/gradle ../blog-content/gradlew .
```

Create `settings.gradle.kts`. `includeBuild` builds the library from its folder, so the
program always has the library as it is now:

```kotlin
rootProject.name = "blog-test"

// The library, built from its folder: a change to it is in this program the next time it runs.
includeBuild("../blog-content")
```

Create `build.gradle.kts`. The dependency names the library by its group and name, and
`includeBuild` supplies it. The `run` task reads the program's `.env`:

```kotlin
plugins {
    application
}

repositories()
{
    mavenCentral()
}

dependencies()
{
    implementation("com.yourorg.blogcontent:blog-content")
}

java()
{
    toolchain()
    {
        languageVersion.set(JavaLanguageVersion.of(21))
    }
}

application()
{
    mainClass.set("blogtest.Main")
}

// The Coho values, from .env, which git ignores. A variable already set, such as
// COHO_REF=feature/x ./gradlew run, wins over the same one in .env.
tasks.named<JavaExec>("run")
{
    val dotenv = file(".env")
    if (dotenv.exists())
    {
        environment(
            dotenv.readLines()
                .filter { '=' in it && !it.trimStart().startsWith("#") }
                .associate { it.substringBefore('=').trim() to it.substringAfter('=').trim() }
                .filterKeys { System.getenv(it) == null },
        )
    }
}
```

Create `src/main/java/blogtest/Main.java`. It lists the blog posts, newest first, with each
one's author, from whichever ref it is given:

```java
package blogtest;

import com.cohocms.delivery.CohoEnvironment;
import com.cohocms.delivery.ListOptions;
import com.yourorg.blogcontent.coho.BlogPost;
import com.yourorg.blogcontent.coho.Coho;
import com.yourorg.blogcontent.coho.TeamMember;

public final class Main
{
    public static void main(String[] args)
    {
        // What to read, and with which credential: the environment decides, not the code.
        Coho coho = new Coho(CohoEnvironment.fromEnvironment());

        // Depth 1 brings each post's author, tags and related posts in the same request.
        var posts = coho.blogPost().list(
            new ListOptions<BlogPost.SortBy>().withOrder(BlogPost.SortBy.PUBLISHED_AT.descending()).withDepth(1));

        System.out.println("Blog posts on " + coho.content().getConfig().getRef() + ":\n");
        for (BlogPost post : posts.getItems())
        {
            String author = post.getAuthor() != null && post.getAuthor().getValue() instanceof TeamMember member
                ? member.getFullName()
                : "no author";
            System.out.printf("  %tF  %s, by %s%n", post.getPublishedAt(), post.getTitle(), author);
            System.out.printf("              %s%n%n", post.getSummary());
        }
    }
}
```

`CohoEnvironment` comes from `coho-delivery`, which the library depends on. It reads the
`COHO_*` variables, and the library's `Coho` client reads with them. The types come from the
library too, so a misspelled method such as `post.getAutor()` is a compile error rather than a
surprise at runtime.

`post.getAuthor()` is null when the post has no author. Otherwise it is a `Linked`: its
`getValue()` is the `TeamMember`, or null when Coho could not follow the link, such as one to
a deleted entry, or beyond the depth you asked for. `SortBy.PUBLISHED_AT` is one of the
fields the type can be sorted by, so an order Coho would refuse does not compile.

## 6. Say where dev is

The program needs a credential to read `dev`. Create a project token for it, rather than
reusing the library's `COHO_TOKEN`. They could be the same token, but the library's stays
with the library, while this one goes wherever the program runs, so each can be revoked
without breaking the other:

```bash
coho token create --role viewer --label "blog-test preview"
```

Copy the token from under `Project token`, as before.

Keep the program's settings in a `.env` file, and never commit it, since it holds the token.
If you make `blog-test` a git repository, put `.env` in its `.gitignore`. Create `.env` with
these lines. Replace the placeholders with the `account` and `project` that `cohoInit` wrote
into the library's `coho.config.json`, and with the token:

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

```bash
./gradlew run -q
```

```
Blog posts on dev:

  2026-10-01  What the drainage survey found under Elm Street, by Tom Okafor
              The corrected summary.

  2026-09-15  Why every roundabout needs a second opinion, by Priya Shah
              A roundabout that looks right on paper can still jam at rush hour. Here is how we check.
```

`-q` leaves out Gradle's own progress. Gradle builds the library too, because the program
includes its build.

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
COHO_REF=feature/spring-update ./gradlew run -q
```

The Elm Street post now shows `Rewritten on a branch.` Run the command from step 7 again:
`dev` still shows `The corrected summary.` If you are a developer working on your own branch
for a while, set `COHO_REF` to your branch in `.env` until you're done.

If a branch changes a content type, generate the library's types from it too. In
`blog-content`:

```bash
./gradlew cohoPull --args="--ref feature/spring-update" cohoGenerate
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

- **`./gradlew` says it cannot find Java, or needs a newer one:** install a JDK, 21 or later,
  and check `java -version`. Gradle uses the one on your `PATH`, or `JAVA_HOME`.
- **`cohoInit` says `COHO_TOKEN is not set`, or prints `Next: cp .env.example .env`:** the
  token is not in the library's `.env`. Check that the file is `.env`, in `blog-content`, with
  a line `COHO_TOKEN=coho_pt_…`.
- **`cohoInit` says `Coho refused the token`:** with `401`, the token is mistyped, revoked or
  expired: create another. With `404`, check `--url`: it is Coho's own address. Nothing is
  written when the token is refused, so run it again as it was.
- **`cohoPull` fails with `401` or `403`:** check `COHO_TOKEN` in `.env`. It must be a project
  token for this project.
- **`cohoPull` fails with `404`:** the Coho server predates the type model. It needs a build
  that serves `…/refs/{ref}/type-model`.
- **The catalog fails with `PROJECT_NOT_FOUND`:** `COHO_TOKEN` is for another project, or
  `account` or `project` in `coho.config.json` is wrong. With `UNAUTHENTICATED`, the token
  has expired or been revoked: create another.
- **`blog-test` fails with `Could not find com.yourorg.blogcontent:blog-content`:** the
  library's group or folder name differs from the dependency. The group is the package you
  gave `cohoInit`, and the name is the library's folder, `blog-content`. Check
  `includeBuild("../blog-content")` in `settings.gradle.kts`, too.
- **`main` fails with `COHO_DELIVERY_URL, COHO_PROJECT, COHO_REF are needed to read released
  content`:** the program saw none of the values. Check that `.env` is in the `blog-test`
  folder, and that `build.gradle.kts` has the `run` task's block from step 5.
- **`COHO_DELIVERY_URL is needed to read released content`:** no preview token reached the
  program, so it took the run for a release. Check `COHO_PREVIEW_TOKEN` in `.env`.
- **`COHO_ACCOUNT is needed to read a preview`, or another value:** add it to `.env`
  (step 6).
- **`UNAUTHENTICATED` or `PROJECT_NOT_FOUND`:** the token is wrong, expired or revoked, or
  for another project. Also check `COHO_ACCOUNT` and `COHO_PROJECT` in `.env`.
- **`REF_NOT_FOUND` on the branch:** check the branch name in `COHO_REF` against
  `coho branch list`.

Next: [Build the Spring Boot service](03_APPLICATION.md).
