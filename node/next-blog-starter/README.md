# Next.js blog starter

A Next.js blog, ready to read its posts from Coho. The layout, the styles, the pages and
the reads are done. What is left is yours: the reference to your content library, and the
repeaters that show each post, tag and related post on the page.

It is built for the content model in [cli-next-blog](../cli-next-blog/README.md), with the
`blogPost`, `teamMember` and `tag` types, and the client library from
[Create the client library](../cli-next-blog/02_CLIENT_LIBRARY.md).
[Build the Next.js blog](../cli-next-blog/03_APPLICATION.md) walks through setting it up,
step by step.

```
next-blog-starter/
├── app/
│   ├── layout.tsx              around every page: the header, the footer and the title
│   ├── page.tsx                the home page: the latest posts       ← a repeater
│   ├── posts/[slug]/page.tsx   a post, with its author and tags      ← two repeaters
│   ├── not-found.tsx           what an unknown address shows
│   └── globals.css             the styles
├── components/
│   ├── post-card.tsx           one post in a list
│   └── markdown.tsx            a markdown field, such as a post's body
├── lib/
│   ├── coho.ts                 the Coho client, and the only import of your library
│   └── site.ts                 the site's name, its locale, and how dates look
└── .env.development            where dev's content is
```

## In short

1. Copy this folder beside your library, such as `~/workarea/blog-site` next to
   `~/workarea/blog-content`.
2. Pack the library: `npm pack` in `blog-content`. It checks the generated code, builds,
   and writes a tarball such as `your-org-blog-content-0.1.0.tgz`.
3. Install it in the site: `npm install ../blog-content/your-org-blog-content-0.1.0.tgz`.
   That adds the reference to `package.json`. If your library has another name than
   `@your-org/blog-content`, change it in `lib/coho.ts`.
4. Fill in `COHO_ACCOUNT` and `COHO_PROJECT` in `.env.development`, and put a project
   token in `.env.local` as `COHO_PREVIEW_TOKEN`. Never give either a `NEXT_PUBLIC_` prefix.
5. `npm run dev`, then replace each `Repeater:` comment with a `.map()` over its list.
   The tutorial has the code for each.

After the library changes, pack it again and install the new tarball by its path, as in
step 3. A plain `npm install` keeps the copy it has.
