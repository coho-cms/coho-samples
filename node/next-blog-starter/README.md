# Next.js blog starter

A Next.js blog, ready to read its posts from Coho. The layout, the styles, the pages and
the reads are done. What is left is yours: the reference to your content library, and the
repeaters that show each post, tag and related post on the page.

It is built for the content model in [cli-next-blog](../cli-next-blog/README.md), with the
`blogPost`, `teamMember` and `tag` types. You need the client library from
[Create the client library](../cli-next-blog/02_CLIENT_LIBRARY.md), built, with its types
generated from `dev`.

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

## 1. Copy the starter

Copy it beside your library, the way `blog-try` is, so it finds the library at
`../blog-content`. From the folder you cloned the samples into:

```bash
cp -R coho-samples/node/next-blog-starter ~/workarea/blog-site
```

```bash
cd ~/workarea/blog-site
```

## 2. Add your library

Install the library from its folder. This adds it to `package.json`, and installs
everything else the site needs:

```bash
npm install ../blog-content
```

`package.json` now has the reference:

```json
"@your-org/blog-content": "file:../blog-content",
```

The site imports the library in one place, `lib/coho.ts`. If yours has another name than
`@your-org/blog-content`, change it there.

The library is linked, not copied, so when you regenerate and rebuild it, the site has the
change. Next.js follows the link because `next.config.ts` names `../blog-content` as a root
it may read; if your library is somewhere else, change the path there too. When the dev
server starts, it lists this setting under `Experiments`. That is expected.

## 3. Say where dev is

`.env.development` says where `dev`'s content is, for `npm run dev`. It holds no secret,
so it is committed. Fill in `COHO_ACCOUNT` and `COHO_PROJECT` from `coho status`, or copy
them from the `.env.dev` you made for `blog-try`.

The site also needs a project token, and that is a secret. Create one for the site:

```bash
coho token create --role viewer --label "blog-site preview"
```

Save it in `.env.local`, which Next.js reads and git ignores:

```
COHO_PREVIEW_TOKEN=<preview-token>
```

Never give it a `NEXT_PUBLIC_` prefix: that would put it in every visitor's browser.
`lib/coho.ts` imports `server-only`, so only server components can read content.

## 4. Run it

```bash
npm run dev
```

It lists the files it read the environment from: `.env.local, .env.development`. Open
http://localhost:3000. You see the header and **Latest posts**, but no posts: the page
reads them, and nothing shows them yet. That is the next step.

## 5. Add the repeaters

A repeater shows each item of a list with the same markup. In React, it is a `.map()`
over the list. Each page already reads its content, and marks the place for each repeater
with a `Repeater:` comment. Replace each comment with the code below. The page reloads as
you save.

**The latest posts**, in `app/page.tsx`. `posts.items` holds the posts in the order Coho
returned them, newest first. A `<PostCard>` shows each one:

```tsx
{posts.items.map((post) => (
  <li key={post._id}>
    <PostCard post={post} />
  </li>
))}
```

**A post's tags**, in `app/posts/[slug]/page.tsx`. The post is read with `depth: 1`, so
`post.tags` holds the tags themselves. A reference Coho could not follow, such as one to a
deleted tag, is a stub, `{ _id, _unresolved }`, and `isResolved` leaves those out:

```tsx
{post.tags?.filter(isResolved).map((tag) => (
  <li key={tag._id}>{tag.name}</li>
))}
```

**Related posts**, in the same file, the same way:

```tsx
{post.related?.filter(isResolved).map((related) => (
  <li key={related._id}>
    <Link href={`/posts/${related._slug}`}>{related.title}</Link>
  </li>
))}
```

`key` tells React which item is which when a list changes, so it is the entry's `_id`,
which never changes. `_slug` is what each post's address is built from.

The types come from your library, so a misspelled field such as `tag.nmae` is an error in
your editor, and `npm run build` fails on it.

## Where to go from here

- **Make it yours.** The site's name is in `lib/site.ts`, and the styles are in
  `app/globals.css`. A post's `layout` field sets its width: `wide` and `landing` are wider.
- **Read more content** through `coho` in `lib/coho.ts`. An author page, for example,
  would read `coho.teamMember.bySlug(slug)`.
- **Publish it.** `npm run build` renders every post ahead of time, and in production a
  page is rendered again at most once a minute (`revalidate`, in `app/layout.tsx`). A
  published site reads released content with a delivery key, rather than `dev` with a
  token. That is a later tutorial.

## If something goes wrong

- **`Module not found: Can't resolve '@your-org/blog-content'`:** the library is not in
  `package.json` (step 2), or it is not at `../blog-content` (check the path in
  `next.config.ts`), or it is not built (run `npm run build` in `blog-content`). If it has
  another name, change it in `lib/coho.ts`.
- **`COHO_DELIVERY_URL is needed to read released content`:** no preview token reached the
  environment, so the site took the run for a release. Check `COHO_PREVIEW_TOKEN` in
  `.env.local`, then restart `npm run dev`.
- **`COHO_ACCOUNT, COHO_PROJECT are needed to read a preview`:** fill them in in
  `.env.development` (step 3).
- **`UNAUTHENTICATED` or `PROJECT_NOT_FOUND`:** the token is wrong, expired or revoked, or
  for another project. Also check `COHO_ACCOUNT` and `COHO_PROJECT` in `.env.development`.
- **The page shows no posts, and no error:** check the repeater in `app/page.tsx` (step 5).
  If it is there, check that `dev` has posts: `npm run catalog -- --preview` in
  `blog-content`.
- **`npm run build` asks for `COHO_` variables:** a build reads `.env.production` and
  `.env.local`, not `.env.development`. Set the variables for the content to build from.
- **A build error about `server-only`:** a component marked `'use client'` imports
  `lib/coho.ts`, directly or through another file. Read content in a server component, and
  pass the client component what it shows as props.
