# 3. Build the Next.js blog

This page wires the client library into a Next.js blog. React templates list the blog
posts, and show each post with its author and tags, all through the library's typed reads.
The types catch a misspelled field or a missing reference while you build, before the site
ever calls Coho.

You need the client library from [Create the client library](02_CLIENT_LIBRARY.md), with
its code generated. The blog brings its own settings and token: the library's `.env` only
holds the token `npm run pull` uses, and never goes with it.

The site starts from [next-blog-starter](../next-blog-starter/README.md), a Next.js app
whose layout, styles, pages and reads are already written. This page adds the two things
that are yours: the library, and the repeaters that show each post, tag and related post.

Like `blog-try`, the site lives beside the library, outside this repository:

```
~/workarea/
├── blog-content/   the client library, from page 2
├── blog-try/       the small program, from page 2
└── blog-site/      the blog, from this page
```

## 1. Copy the starter

From the folder you cloned the samples into:

```bash
cp -R coho-samples/node/next-blog-starter ~/workarea/blog-site
```

Here is what it holds. The arrows mark where the repeaters go:

```
blog-site/
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
│   ├── coho.ts                 the Coho client, and the only import of the library
│   └── site.ts                 the site's name, its locale, and how dates look
└── .env.development            where dev's content is
```

## 2. Pack the library

The site installs the library the way it will once the library is published: as a
package, not as a link to the library's folder. `npm pack` makes that package, a tarball,
in the library's folder:

```bash
cd ~/workarea/blog-content
```

```bash
npm pack
```

Before it packs, it checks that the generated code matches the type model, and builds
the library, so the tarball is never stale:

```
> @your-org/blog-content@0.1.0 prepack
> coho-codegen check && npm run build

Generated code is up to date.
…
npm notice filename: your-org-blog-content-0.1.0.tgz
```

The tarball holds what a registry would serve: `dist`, `package.json`, the README and the
license. The library's `.gitignore` keeps it out of the library's repository.

## 3. Add the library to the site

Install the tarball into the site:

```bash
cd ../blog-site
```

```bash
npm install ../blog-content/your-org-blog-content-0.1.0.tgz
```

This installs everything the site needs, and adds the library to its `package.json`:

```json
"@your-org/blog-content": "file:../blog-content/your-org-blog-content-0.1.0.tgz",
```

npm unpacks a copy of the library into `node_modules`, so the site has the library and
nothing else from its folder. When the library is published, this line becomes a version,
such as `"^0.1.0"`, and nothing else in the site changes.

The site imports the library in one file, `lib/coho.ts`. If you named it something other
than `@your-org/blog-content`, change the name there.

## 4. Say where dev is

`.env.development` says where `dev`'s content is. Next.js reads it for `npm run dev`. It
holds no secret, so a real project commits it. Fill in `COHO_ACCOUNT` and `COHO_PROJECT`
with the same ids as the `.env.local` you made for `blog-try`:

```
COHO_URL=https://api-dev.coho-cms.dev
COHO_ACCOUNT=<account-id>
COHO_PROJECT=<project-id>
COHO_REF=dev
COHO_LOCALE=en-US
```

The site also needs a project token. As with `blog-try`, create one of its own, so each
can be revoked without breaking the other:

```bash
coho token create --role viewer --label "blog-site preview"
```

A token is a secret, so it goes in `.env.local`, which Next.js also reads and the site's
`.gitignore` keeps out of git. Create it with this line:

```
COHO_PREVIEW_TOKEN=<preview-token>
```

Never give a Coho variable a `NEXT_PUBLIC_` prefix: Next.js would put it in every visitor's
browser. `lib/coho.ts` imports `server-only`, so only server components can read content.

## 5. Run it

```bash
npm run dev
```

It lists the files it read: `.env.local, .env.development`. Open http://localhost:3000.
You see the site's name and **Latest posts**, but no posts. The page reads them, and
nothing shows them yet. That is what the repeaters are for.

## 6. List the posts

A repeater shows each item of a list with the same markup. In React, it is a `.map()` over
the list. Each page already reads its content, and marks the place for each repeater with
a `Repeater:` comment.

Open `app/page.tsx`. It reads the posts, newest first:

```tsx
// Newest first. depth: 1 brings each post's author and tags in the same request.
const posts = await coho.blogPost.list({ order: '-publishedAt', depth: 1 });
```

