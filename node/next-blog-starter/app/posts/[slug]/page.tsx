import type { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { cache } from 'react';
import { Markdown } from '@/components/markdown';
import { coho, isResolved } from '@/lib/coho';
import { formatDate } from '@/lib/site';

type Props = { params: Promise<{ slug: string }> };

// depth: 1 brings the post's author, tags and related posts in the same request.
// cache() shares the one read between the page and its metadata.
const getPost = cache((slug: string) => coho.blogPost.bySlug(slug, { depth: 1 }));

// Every post is rendered at build time. One published later renders on its first visit.
export async function generateStaticParams() {
    const posts = await coho.blogPost.list();
    return posts.items.map((post) => ({ slug: post._slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const post = await getPost((await params).slug);
    if (post === null) return {};
    return { title: post.title, description: post.seoDescription ?? post.summary };
}

export default async function PostPage({ params }: Props) {
    const post = await getPost((await params).slug);
    if (post === null) notFound();

    const author = post.author && isResolved(post.author) ? post.author : undefined;

    return (
        <article className="post" data-layout={post.layout}>
            <header>
                <h1>{post.title}</h1>
                <p className="meta">
                    <time dateTime={post.publishedAt}>{formatDate(post.publishedAt)}</time>
                    {author && <> · {author.fullName}</>}
                    {post.readingMinutes !== undefined && <> · {post.readingMinutes} min read</>}
                </p>
                <ul className="tags">
                    {/* Repeater: an <li> with the name of each tag in post.tags. */}
                </ul>
            </header>

            <Markdown>{post.body}</Markdown>

            {author && (
                <aside className="author">
                    <h2>{author.fullName}</h2>
                    {author.title && <p className="meta">{author.title}</p>}
                    <Markdown>{author.bio}</Markdown>
                </aside>
            )}

            {post.related && post.related.length > 0 && (
                <section className="related">
                    <h2>Related posts</h2>
                    <ul>
                        {/* Repeater: an <li> linking to each post in post.related. */}
                    </ul>
                </section>
            )}
        </article>
    );
}
