"""
What the API answers with. These are the service's own models, not the content library's:
the API's shape is a promise to whoever calls it, so it changes only when you change it here,
not whenever a content type does.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SiteInfo(BaseModel):
    """The front page: the site's name, and where its posts are."""

    name: str
    locale: str
    posts: str
    docs: str


class AuthorOut(BaseModel):
    """A post's author, from the team member it links to."""

    slug: str
    name: str
    title: str | None
    bio_html: str | None
    """The author's bio, as HTML."""


class PostSummary(BaseModel):
    """One post in a list: its date, author, title and summary, and where to read it."""

    slug: str
    url: str
    title: str | None
    summary: str | None
    published_at: datetime
    author: str | None
    """The author's name. None when the post has none, or it could not be read."""
    featured: bool


class PostLink(BaseModel):
    """A link to another post."""

    slug: str
    url: str
    title: str | None


class PostOut(BaseModel):
    """A post, with its author, tags and related posts."""

    slug: str
    title: str | None
    summary: str | None
    description: str | None
    """For search engines and link previews."""
    published_at: datetime
    layout: str
    reading_minutes: int | None
    author: AuthorOut | None
    tags: list[str]
    """The name of each tag."""
    body: str | None
    """The body, as the markdown it was written in."""
    body_html: str | None
    """The body, as HTML."""
    related: list[PostLink]
