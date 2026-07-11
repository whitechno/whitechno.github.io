# whitechno.github.io

Personal site and blog of Oleg White ([whitechno](https://github.com/whitechno)),
live at <https://whitechno.github.io/>.

Built with Jekyll on the stock GitHub Pages build — no theme, no plugins,
no JavaScript. Pushing to `master` publishes the site.

## Adding a post

Create a folder per post, with images alongside:

```
blog/YYYY/MM/DD/
├── index.md      # front matter: layout: post, title, date
└── (images/SVGs, referenced by relative path)
```

Front matter:

```yaml
---
layout: post
title: "Post Title"
date: YYYY-MM-DD
---
```

Any page under `blog/` with a `date` appears automatically in the post list
on the landing page.
