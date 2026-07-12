# whitechno.github.io

Personal site and blog of Oleg White ([whitechno](https://github.com/whitechno)),
live at <https://whitechno.github.io/>.

Built with Jekyll on the stock GitHub Pages build — no theme, no plugins,
no JavaScript. Pushing to `main` publishes the site.

## Adding a post

Create a folder per post — date path plus a title slug — with images alongside:

```
blog/YYYY/MM/DD/post-title-slug/
├── index.md      # front matter: layout: post, title, date
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
---
```

Any page under `blog/` with a `date` appears automatically in the post list
on the landing page.

## Importing a report from dag-docs-pub

Posts are first written as reports in
`dag/dag-docs-pub/docs/reports/YYYY/MM/DD/<slug>.md` (setext title, a
`Month D, YYYY` date line, assets alongside). `_scripts/import_post.py`
copies and transforms one into a post folder:

```bash
python3 _scripts/import_post.py 2026/07/01/vector-search-libraries-summary.md \
  --description "One-sentence description for the meta tag."
```

It converts the title/date header to front matter, keeps an
"*Updated ...*" note, copies all sibling assets, and rewrites relative
cross-report links for the blog tree. Use `--dry-run` to preview and
`--force` to overwrite. Then review, `git add`, commit, push.
