# 3. Build the Ktor service

This page wires the client library into a Ktor web service for the blog. Its routes list the
blog posts, and give each post with its author and tags, as JSON, all through the library's
typed reads. The types catch a misspelled field or a missing reference while you build,
before the service ever calls Coho.

You need the client library from [Create the client library](02_CLIENT_LIBRARY.md), with
its code generated. The service brings its own settings and token: the library's `.env` only
holds the token `cohoPull` uses, and never goes with it.

The service starts from [ktor-blog-starter](../ktor-blog-starter/README.md), a Ktor app whose
routes, response classes and reads are already written. This page adds the two things that
are yours: the library, and the repeaters that build each list of posts, tags and related
posts.

Like `blog-test`, the service lives beside the library, outside this repository:

```
~/workarea/
├── blog-content/   the client library, from page 2
├── blog-test/      the small program, from page 2
└── blog-api/       the service, from this page
```

## 1. Copy the starter

From the folder you cloned the samples into:

```bash
cp -R coho-samples/kotlin/ktor-blog-starter ~/workarea/blog-api
```

Here is what it holds. The arrows mark where the repeaters go:

```
blog-api/
├── build.gradle.kts                   the service's packages: Ktor, kotlinx.serialization, CommonMark
├── src/main/kotlin/com/example/blog/
│   ├── Application.kt                 the app: its routes, and the Coho client they read through
│   ├── Site.kt                        the site's name, markdown as HTML, and dates as ISO 8601
│   ├── Posts.kt                       the latest posts                    ← a repeater
│   │                                  a post, with its author and tags    ← two repeaters
│   └── Api.kt                         what the API answers with
└── .env.example                       the values the service reads
```

## 2. Add the library

While you develop, the service builds the library from its folder, as `blog-test` does:

```bash
cd ~/workarea/blog-api
```

Add the library's build to the end of `settings.gradle.kts`:

```kotlin
// Your content library, built from its folder.
includeBuild("../blog-content")
```

and the library to the `dependencies` in `build.gradle.kts`:

```kotlin
    // Your content library.
    implementation("com.yourorg.blogcontent:blog-content")
```

The service builds the library with its own code, so a regenerated library is in the service
the next time it starts, with nothing to publish. When the library is published to a Maven
repository, the `includeBuild` line goes, the dependency gets a version, and nothing else in
the service changes.

The starter imports the library's classes from `com.yourorg.blogcontent.coho`, the package
from page 2. If you gave the library another, change `com.yourorg.blogcontent` in the
starter's `src` to yours.

## 3. Say where dev is

The service reads the same values as `blog-test`: where `dev`'s content is, and the token to
read it with. Copy `blog-test`'s `.env`:

```bash
cp ../blog-test/.env .env
```

The starter's `.gitignore` already keeps `.env` out of git, and its `run` task reads it, as
`blog-test`'s does. Its `.env.example` lists the values, for whoever sets the service up next.

Sharing `blog-test`'s token is fine while you try things out. A real service gets a token of
its own, so each can be revoked without breaking the other. Create one with
`coho token create --role viewer --label "blog-api preview"`, and put it in `.env` as
`COHO_PREVIEW_TOKEN`.

The client is made once, when the service starts, in `Application.kt`:

```kotlin
val coho = Coho(CohoEnvironment.fromEnvironment())
```

and handed to the routes, `posts(coho)`. The service runs on the server, so the token never
reaches whoever calls it.

## 4. Run it

```bash
./gradlew run
```

Gradle builds the library and the service, and Ktor starts on port 8080. Ask for the posts:

```bash
curl -s http://localhost:8080/posts
```

```json
[]
```

The route reads the posts, and nothing puts them in its answer yet. That is what the
repeaters are for.

## 5. List the posts

A repeater builds the same thing for each item of a list. In Kotlin, it is a `map` over the
list. Each route already reads its content, and marks the place for each repeater with a
`Repeater:` comment.

Open `Posts.kt`. The `/posts` route reads the posts, newest first:

```kotlin
// Newest first. Depth 1 brings each post's author and tags in the same request.
val posts = coho.blogPost.listAsync(ListOptions(order = BlogPost.SortBy.PublishedAt.descending, depth = 1)).await()
```

Each read has a blocking form, `list`, and an `Async` one, which returns a
`CompletableFuture`. A Ktor route is a coroutine, so it calls the `Async` one and `await`s it,
which leaves the thread free for other requests while Coho answers.

Replace the `Repeater:` comment, and the `call.respond(…)` under it, with a summary of each
post:

```kotlin
call.respond(posts.items.map { summary(it) })
```

