package com.example.blog

import com.cohocms.delivery.ListOptions
import com.cohocms.delivery.ReadOptions
import com.yourorg.blogcontent.coho.BlogPost
import com.yourorg.blogcontent.coho.Coho
import com.yourorg.blogcontent.coho.TeamMember
import io.ktor.http.HttpStatusCode
import io.ktor.server.response.respond
import io.ktor.server.routing.Route
import io.ktor.server.routing.get
import kotlinx.coroutines.future.await

/** The posts: the latest, and one by its slug, with its author and tags. */
fun Route.posts(coho: Coho)
{
    /** The latest posts, newest first. */
    get("/posts")
    {
        // Newest first. Depth 1 brings each post's author and tags in the same request.
        val posts = coho.blogPost.listAsync(ListOptions(order = BlogPost.SortBy.PublishedAt.descending, depth = 1)).await()

        // Repeater: a summary(post) for each post in posts.items.
        call.respond(emptyList<PostSummary>())
    }

    /** A post, with its author, tags and related posts. */
    get("/posts/{slug}")
    {
        val slug = call.parameters["slug"]!!
        // Depth 1 brings the post's author, tags and related posts in the same request.
        val post = coho.blogPost.bySlugAsync(slug, ReadOptions(depth = 1)).await()
        if (post == null)
        {
            call.respond(HttpStatusCode.NotFound, mapOf("detail" to "There is no post '$slug'."))
            return@get
        }

        call.respond(
            PostOut(
                slug = post.slug,
                title = post.title,
                summary = post.summary,
                description = post.seoDescription ?: post.summary,
                publishedAt = Site.iso(post.publishedAt),
                layout = post.layout,
                readingMinutes = post.readingMinutes,
                author = author(post),
                // Repeater: the name of each tag in post.tags.
                tags = emptyList(),
                body = post.body,
                bodyHtml = Site.markdown(post.body),
                // Repeater: a link(related) to each post in post.related.
                related = emptyList(),
            ),
        )
    }
}

/** One post in a list. */
fun summary(post: BlogPost): PostSummary
{
    // A post read with depth 1 has its author. Without it, the author is only a link.
    val writer: TeamMember? = post.author?.value
    return PostSummary(
        slug = post.slug,
        url = "/posts/${post.slug}",
        title = post.title,
        summary = post.summary,
        publishedAt = Site.iso(post.publishedAt),
        author = writer?.fullName,
        featured = post.featured == true,
    )
}

/** A link to a post. */
fun link(post: BlogPost) = PostLink(slug = post.slug, url = "/posts/${post.slug}", title = post.title)

/** The team member a post links to as its author, if it has one and it was read. */
fun author(post: BlogPost): AuthorOut?
{
    val writer = post.author?.value ?: return null
    return AuthorOut(slug = writer.slug, name = writer.fullName, title = writer.title, bioHtml = Site.markdown(writer.bio))
}
