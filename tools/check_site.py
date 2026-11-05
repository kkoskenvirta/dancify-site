#!/usr/bin/env python3
"""Checks the built site: every internal link, image, script and stylesheet resolves to a file, every in-page anchor
exists, every <use href="#…"> icon is in the page, and every JSON-LD block parses.

    python3 tools/check_site.py
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
HOST = "dancify.apphq.online"


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[str] = []
        self.ids: set[str] = set()
        self.uses: list[str] = []
        self.ld: list[str] = []
        self._ld = False
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "use" and a.get("href"):
            self.uses.append(a["href"])
        for key in ("href", "src"):
            if a.get(key) and tag not in ("use",):
                self.refs.append(a[key])
        if a.get("srcset"):
            self.refs += [part.strip().split(" ")[0] for part in a["srcset"].split(",")]
        if tag == "script" and a.get("type") == "application/ld+json":
            self._ld, self._buf = True, []

    def handle_data(self, data: str) -> None:
        if self._ld:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._ld:
            self._ld = False
            self.ld.append("".join(self._buf))


def resolve(page: Path, ref: str) -> Path | None:
    parts = urlsplit(ref)
    if parts.scheme in ("mailto", "tel", "data", "javascript"):
        return None
    if parts.scheme in ("http", "https"):
        if parts.netloc != HOST:
            return None
        path = parts.path
    elif ref.startswith("/"):
        path = parts.path
    else:
        path = str((page.parent / parts.path).relative_to(ROOT)) if parts.path else ""
        path = "/" + path if path else ""
    if not path:
        return None
    target = ROOT / unquote(path).lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    return target


def main() -> int:
    errors: list[str] = []
    pages = [p for p in ROOT.rglob("*.html") if "tools" not in p.relative_to(ROOT).parts and not p.name.startswith("_")]
    ld_blocks = 0
    for page in sorted(pages):
        rel = page.relative_to(ROOT)
        parser = Page()
        parser.feed(page.read_text())
        for ref in parser.refs:
            if ref.startswith("#"):
                if ref != "#" and ref[1:] not in parser.ids:
                    errors.append(f"{rel}: anchor {ref} has no target")
                continue
            target = resolve(page, ref)
            if target is None:
                continue
            if not target.exists():
                errors.append(f"{rel}: {ref} -> missing {target.relative_to(ROOT)}")
            frag = urlsplit(ref).fragment
            if frag and target.exists() and target.suffix == ".html" and f'id="{frag}"' not in target.read_text():
                errors.append(f"{rel}: {ref} -> no #{frag} in {target.relative_to(ROOT)}")
        for use in parser.uses:
            if use.lstrip("#") not in parser.ids:
                errors.append(f"{rel}: icon {use} isn't in the page's sprite")
        for block in parser.ld:
            ld_blocks += 1
            try:
                json.loads(block)
            except json.JSONDecodeError as error:
                errors.append(f"{rel}: JSON-LD doesn't parse ({error})")
    for xml in ROOT.rglob("*.xml"):
        if "tools" in xml.relative_to(ROOT).parts:
            continue
        for loc in re.findall(r"<loc>https://dancify\.apphq\.online(/[^<]*)</loc>", xml.read_text()):
            target = ROOT / loc.lstrip("/")
            if loc.endswith("/"):
                target = target / "index.html"
            if not target.exists():
                errors.append(f"{xml.relative_to(ROOT)}: {loc} doesn't exist")
    print(f"{len(pages)} pages, {ld_blocks} JSON-LD blocks checked")
    for error in errors:
        print("error:", error)
    print("no problems found" if not errors else f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
