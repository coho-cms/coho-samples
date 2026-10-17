import { PostCard } from '@/components/post-card';
import { coho } from '@/lib/coho';

export default async function HomePage() {
  // Newest first. depth: 1 brings each post's author and tags in the same request.
  const posts = await coho.blogPost.list({ order: '-publishedAt', depth: 1 });

  return (
    <>
      <h1 className="page-title">Latest posts</h1>
      <ul className="post-list">
        {/* Repeater: an <li> with a <PostCard> for each post in posts.items. */}
      </ul>
    </>
  );
}
