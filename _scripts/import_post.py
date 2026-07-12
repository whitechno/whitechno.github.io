#!/usr/bin/env python3
"""Import a report from dag-docs-pub into the blog.

Copies and transforms a report written under
    <reports>/YYYY/MM/DD/<slug>.md          (+ sibling assets: SVGs, logos/, ...)
into a Jekyll page at
    <site>/blog/YYYY/MM/DD/<slug>/index.md  (+ the same assets, copied verbatim)

Transformation rules (see design-whitechno-github-io.md in dag-cv-white):
  1. The setext header (title line, ==== line, date line) becomes YAML front
     matter: layout: post, title, date (ISO), description.
  2. "Month D, YYYY (Updated Month D, YYYY)" keeps the update as an
     "*Updated Month D, YYYY*" line at the top of the body.
  3. Markdown links wrapped right after "](" are joined so the URL follows
     "](" directly (kramdown may not parse a newline there).
  4. Relative links into OTHER report day-dirs are re-resolved for the blog
     tree, where each post lives one level deeper (its slug folder):
       ../../MM/DD/other-slug.md   ->  ../../../MM/DD/other-slug/
       ../../MM/DD/asset.svg       ->  ../../../MM/DD/other-slug/asset.svg
  5. Same-folder relative links (logos/x.svg, infographic.svg) pass through
     unchanged, as do absolute http(s) links.

Usage:
    _scripts/import_post.py 2026/07/01/vector-search-libraries-summary.md \
        [--description "..."] [--dry-run] [--force]

The report path may be absolute or relative to the reports root
(default: ../dag/dag-docs-pub/docs/reports relative to the site repo,
override with --reports-root or $REPORTS_ROOT).
"""

import argparse
import re
import shutil
import sys
from datetime import datetime
from os.path import relpath
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORTS_ROOT = (
    SITE_ROOT.parent / "dag" / "dag-docs-pub" / "docs" / "reports"
)

DATE_LINE_RE = re.compile(
    r"^(?P<date>[A-Z][a-z]+ \d{1,2}, \d{4})"
    r"(?: \(Updated (?P<updated>[A-Z][a-z]+ \d{1,2}, \d{4})\))?\s*$"
)
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")


def die(msg):
    sys.exit(f"error: {msg}")


def parse_header(text, path):
    """Split source into (title, date, updated-or-None, body)."""
    lines = text.split("\n")
    if len(lines) < 4 or not re.fullmatch(r"=+\s*", lines[1]):
        die(f"{path}: expected setext header (title, ====, date line)")
    m = DATE_LINE_RE.match(lines[2])
    if not m:
        die(f"{path}: line 3 is not 'Month D, YYYY[ (Updated ...)]': {lines[2]!r}")
    date = datetime.strptime(m["date"], "%B %d, %Y").date()
    body = "\n".join(lines[3:]).lstrip("\n")
    return lines[0].strip(), date, m["updated"], body


def owning_slug(day_dir):
    """The report that owns a day-dir's assets = its single top-level .md."""
    mds = sorted(day_dir.glob("*.md"))
    if len(mds) != 1:
        die(
            f"{day_dir}: expected exactly one report .md to resolve an asset "
            f"link, found {[p.name for p in mds]}"
        )
    return mds[0].stem


def rewrite_links(body, src_dir, reports_root, slug):
    """Join wrapped links, then remap cross-report relative links.

    The blog mirrors the reports tree except each post sits one level deeper,
    in its slug folder — so a link into another day-dir is re-resolved as a
    relative path from blog/Y/M/D/slug/ to blog/Y'/M'/D'/their-slug/[asset].
    """
    # kramdown chokes on a newline straight after "](": join URL up.
    body = re.sub(r"\]\(\s*\n\s*", "](", body)

    reports_root = reports_root.resolve()
    src_dir = src_dir.resolve()
    post_dir = Path("blog", *src_dir.relative_to(reports_root).parts, slug)

    def remap(m):
        url = m.group(1)
        if "://" in url or url.startswith(("#", "/", "mailto:")):
            return m.group(0)
        target = (src_dir / url).resolve()
        if target.parent == src_dir or src_dir in target.parents:
            return m.group(0)  # own folder (or below): copied verbatim
        try:
            parts = target.relative_to(reports_root).parts  # (Y, M, D, name..)
        except ValueError:
            print(f"  warning: link escapes reports root, left as-is: {url}")
            return m.group(0)
        if len(parts) < 4:
            print(f"  warning: unrecognized link layout, left as-is: {url}")
            return m.group(0)
        their_slug = owning_slug(reports_root.joinpath(*parts[:3]))
        their_dir = Path("blog", *parts[:3], their_slug)
        name = Path(*parts[3:])
        if name.suffix == ".md":  # link to the report itself -> post URL
            new = relpath(their_dir, post_dir) + "/"
        else:  # link to one of its assets
            new = relpath(their_dir / name, post_dir)
        return f"]({new})"

    return LINK_RE.sub(remap, body)


