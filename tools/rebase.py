#!/usr/bin/env python3
"""Points the site at the address in tools/blog/site.json → "base".

The site is written with root paths ("/assets/…", "/es/"). When "base" has a path of its own (a GitHub project page
like https://kkoskenvirta.github.io/dancify-site), every root path in the HTML, CSS and JS gets that prefix. The blog
build runs this at the end, so generated and hand-written pages always agree; running it again changes nothing.

Moving to another address (a custom domain, say): set "base", then run

    python3 tools/rebase.py --from https://kkoskenvirta.github.io/dancify-site
    python3 tools/blog/build.py

--from replaces the old absolute URLs and strips the old prefix before the new one is applied. Update CNAME too.
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / "tools/blog/site.json").read_text())["base"].rstrip("/")
PREFIX = urlsplit(BASE).path.rstrip("/")

ATTR = re.compile(r'\b(href|src|action|poster)="(/[^"]*)"')
SRCSET = re.compile(r'\b(srcset|imagesrcset)="([^"]*)"')
CSS_URL = re.compile(r'url\((["\']?)(/[^"\')]*)\1\)')
JS_ROOT = re.compile(r'^const ROOT = "[^"]*";', re.M)


def prefixed(path: str, prefix: str = PREFIX, old: str = "") -> str:
    if path.startswith("//"):
        return path
    if old and (path == old or path.startswith(old + "/")):
        path = path[len(old):] or "/"
    if prefix and (path == prefix or path.startswith(prefix + "/")):
        return path
    return prefix + path


def rebase_html(text: str, prefix: str = PREFIX, old: str = "") -> str:
    text = ATTR.sub(lambda m: f'{m[1]}="{prefixed(m[2], prefix, old)}"', text)

    def srcset(m: re.Match) -> str:
        entries = []
        for entry in m[2].split(","):
            parts = entry.strip().split(" ", 1)
            if parts[0].startswith("/"):
                parts[0] = prefixed(parts[0], prefix, old)
            entries.append(" ".join(parts))
        return f'{m[1]}="{", ".join(entries)}"'

    text = SRCSET.sub(srcset, text)
    # Inline scripts that build root paths (the language redirect, the 404 page) read this.
    text = re.sub(r'(<html\b[^>]*?) data-root="[^"]*"', r"\1", text)
    return re.sub(r"<html\b", f'<html data-root="{prefix}"', text, count=1)


def rebase_css(text: str, prefix: str = PREFIX, old: str = "") -> str:
    return CSS_URL.sub(lambda m: f"url({m[1]}{prefixed(m[2], prefix, old)}{m[1]})", text)


def rebase_js(text: str, prefix: str = PREFIX, old: str = "") -> str:
    return JS_ROOT.sub(f'const ROOT = "{prefix}";', text)


def site_files(*suffixes: str):
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT).parts
        if path.is_file() and path.suffix in suffixes and rel[0] not in ("tools", ".git") and path.name != "README.md":
            yield path


def apply(old_base: str | None = None) -> int:
    old_prefix = urlsplit(old_base).path.rstrip("/") if old_base else ""
    changed = 0
    for path in site_files(".html", ".css", ".js", ".md", ".txt", ".xml"):
        text = original = path.read_text()
        if old_base and old_base.rstrip("/") != BASE:
            text = text.replace(old_base.rstrip("/"), BASE)
        if path.suffix == ".html":
            text = rebase_html(text, PREFIX, old_prefix)
        elif path.suffix == ".css":
            text = rebase_css(text, PREFIX, old_prefix)
        elif path.suffix == ".js":
            text = rebase_js(text, PREFIX, old_prefix)
        if text != original:
            path.write_text(text)
            changed += 1
    return changed


if __name__ == "__main__":
    old = sys.argv[sys.argv.index("--from") + 1] if "--from" in sys.argv else None
    print(f"{apply(old)} files pointed at {BASE}")
