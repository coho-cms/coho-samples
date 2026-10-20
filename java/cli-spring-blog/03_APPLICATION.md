# 3. Build the Spring Boot service

This page wires the client library into a Spring Boot web service for the blog. Its routes
list the blog posts, and give each post with its author and tags, as JSON, all through the
library's typed reads. The types catch a misspelled field or a missing reference while you
build, before the service ever calls Coho.

You need the client library from [Create the client library](02_CLIENT_LIBRARY.md), with
its code generated. The service brings its own settings and token: the library's `.env` only
holds the token `cohoPull` uses, and never goes with it.

The service starts from [spring-blog-starter](../spring-blog-starter/README.md), a Spring Boot
app whose routes, response records and reads are already written. This page adds the two
things that are yours: the library, and the repeaters that build each list of posts, tags
and related posts.

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
cp -R coho-samples/java/spring-blog-starter ~/workarea/blog-api
```

Here is what it holds. The arrows mark where the repeaters go:

```
blog-api/
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

The starter's `.gitignore` already keeps `.env` out of git, and its `bootRun` task reads it,
as `blog-test`'s `run` does. Its `.env.example` lists the values, for whoever sets the service
up next.

Sharing `blog-test`'s token is fine while you try things out. A real service gets a token of
its own, so each can be revoked without breaking the other. Create one with
`coho token create --role viewer --label "blog-api preview"`, and put it in `.env` as
`COHO_PREVIEW_TOKEN`.

The client is made once, as a Spring bean, in `CohoConfiguration.java`:

```java
@Bean
public Coho coho(Environment environment)
{
    return new Coho(CohoEnvironment.from(environment::getProperty));
}
```

It reads the `COHO_*` values from Spring's `Environment`, so they can come from environment
variables, `application.properties` or anything else Spring reads. Each controller asks for
the client in its constructor. The service runs on the server, so the token never reaches
whoever calls it.

## 4. Run it

```bash
./gradlew bootRun
```

Gradle builds the library and the service, and Spring Boot starts on port 8080. Open
http://localhost:8080/swagger-ui.html. springdoc lists every route there, with what it
answers, and **Try it out** calls it.

Ask for the posts, there or with `curl`:

```bash
curl -s http://localhost:8080/posts
```

```json
[]
```

The route reads the posts, and nothing puts them in its answer yet. That is what the
repeaters are for.

## 5. List the posts

A repeater builds the same thing for each item of a list. In Java, it is a stream over the
list, mapped to what the API answers with. Each route already reads its content, and marks
the place for each repeater with a `Repeater:` comment.

Open `PostsController.java`. `latestPosts` reads the posts, newest first:

```java
// Newest first. Depth 1 brings each post's author and tags in the same request.
var posts = coho.blogPost().list(
    new ListOptions<BlogPost.SortBy>().withOrder(BlogPost.SortBy.PUBLISHED_AT.descending()).withDepth(1));
```

Replace the `Repeater:` comment, and the `return List.of();` under it, with a summary of each
post:

```java
return posts.getItems().stream().map(post -> summary(post)).toList();
```

Stop the service with Ctrl+C, and run `./gradlew bootRun` again: Spring Boot runs the code it
was started with. Ask for the posts again: both are there, each with its date, its author
and its summary. The roundabout post has `"featured": true`.

`summary`, further down the file, shows how a post's author is read: the post was read with
`withDepth(1)`, so `post.getAuthor().getValue()` is the team member itself.

## 6. Give a post's tags and related posts

Ask for a post:

```bash
curl -s http://localhost:8080/posts/elm-street-drainage
```

It has its title, its author with a short bio, and its body, both as the markdown it was
written in and as HTML. Its `tags` and `related` are empty. The `post` route reads the post
by its slug, again with depth 1, so its tags and related posts come in the same request.

In `post`, replace the first `Repeater:` comment, and the `List.of(),` under it, with the
name of each tag:

```java
            Linked.resolved(post.getTags()).stream().map(tag -> tag.getName()).toList(),
```