Replace the `Repeater:` comment with a `<PostCard>` for each post:

```tsx
{posts.items.map((post) => (
  <li key={post._id}>
    <PostCard post={post} />
  </li>
))}
```

Save, and the page shows both posts, each with its date, its author and its summary. The
roundabout post is marked **Featured**.

`key` tells React which item is which when the list changes, so it is the entry's `_id`,
which never changes. `components/post-card.tsx` shows how a card reads the author: the
post was read with `depth: 1`, so `post.author` is the team member itself.

## 7. Show a post's tags and related posts

Open a post. It shows its title, its author and its body, with a box about the author.
`app/posts/[slug]/page.tsx` reads it by its slug, again with `depth: 1`, so its tags and
related posts come in the same request.

Replace the first `Repeater:` comment, under the title, with the post's tags:

```tsx
{post.tags?.filter(isResolved).map((tag) => (
  <li key={tag._id}>{tag.name}</li>
))}
```

Replace the second, under **Related posts**, with a link to each related post:

```tsx
{post.related?.filter(isResolved).map((related) => (
  <li key={related._id}>
    <Link href={`/posts/${related._slug}`}>{related.title}</Link>
  </li>
))}
```

The Elm Street post now shows the Drainage and Project notes tags, and links to the
roundabout post. The roundabout post has no related posts, so it has no **Related posts**
section.

`isResolved` is there because a reference is not always an entry. One that Coho could not
follow, such as a link to a deleted tag, comes back as a stub, `{ _id, _unresolved }`, and
`filter(isResolved)` leaves those out. It also tells TypeScript that what is left are tags.

## 8. Let the types catch a mistake

The types come from the library, so the site knows every field. In the tags repeater,
change `tag.name` to `tag.nmae`. Your editor marks it straight away, and a build fails:

```bash
npm run build
```

```
app/posts/[slug]/page.tsx(44,36): error TS2339: Property 'nmae' does not exist on type 'Tag'.
Failed to type check.
```

The same goes for a field removed from a content type: once the library is regenerated
without it, every read of it fails the site's build, not a page in production. Change it
back to `tag.name`.

## 9. When the library changes

The site has a copy of the library, so it changes only when you install a new tarball.
After you regenerate the library, for example because a content type changed, pack it
again in `blog-content`:

```bash
npm pack
```

and install the new tarball in `blog-site`:

```bash
npm install ../blog-content/your-org-blog-content-0.1.0.tgz
```

Then restart `npm run dev`. A plain `npm install` is not enough: the version is the same,
so npm sees nothing to do. If you change the library's version, the tarball's name
changes with it, and so does the line in `package.json`.

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

- **`npm pack` fails with `Generated code is out of date`:** the type model was pulled and
  the code not generated from it. Run `npm run generate` in `blog-content`, then pack again.
- **`npm install` fails with `ENOENT` for the tarball:** check its name with
  `ls ../blog-content/*.tgz`. It carries the library's name and version.
- **`Module not found: Can't resolve '@your-org/blog-content'`:** the library is not
  installed (step 3), or it has another name: change the name in `lib/coho.ts`.
- **`COHO_DELIVERY_URL is needed to read released content`:** no preview token reached the
  environment, so the site took the run for a release. Check `COHO_PREVIEW_TOKEN` in
  `.env.local`, then restart `npm run dev`.
- **`COHO_ACCOUNT, COHO_PROJECT are needed to read a preview`:** fill them in in
  `.env.development` (step 4).
- **`UNAUTHENTICATED` or `PROJECT_NOT_FOUND`:** the token is wrong, expired or revoked, or
  for another project. Also check `COHO_ACCOUNT` and `COHO_PROJECT` in `.env.development`.
- **The page shows no posts, and no error:** check the repeater in `app/page.tsx` (step 6).
  If it is there, check that `dev` has posts: `npm run catalog -- --preview` in
  `blog-content`.
- **The site still shows the old library after a change:** install the new tarball by its
  path, as in step 9, not with a plain `npm install`, and restart `npm run dev`.
- **`npm run build` asks for `COHO_` variables:** a build reads `.env.production` and
  `.env.local`, not `.env.development`. Set the variables for the content to build from.
- **A build error about `server-only`:** a component marked `'use client'` imports
  `lib/coho.ts`, directly or through another file. Read content in a server component, and
  pass the client component what it shows as props.
