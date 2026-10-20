"""The site's name, its locale, and how a markdown field becomes HTML."""

from __future__ import annotations

import os

from markdown_it import MarkdownIt

NAME = "Field notes"
"""The site's name, which the API's front page and docs show."""

LOCALE = os.environ.get("COHO_LOCALE") or "en-US"
"""The locale the content is read in."""

# CommonMark, with any HTML in the text escaped rather than passed through.
_markdown = MarkdownIt("commonmark", {"html": False})


def markdown(text: str | None) -> str | None:
    """A markdown field, such as a post's body, as HTML. None stays None."""
    return _markdown.render(text) if text is not None else None
