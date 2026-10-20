package com.example.blog;

import org.commonmark.parser.Parser;
import org.commonmark.renderer.html.HtmlRenderer;
import org.jspecify.annotations.Nullable;

/** The site's name, and how a markdown field becomes HTML. */
public final class Site
{
    /** The site's name, which the API's front page shows. */
    public static final String NAME = "Field notes";

    // CommonMark, with any HTML in the text escaped rather than passed through.
    private static final Parser PARSER = Parser.builder().build();
    private static final HtmlRenderer RENDERER = HtmlRenderer.builder().escapeHtml(true).build();

    private Site()
    {
    }

    /** A markdown field, such as a post's body, as HTML. Null stays null. */
    public static @Nullable String markdown(@Nullable String text)
    {
        return text == null ? null : RENDERER.render(PARSER.parse(text));
    }
}
