package com.example.blog

import kotlinx.serialization.Serializable

// What the API answers with. These are the service's own classes, not the content library's:
// the API's shape is a promise to whoever calls it, so it changes only when you change it here,
// not whenever a content type does.

/** The front page: the site's name, and where its posts are. */
@Serializable
data class SiteInfo(val name: String, val posts: String)

/** A post's author, from the team member it links to. */
@Serializable
data class AuthorOut(val slug: String, val name: String, val title: String?, val bioHtml: String?)

/** One post in a list: its date, author, title and summary, and where to read it. */
@Serializable
data class PostSummary(
    val slug: String,
    val url: String,
    val title: String?,
    val summary: String?,
    /** An ISO 8601 date and time. */
    val publishedAt: String,
    /** The author's name. Null when the post has none, or it could not be read. */
    val author: String?,
    val featured: Boolean,
)

/** A link to another post. */
@Serializable
data class PostLink(val slug: String, val url: String, val title: String?)

/** A post, with its author, tags and related posts. */
@Serializable
data class PostOut(
    val slug: String,
    val title: String?,
    val summary: String?,
    /** For search engines and link previews. */
    val description: String?,
    val publishedAt: String,
    val layout: String,
    val readingMinutes: Long?,
    val author: AuthorOut?,
    /** The name of each tag. */
    val tags: List<String>,
    /** The body, as the markdown it was written in. */
    val body: String?,
    /** The body, as HTML. */
    val bodyHtml: String?,
    val related: List<PostLink>,
)
