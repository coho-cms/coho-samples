import Link from 'next/link';
import { isResolved, type BlogPost } from '@/lib/coho';
import { formatDate } from '@/lib/site';

/** One post in a list: its date, author, title and summary, linking to the post. */
export function PostCard({ post }: { post: BlogPost }) {
    // A post read with depth: 1 has its author. Without it, the author is only a link.
    const author = post.author && isResolved(post.author) ? post.author : undefined;

    return (
        <article className="post-card">
            <p className="meta">
                <time dateTime={post.publishedAt}>{formatDate(post.publishedAt)}</time>
                {author && <> · {author.fullName}</>}
                {post.featured && <span className="badge">Featured</span>}
            </p>
            <h2>
                <Link href={`/posts/${post._slug}`}>{post.title}</Link>
            </h2>
            {post.summary && <p>{post.summary}</p>}
        </article>
    );
}
