package com.example.blog.api;

import java.time.OffsetDateTime;
import java.util.List;
import org.jspecify.annotations.Nullable;

/**
 * What the API answers with. These are the service's own records, not the content library's: the
 * API's shape is a promise to whoever calls it, so it changes only when you change it here, not
 * whenever a content type does.
 */
public final class Api
{
    private Api()
    {
    }

    /** The front page: the site's name, and where its posts are. */
    public record SiteInfo(String name, String posts, String docs)
    {
    }

    /** A post's author, from the team member it links to. */
    public record AuthorOut(String slug, String name, @Nullable String title, @Nullable String bioHtml)
    {
    }

    /**
     * One post in a list: its date, author, title and summary, and where to read it.
     *
     * @param author The author's name. Null when the post has none, or it could not be read.
     */
    public record PostSummary(
        String slug,
        String url,
        @Nullable String title,
        @Nullable String summary,
        OffsetDateTime publishedAt,
        @Nullable String author,
        boolean featured)
    {
    }

    /** A link to another post. */
    public record PostLink(String slug, String url, @Nullable String title)
    {
    }

    /**
     * A post, with its author, tags and related posts.
     *
     * @param description For search engines and link previews.
     * @param tags The name of each tag.
     * @param body The body, as the markdown it was written in.
     * @param bodyHtml The body, as HTML.
     */
    public record PostOut(
        String slug,
        @Nullable String title,
        @Nullable String summary,
        @Nullable String description,
        OffsetDateTime publishedAt,
        String layout,
        @Nullable Long readingMinutes,
        @Nullable AuthorOut author,
        List<String> tags,
        @Nullable String body,
        @Nullable String bodyHtml,
        List<PostLink> related)
    {
    }
}
