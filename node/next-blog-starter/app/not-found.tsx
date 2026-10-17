import Link from 'next/link';

export default function NotFound() {
  return (
    <>
      <h1 className="page-title">Not found</h1>
      <p>
        There is nothing at this address. <Link href="/">See the latest posts</Link>.
      </p>
    </>
  );
}
