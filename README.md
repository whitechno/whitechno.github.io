# whitechno.github.io

Personal site and blog of Oleg White ([whitechno](https://github.com/whitechno)),
live at <https://whitechno.github.io/>.

Built with Jekyll on the stock GitHub Pages build — no theme, no plugins,
no JavaScript. Pushing to `main` publishes the site.

## Adding a post

Create a folder per post — date path plus a title slug — with images alongside:

```
blog/YYYY/MM/DD/post-title-slug/
├── index.md      # front matter: layout: post, title, date, description
└── (images/SVGs, referenced by relative path)
```

The post's URL is the folder path, e.g.
`/blog/2026/06/30/vector-databases-summary/`.

Front matter:

```yaml
---
layout: post
title: "Post Title"
date: YYYY-MM-DD
description: One plain-text sentence on what the post covers.
---
```

Any page under `blog/` with a `date` appears automatically in the post list
on the landing page and in the Atom feed at `/feed.xml`. The `description`
becomes the page's HTML meta description — the snippet search results and
link previews show under the title — and the feed entry's summary; without
it the page falls back to the generic site-wide description.

Site maintenance — design doc, post-import tooling, instructions — lives in
the separate private repo `whitechno.github.io.dev`.