def first_sentence(body):
    para = body.split("\n\n", 1)[0].replace("\n", " ")
    para = re.sub(r"\[([^]]*)\]\([^)]*\)", r"\1", para)  # strip link targets
    para = re.sub(r"[*_]{1,2}(\S(?:[^*_]*\S)?)[*_]{1,2}", r"\1", para)  # emphasis
    m = re.match(r".+?[.!?](?=\s|$)", para)
    return (m.group(0) if m else para).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("report", help="report .md, absolute or relative to reports root")
    ap.add_argument("--description", help="front-matter description (else: first sentence, with a warning)")
    ap.add_argument("--reports-root", type=Path, default=DEFAULT_REPORTS_ROOT)
    ap.add_argument("--site-root", type=Path, default=SITE_ROOT)
    ap.add_argument("--dry-run", action="store_true", help="print what would be written, write nothing")
    ap.add_argument("--force", action="store_true", help="overwrite an existing post folder")
    args = ap.parse_args()

    reports_root = args.reports_root.resolve()
    src = Path(args.report)
    if not src.is_absolute():
        src = reports_root / src
    src = src.resolve()
    if not src.is_file():
        die(f"no such report: {src}")
    try:
        rel = src.relative_to(reports_root)
    except ValueError:
        die(f"{src} is not under reports root {reports_root}")
    if len(rel.parts) != 4:
        die(f"expected <reports>/YYYY/MM/DD/<slug>.md, got {rel}")

    slug = src.stem
    date_path = Path(*rel.parts[:3])
    dest_dir = args.site_root / "blog" / date_path / slug

    title, date, updated, body = parse_header(src.read_text(), src)
    if str(date_path) != date.strftime("%Y/%m/%d"):
        print(f"  warning: directory {date_path} != date line {date}")

    body = rewrite_links(body, src.parent, reports_root, slug)

    description = args.description
    if not description:
        description = first_sentence(body)
        print(f"  warning: no --description; using first sentence:\n    {description}")

    front = (
        "---\n"
        "layout: post\n"
        f'title: "{title}"\n'
        f"date: {date.isoformat()}\n"
        f"description: {description}\n"
        "---\n"
    )
    updated_note = f"\n*Updated {updated}*\n" if updated else ""
    index_md = f"{front}{updated_note}\n{body}"

    assets = [p for p in src.parent.iterdir() if p != src and not p.name.startswith(".")]
    asset_names = [p.name + ("/" if p.is_dir() else "") for p in assets]

    print(f"import: {rel}")
    print(f"    to: {dest_dir.relative_to(args.site_root)}/index.md")
    print(f"assets: {', '.join(asset_names) or '(none)'}")
    if args.dry_run:
        print("--- index.md " + "-" * 27)
        print(index_md)
        return

    if dest_dir.exists() and not args.force:
        die(f"{dest_dir} exists (use --force to overwrite)")
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / "index.md").write_text(index_md)
    skipped_md = []

    def ignore_md(d, names):
        bad = [n for n in names if n.endswith(".md")]
        skipped_md.extend(f"{d}/{n}" for n in bad)
        return bad

    for p in assets:
        if p.is_dir():
            shutil.copytree(p, dest_dir / p.name, dirs_exist_ok=True, ignore=ignore_md)
        elif p.suffix == ".md":
            skipped_md.append(str(p))
        else:
            shutil.copy2(p, dest_dir / p.name)
    for s in skipped_md:
        print(f"  note: skipped stray .md asset: {s}")
    print(f"done. Review, then: git add blog/{date_path}/{slug} && git commit && git push")


if __name__ == "__main__":
    main()
