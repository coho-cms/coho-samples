"""The posts: the latest, and one by its slug, with its author and tags."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app import site
from app.content import BlogPost, TeamMember
from app.dependencies import Coho
from app.schemas import AuthorOut, PostLink, PostOut, PostSummary

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("")
async def latest_posts(coho: Coho) -> list[PostSummary]:
    """The latest posts, newest first."""
    # Newest first. Depth 1 brings each post's author and tags in the same request.
    posts = await coho.blog_post.list(order="-publishedAt", depth=1)

    # Repeater: a summary(post) for each post in posts.items.
    return []


@router.get("/{slug}")
async def post(slug: str, coho: Coho) -> PostOut:
    """A post, with its author, tags and related posts."""
    # Depth 1 brings the post's author, tags and related posts in the same request.
    post = await coho.blog_post.by_slug(slug, depth=1)
    if post is None:
        raise HTTPException(status_code=404, detail=f"There is no post '{slug}'.")

    return PostOut(
        slug=post.slug,
        title=post.title,
        summary=post.summary,
        description=post.seo_description or post.summary,
        published_at=post.published_at,
        layout=post.layout,
        reading_minutes=post.reading_minutes,
        author=author(post),
        # Repeater: the name of each tag in post.tags.
        tags=[],
        body=post.body,
        body_html=site.markdown(post.body),
        # Repeater: a link(related) to each post in post.related.
        related=[],
    )


def summary(post: BlogPost) -> PostSummary:
    """One post in a list."""
    # A post read with depth 1 has its author. Without it, the author is only a link.
    writer = post.author if isinstance(post.author, TeamMember) else None
    return PostSummary(
        slug=post.slug,
        url=f"/posts/{post.slug}",
        title=post.title,
        summary=post.summary,
        published_at=post.published_at,
        author=writer.full_name if writer is not None else None,
        featured=post.featured is True,
    )


def link(post: BlogPost) -> PostLink:
    """A link to a post."""
    return PostLink(slug=post.slug, url=f"/posts/{post.slug}", title=post.title)


def author(post: BlogPost) -> AuthorOut | None:
    """The team member a post links to as its author, if it has one and it was read."""
    writer = post.author if isinstance(post.author, TeamMember) else None
    if writer is None:
        return None
    return AuthorOut(
        slug=writer.slug,
        name=writer.full_name,
        title=writer.title,
        bio_html=site.markdown(writer.bio),
    )
