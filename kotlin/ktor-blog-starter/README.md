# Ktor blog starter

A Ktor web service for a blog, ready to read its posts from Coho and answer with JSON. The
routes, the response classes and the reads are done. What is left is yours: your content
library, and the repeaters that build each list of posts, tags and related posts.

It is built for the content model in [cli-ktor-blog](../cli-ktor-blog/README.md), with the
`blogPost`, `teamMember` and `tag` types, and the client library from
[Create the client library](../cli-ktor-blog/02_CLIENT_LIBRARY.md).
[Build the Ktor service](../cli-ktor-blog/03_APPLICATION.md) walks through setting it up,
step by step.

```
ktor-blog-starter/
├── build.gradle.kts                   the service's packages: Ktor, kotlinx.serialization, CommonMark
├── src/main/kotlin/com/example/blog/
│   ├── Application.kt                 the app: its routes, and the Coho client they read through
│   ├── Site.kt                        the site's name, markdown as HTML, and dates as ISO 8601
│   ├── Posts.kt                       the latest posts                    ← a repeater
│   │                                  a post, with its author and tags    ← two repeaters
│   └── Api.kt                         what the API answers with
└── .env.example                       the values the service reads
```

## In short

You need a JDK, 21 or later.

1. Copy this folder beside your library, such as `~/workarea/blog-api` next to
   `~/workarea/blog-content`.
2. Add the library: `includeBuild("../blog-content")` at the end of `settings.gradle.kts`, and
   `implementation("com.yourorg.blogcontent:blog-content")` in `build.gradle.kts`. If your
   library has another package than `com.yourorg.blogcontent`, change it in the imports.
3. Copy `.env.example` to `.env`, which git ignores, and fill in `COHO_ACCOUNT`,
   `COHO_PROJECT` and a project token as `COHO_PREVIEW_TOKEN`. Copying `blog-test`'s is
   enough: `cp ../blog-test/.env .env`.
4. `./gradlew run`, and ask for http://localhost:8080/posts.
5. Replace each `Repeater:` comment in `Posts.kt`, and the empty list under it, with a `map`
   over its list. The tutorial has the code for each.

Each route reads with the `Async` form of a read, and `await`s it, so a request waiting on
Coho holds no thread. The service builds the library from its folder, so a regenerated
library is in the service the next time it starts, with nothing to publish.
