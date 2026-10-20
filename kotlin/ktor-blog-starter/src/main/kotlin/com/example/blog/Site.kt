package com.example.blog

import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter
import org.commonmark.parser.Parser
import org.commonmark.renderer.html.HtmlRenderer

/** The site's name, and how a markdown field becomes HTML. */
object Site
{
    /** The site's name, which the API's front page shows. */
    const val NAME = "Field notes"

    // CommonMark, with any HTML in the text escaped rather than passed through.
    private val parser = Parser.builder().build()
    private val renderer = HtmlRenderer.builder().escapeHtml(true).build()

    /** A markdown field, such as a post's body, as HTML. Null stays null. */
    fun markdown(text: String?): String? = text?.let { renderer.render(parser.parse(it)) }

    /** A date and time as ISO 8601 writes it, with its seconds and its offset: `2026-10-01T09:00:00Z`. */
    fun iso(time: OffsetDateTime): String = time.format(DateTimeFormatter.ISO_OFFSET_DATE_TIME)
}
