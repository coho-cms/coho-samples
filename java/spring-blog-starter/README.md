# Spring Boot blog starter

A Spring Boot web service for a blog, ready to read its posts from Coho and answer with JSON.
The routes, the response records and the reads are done. What is left is yours: your content
library, and the repeaters that build each list of posts, tags and related posts.

It is built for the content model in [cli-spring-blog](../cli-spring-blog/README.md), with
the `blogPost`, `teamMember` and `tag` types, and the client library from
[Create the client library](../cli-spring-blog/02_CLIENT_LIBRARY.md).
[Build the Spring Boot service](../cli-spring-blog/03_APPLICATION.md) walks through setting
it up, step by step.

```
spring-blog-starter/
├── build.gradle.kts                 the service's packages: Spring Boot, springdoc, CommonMark
├── src/main/java/com/example/blog/
│   ├── BlogApplication.java         the app
│   ├── CohoConfiguration.java       the Coho client, and what a refusal from Coho answers
│   ├── Site.java                    the site's name, and markdown as HTML
│   ├── PostsController.java         the latest posts                    ← a repeater
│   │                                a post, with its author and tags    ← two repeaters
│   └── api/Api.java                 what the API answers with
└── .env.example                     the values the service reads
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
4. `./gradlew bootRun`, and open http://localhost:8080/swagger-ui.html.
5. Replace each `Repeater:` comment in `PostsController.java`, and the empty list under it,
   with a stream over its list. The tutorial has the code for each.

The service builds the library from its folder, so a regenerated library is in the service
the next time it starts, with nothing to publish. When the library is published, the
`includeBuild` line goes and the dependency gets a version.
