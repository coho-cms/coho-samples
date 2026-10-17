import type { Metadata } from 'next';
import Link from 'next/link';
import type { ReactNode } from 'react';
import { locale, siteName } from '@/lib/site';
import './globals.css';

export const metadata: Metadata = {
  title: { default: siteName, template: `%s · ${siteName}` },
  description: 'Notes from our work, published with Coho.',
};

// In production, a page is rendered again with fresh content at most once a minute.
// `npm run dev` renders on every request, so it always shows the latest.
export const revalidate = 60;

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang={locale}>
      <body>
        <header className="site-header">
          <Link href="/" className="site-name">
            {siteName}
          </Link>
        </header>
        <main className="site-main">{children}</main>
        <footer className="site-footer">Published with Coho.</footer>
      </body>
    </html>
  );
}
