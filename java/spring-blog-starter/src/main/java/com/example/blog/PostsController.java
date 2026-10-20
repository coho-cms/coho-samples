package com.example.blog;

import com.cohocms.delivery.ListOptions;
import com.cohocms.delivery.ReadOptions;
import com.example.blog.api.Api.AuthorOut;
import com.example.blog.api.Api.PostLink;
import com.example.blog.api.Api.PostOut;
import com.example.blog.api.Api.PostSummary;
import com.example.blog.api.Api.SiteInfo;
import com.yourorg.blogcontent.coho.BlogPost;
import com.yourorg.blogcontent.coho.Coho;
import com.yourorg.blogcontent.coho.TeamMember;
import java.util.List;
import org.jspecify.annotations.Nullable;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/** The site's front page, and its posts: the latest, and one by its slug, with its author and tags. */
@RestController
public class PostsController
{
    private final Coho coho;

    public PostsController(Coho coho)
    {
        this.coho = coho;
    }

    /** The site's name, and where its posts are. */
    @GetMapping("/")
    public SiteInfo frontPage()
    {
        return new SiteInfo(Site.NAME, "/posts", "/swagger-ui.html");
    }

    /** The latest posts, newest first. */
    @GetMapping("/posts")
    public List<PostSummary> latestPosts()
    {
        // Newest first. Depth 1 brings each post's author and tags in the same request.
        var posts = coho.blogPost().list(
            new ListOptions<BlogPost.SortBy>().withOrder(BlogPost.SortBy.PUBLISHED_AT.descending()).withDepth(1));

        // Repeater: a summary(post) for each post in posts.getItems().
        return List.of();
    }

    /** A post, with its author, tags and related posts. */
    @GetMapping("/posts/{slug}")
    public PostOut post(@PathVariable String slug)
    {
        // Depth 1 brings the post's author, tags and related posts in the same request.
        BlogPost post = coho.blogPost().bySlug(slug, ReadOptions.depth(1));
        if (post == null)
        {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "There is no post '" + slug + "'.");
        }

        return new PostOut(
            post.getSlug(),
            post.getTitle(),
            post.getSummary(),
            post.getSeoDescription() != null ? post.getSeoDescription() : post.getSummary(),
            post.getPublishedAt(),
            post.getLayout(),
            post.getReadingMinutes(),
            author(post),
            // Repeater: the name of each tag in post.getTags().
            List.of(),
            post.getBody(),
            Site.markdown(post.getBody()),
            // Repeater: a link(related) to each post in post.getRelated().
            List.of());
    }

    /** One post in a list. */
    private static PostSummary summary(BlogPost post)
    {
        // A post read with depth 1 has its author. Without it, the author is only a link.
        TeamMember writer = writer(post);
        return new PostSummary(
            post.getSlug(),
            "/posts/" + post.getSlug(),
            post.getTitle(),
            post.getSummary(),
            post.getPublishedAt(),
            writer != null ? writer.getFullName() : null,
            Boolean.TRUE.equals(post.getFeatured()));
    }

    /** A link to a post. */
    private static PostLink link(BlogPost post)
    {
        return new PostLink(post.getSlug(), "/posts/" + post.getSlug(), post.getTitle());
    }

    /** The team member a post links to as its author, if it has one and it was read. */
    private static @Nullable AuthorOut author(BlogPost post)
    {
        TeamMember writer = writer(post);
        if (writer == null)
        {
            return null;
        }
        return new AuthorOut(writer.getSlug(), writer.getFullName(), writer.getTitle(), Site.markdown(writer.getBio()));
    }

    /** The post's author: null when it has none, or when Coho could not follow the link. */
    private static @Nullable TeamMember writer(BlogPost post)
    {
        return post.getAuthor() != null ? post.getAuthor().getValue() : null;
    }
}