Replace the second, and the `List.of());` under it, with a link to each related post:

```java
            Linked.resolved(post.getRelated()).stream().map(related -> link(related)).toList());
```

`Linked` comes from the delivery runtime. Add it to the imports at the top of the file:

```java
import com.cohocms.delivery.Linked;
```

Restart the service. The Elm Street post now has the Drainage and Project notes tags, and
links to the roundabout post. The roundabout post has no related posts, so its `related` is
empty.

`Linked.resolved` is there because a reference is not always an entry. `post.getTags()` is a
list of `Linked<Tag>`: each is the tag, or a stub Coho could not follow, such as a link to a
deleted tag. `Linked.resolved` leaves the stubs out, and gives you the tags themselves.

## 7. Let the types catch a mistake

The types come from the library, so the compiler knows every field. In the tags repeater,
change `tag.getName()` to `tag.getNmae()`. Your editor marks it straight away, and a build
fails:

```bash
./gradlew build
```

```
PostsController.java:71: error: cannot find symbol
            Linked.resolved(post.getTags()).stream().map(tag -> tag.getNmae()).toList(),
                                                                   ^
  symbol:   method getNmae()
  location: variable tag of type Tag
```

The same goes for a field removed from a content type: once the library is regenerated
without it, every read of it fails the service's build, not a request in production. Change
it back to `tag.getName()`.

## 8. When the library changes

The service builds the library from its folder, so a change to the library reaches the
service with nothing to install. Regenerate the library, for example because a content type
changed, then restart the service: `bootRun` builds the new library with it.

## Where to go from here

- **Make it yours.** The site's name is in `Site.java`, and what the API answers with is in
  `api/Api.java`. The service answers with records of its own, rather than the library's
  classes, so its shape changes only when you change it, not whenever a content type does.
  A post's `layout` says how wide a front end should show it: `wide` and `landing` are wider.
- **Read more content** through `coho` in a controller. An author route, for example, would
  read `coho.teamMember().bySlug(slug)`.
- **Publish it.** A published service reads released content with a delivery key, rather
  than `dev` with a token, set as the host's environment variables rather than a `.env`
  file, and runs from the jar `./gradlew bootJar` builds. The client caches what delivery
  sends as long as delivery says it may. That is a later tutorial.

## If something goes wrong

- **`package com.yourorg.blogcontent.coho does not exist`:** the library is not added (step
  2), it has no generated code yet, or it has another package: run page 2's step 3, or change
  the package in the starter's imports.
- **`Could not find com.yourorg.blogcontent:blog-content`:** check the `includeBuild` line in
  `settings.gradle.kts`, and that the library's folder is `../blog-content`.
- **The service fails to start with `Coho: COHO_DELIVERY_URL, COHO_PROJECT, COHO_REF are
  needed to read released content`:** it saw none of the values. Check that `.env` is in
  `blog-api` (step 3), and run the service with `./gradlew bootRun`, which reads it.
- **`COHO_DELIVERY_URL is needed to read released content`:** no preview token reached the
  service, so it took the run for a release. Check `COHO_PREVIEW_TOKEN` in `.env`.
- **`COHO_ACCOUNT, COHO_PROJECT are needed to read a preview`:** add them to `.env`
  (step 3).
- **A route answers `502` with `UNAUTHENTICATED` or `PROJECT_NOT_FOUND`:** the token is
  wrong, expired or revoked, or for another project. Also check `COHO_ACCOUNT` and
  `COHO_PROJECT`. The service answers `502` whenever Coho refuses a read, with Coho's code.
- **The posts are an empty list, and no error:** check the repeater in `latestPosts`
  (step 5), and that you restarted the service. If it is there, check that `dev` has posts:
  `./gradlew catalog --args=--preview` in `blog-content`.
- **`Port 8080 was already in use`:** another copy of the service is still running. Stop it,
  or run on another port: `./gradlew bootRun --args='--server.port=8081'`.

Next: [Images and downloads](04_IMAGES_AND_ASSETS.md).