Stop the service with Ctrl+C, and run `./gradlew run` again: Ktor runs the code it was started
with. Ask for the posts again: both are there, each with its date, its author and its
summary. The roundabout post has `"featured": true`.

`summary`, further down the file, shows how a post's author is read: the post was read with
`depth = 1`, so `post.author?.value` is the team member itself.

## 6. Give a post's tags and related posts

Ask for a post:

```bash
curl -s http://localhost:8080/posts/elm-street-drainage
```

It has its title, its author with a short bio, and its body, both as the markdown it was
written in and as HTML. Its `tags` and `related` are empty. The `/posts/{slug}` route reads
the post by its slug, again with depth 1, so its tags and related posts come in the same
request.

Replace the first `Repeater:` comment, and the `tags = emptyList(),` under it, with the name
of each tag:

```kotlin
                tags = post.tags.resolved().map { it.name },
```

Replace the second, and `related = emptyList(),`, with a link to each related post:

```kotlin
                related = post.related.resolved().map { link(it) },
```

`resolved` comes from the delivery runtime. Add it to the imports at the top of the file:

```kotlin
import com.cohocms.delivery.resolved
```

Restart the service. The Elm Street post now has the Drainage and Project notes tags, and
links to the roundabout post. The roundabout post has no related posts, so its `related` is
empty.

`resolved` is there because a reference is not always an entry. `post.tags` is a list of
`Linked<Tag>`: each is the tag, or a stub Coho could not follow, such as a link to a deleted
tag. `resolved()` leaves the stubs out, and gives you the tags themselves.

## 7. Let the types catch a mistake

The types come from the library, so the compiler knows every field. In the tags repeater,
change `it.name` to `it.nmae`. Your editor marks it straight away, and a build fails:

```bash
./gradlew build
```

```
e: …/Posts.kt:49:54 Unresolved reference 'nmae' on receiver of type 'Tag'.
```

The same goes for a field removed from a content type: once the library is regenerated
without it, every read of it fails the service's build, not a request in production. Change
it back to `it.name`.

## 8. When the library changes

The service builds the library from its folder, so a change to the library reaches the
service with nothing to install. Regenerate the library, for example because a content type
changed, then restart the service: `run` builds the new library with it.

## Where to go from here

- **Make it yours.** The site's name is in `Site.kt`, and what the API answers with is in
  `Api.kt`. The service answers with classes of its own, rather than the library's, so its
  shape changes only when you change it, not whenever a content type does. A post's
  `layout` says how wide a front end should show it: `wide` and `landing` are wider.
- **Read more content** through `coho` in a route. An author route, for example, would read
  `coho.teamMember.bySlugAsync(slug).await()`.
- **Publish it.** A published service reads released content with a delivery key, rather
  than `dev` with a token, set as the host's environment variables rather than a `.env`
  file, and runs from what `./gradlew installDist` builds. The client caches what delivery
  sends as long as delivery says it may. That is a later tutorial.

## If something goes wrong

- **`Unresolved reference 'yourorg'`:** the library is not added (step 2), it has no generated
  code yet, or it has another package: run page 2's step 3, or change the package in the
  starter's imports.
- **`Could not find com.yourorg.blogcontent:blog-content`:** check the `includeBuild` line in
  `settings.gradle.kts`, and that the library's folder is `../blog-content`.
- **The service fails to start with `Coho: COHO_DELIVERY_URL, COHO_PROJECT, COHO_REF are
  needed to read released content`:** it saw none of the values. Check that `.env` is in
  `blog-api` (step 3), and run the service with `./gradlew run`, which reads it.
- **`COHO_DELIVERY_URL is needed to read released content`:** no preview token reached the
  service, so it took the run for a release. Check `COHO_PREVIEW_TOKEN` in `.env`.
- **`COHO_ACCOUNT, COHO_PROJECT are needed to read a preview`:** add them to `.env`
  (step 3).
- **A route answers `502` with `UNAUTHENTICATED` or `PROJECT_NOT_FOUND`:** the token is
  wrong, expired or revoked, or for another project. Also check `COHO_ACCOUNT` and
  `COHO_PROJECT`. The service answers `502` whenever Coho refuses a read, with Coho's code.
- **The posts are an empty list, and no error:** check the repeater in the `/posts` route
  (step 5), and that you restarted the service. If it is there, check that `dev` has posts:
  `./gradlew catalog --args=--preview` in `blog-content`.
- **`Address already in use`:** another copy of the service is still running. Stop it, or run
  on another port: `PORT=8081 ./gradlew run`.

Next: [Images and downloads](04_IMAGES_AND_ASSETS.md).
