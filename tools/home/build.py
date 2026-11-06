#!/usr/bin/env python3
"""Builds the three landing pages (index.html, es/index.html, de/index.html) from one template.

Words live in copy-<lang>.json. In a title, {braces} mark the one phrase that takes the accent colour, the way the
App Store screenshots set their headlines. parts/<lang>-{head,nav,footer}.html hold the language's <head> (meta,
hreflang, structured data), bar and footer; {base} in them is site.json's "base".

The blog build calls this first, then fills the blog cards between their markers and points every path at "base"
(tools/rebase.py), so `python3 tools/blog/build.py` is the only command to run.

Screens are always whole: no phone here is cropped, faded or laid over another one.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SITE = json.loads((ROOT / "tools/blog/site.json").read_text())
BASE = SITE["base"].rstrip("/")
SPRITE = (ROOT / "tools/blog/sprite.svg").read_text().strip()
STORE = "https://apps.apple.com/app/id6830154598"
PAGES = {"en": "index.html", "es": "es/index.html", "de": "de/index.html"}

# Icons follow the order of the points in the copy files.
ICONS = {
    "camera": ["metronome", "focus", "tripod", "lens", "slowmo", "record"],
    "handsfree": ["check", "play", "stack", "device"],
    "reference": ["pip", "play", "headphones", "stack"],
    "player": ["loop", "metronome", "slowmo", "mirror", "tv", "music"],
    "editor": ["scissors", "speed", "snow", "crop", "sliders", "text", "music", "flag"],
    "privacy": ["user-off", "ban", "cloud", "device"],
}


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def title(text: str) -> str:
    """Sentence-case headline with its one accent phrase."""
    return re.sub(r"\{(.+?)\}", r'<span class="marked">\1</span>', esc(text))


def plain(text: str) -> str:
    return text.replace("{", "").replace("}", "")


def icon(name: str) -> str:
    return f'<svg aria-hidden="true"><use href="#i-{name}"/></svg>'


class Page:
    def __init__(self, lang: str):
        self.lang = lang
        self.c = json.loads((HERE / f"copy-{lang}.json").read_text())
        self.first_image = True

    def phone(self, name: str, extra: str = "", width: int = 780, eager: bool = False) -> str:
        alt = esc(self.c["alts"].get(name, ""))
        src = f"/assets/img/app/{self.lang}/{name}.webp"
        load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
        cls = f"phone {extra}".strip()
        return f'<div class="{cls}"><img src="{src}" width="{width}" height="1695" {load} alt="{alt}"></div>'

    def chip(self, text: str, tag: str | None = None) -> str:
        badge = f'<span class="tag tag-premium">{esc(tag)}</span>' if tag else ""
        return f'<p class="eyebrow"><span class="mark" aria-hidden="true"></span>{esc(text)}{badge}</p>'

    def head(self, key: str, center: bool = True, level: str = "h2") -> str:
        s = self.c[key]
        lead = s.get("lead_html") or (esc(s["lead"]) if s.get("lead") else "")
        cls = "section-head is-center" if center else "section-head"
        return f"""<div class="{cls}" data-reveal>
          {self.chip(s['chip'], s.get('tag'))}
          <{level} id="{key}-title">{title(s['title'])}</{level}>
          {f'<p>{lead}</p>' if lead else ''}
        </div>"""

    def points(self, key: str) -> str:
        items = "\n".join(
            f"""            <li><span class="ico">{icon(ICONS[key][i])}</span><b>{esc(a)}</b><p>{esc(b)}</p></li>"""
            for i, (a, b) in enumerate(self.c[key]["points"])
        )
        return f'<ul class="points">\n{items}\n          </ul>'

    def feature(self, key: str, screens: list[str], flip: bool = False, tight: bool = False) -> str:
        s = self.c[key]
        poses = ["pose-left", "pose-right"] if len(screens) > 1 else ["pose-left" if flip else "pose-right"]
        phones = "\n".join("          " + self.phone(n, p) for n, p in zip(screens, poses))
        side = "from-left" if flip else "from-right"
        visual = "feature-visual is-pair" if len(screens) > 1 else "feature-visual"
        return f"""    <section class="section" id="{key}" aria-labelledby="{key}-title"{' style="padding-top:0"' if tight else ''}>
      <div class="container feature{' is-flip' if flip else ''}">
        <div class="feature-copy" data-reveal>
          {self.chip(s['chip'], s.get('tag'))}
          <h2 id="{key}-title">{title(s['title'])}</h2>
          <p>{esc(s['lead'])}</p>
          {self.points(key)}
        </div>
        <div class="{visual}" data-reveal style="--delay:.08s">
          <span class="beam" aria-hidden="true"></span>
          <span class="tape floor {side}" aria-hidden="true"></span>
{phones}
        </div>
      </div>
    </section>"""

    def trio(self, screens: list[str], captions: list[list[str]]) -> str:
        items = "\n".join(
            f"""          <figure class="screen" data-reveal style="--delay:{i * 0.07:.2f}s">
            {self.phone(n)}
            <figcaption><b>{esc(a)}</b>{esc(b)}</figcaption>
          </figure>"""
            for i, (n, (a, b)) in enumerate(zip(screens, captions))
        )
        return f"""<div class="screens-wrap">
          <span class="beam" aria-hidden="true"></span>
          <span class="tape floor across" aria-hidden="true"></span>
          <div class="screens">
{items}
          </div>
        </div>"""

    def store_button(self) -> str:
        h = self.c["hero"]
        return f"""<a class="btn btn-store" href="{STORE}" data-store>
              {icon('apple')}
              <span class="btn-label"><small>{esc(h['store_small'])}</small><strong>{esc(h['store'])}</strong></span>
            </a>"""

    def main(self) -> str:
        c = self.c
        h = c["hero"]
        meta = "".join(f"<li>{icon('check')}{esc(m)}</li>" for m in h["meta"])
        styles = c["styles"]
        style_items = "".join(f"<li>{esc(s)}</li>" for s in styles["list"])
        steps = "\n".join(
            f"""          <li class="how-step" data-reveal style="--delay:{i * 0.07:.2f}s">
            <span class="step-no">0{i + 1}</span>
            <h3>{esc(a)}</h3>
            <p>{esc(b)}</p>
            {self.phone(n)}
          </li>"""
            for i, (n, (a, b)) in enumerate(zip(["camera", "day-calendar", "recording"], c["how"]["steps"]))
        )
        notes = "".join(f'<span><span class="mark" aria-hidden="true"></span>{esc(n)}</span>' for n in c["diary"]["notes"])
        tools = "\n".join(
            f"""          <li data-reveal style="--delay:{i * 0.03:.2f}s"><span class="ico">{icon(ICONS['editor'][i])}</span><b>{esc(a)}</b><p>{esc(b)}</p></li>"""
            for i, (a, b) in enumerate(c["editor"]["tools"])
        )
        ed = c["editor"]
        pr = c["privacy"]
        privacy_items = "\n".join(
            f"""            <li><b>{icon(ICONS['privacy'][i])}{esc(a)}</b><p>{esc(b)}</p></li>""" for i, (a, b) in enumerate(pr["items"])
        )
        plans = []
        for i, plan in enumerate(c["pricing"]["plans"]):
            rows = "".join(f"<li>{icon('check')}<span>{esc(x)}</span></li>" for x in plan["list"])
            button = f"""<a class="btn btn-primary" href="{STORE}" data-store>{icon('apple')}{esc(plan['button'])}</a>""" if plan.get("button") else ""
            tag = "tag-premium" if i else "tag-free"
            plans.append(f"""          <article class="plan card{' is-premium' if i else ''}" data-reveal{' style="--delay:.08s"' if i else ''}>
            <h3>{esc(plan['name'])} <span class="tag {tag}">{esc(plan['tag'])}</span></h3>
            <p class="plan-price">{esc(plan['price'])}<small>{esc(plan['price_note'])}</small></p>
            <ul>{rows}</ul>
            {button}
          </article>""")
        faqs = "\n".join(f"""          <details>
            <summary>{esc(q)}</summary>
            <p>{a if "<a " in a else esc(a)}</p>
          </details>""" for q, a in c["faq"]["items"])
        return f"""  <main id="main">
    <section class="hero">
      <span class="nav-sentinel" data-nav-sentinel aria-hidden="true"></span>
      <div class="container hero-grid">
        <div class="hero-copy">
          <p class="eyebrow hero-hook" data-reveal><span class="mark" aria-hidden="true"></span>{esc(h['chip'])}</p>
          <h1 data-reveal style="--delay:.06s">{title(h['title'])}</h1>
          <p class="hero-lead" data-reveal style="--delay:.12s">{esc(h['lead'])}</p>
          <div class="hero-actions" data-reveal style="--delay:.18s">
            {self.store_button()}
            <a class="btn btn-ghost" href="#how">{esc(h['how_link'])}</a>
          </div>
          <ul class="hero-meta" data-reveal style="--delay:.24s">{meta}</ul>
        </div>
        <div class="stage" data-reveal style="--delay:.12s">
          <span class="beam" aria-hidden="true"></span>
          <span class="tape floor from-right" aria-hidden="true"></span>
          {self.phone('camera-countin', 'p-side pose-right')}
          {self.phone('journal', 'p-main pose-tilt', eager=True)}
        </div>
      </div>
    </section>

    <section class="styles-band" id="styles" aria-label="{esc(plain(styles['chip']))}">
      <div class="container">
        <ul class="styles">{style_items}</ul>
        <p class="styles-note">{esc(styles['note'])}</p>
      </div>
    </section>

    <section class="section" id="how" aria-labelledby="how-title">
      <div class="container">
        {self.head('how')}
        <div class="how-wrap">
          <span class="tape floor across" aria-hidden="true"></span>
          <ol class="how-steps">
{steps}
          </ol>
        </div>
      </div>
    </section>

{self.feature('camera', ['camera-follow', 'camera-formats'])}

{self.feature('handsfree', ['hands-free'], flip=True, tight=True)}

{self.feature('reference', ['camera-reference', 'camera-split'], tight=True)}

    <section class="section" id="diary" aria-labelledby="diary-title">
      <div class="container">
        {self.head('diary')}
        {self.trio(['journal-light', 'timeline', 'pieces'], c['diary']['screens'])}
        <p class="screens-note" data-reveal>{notes}</p>
      </div>
    </section>

{self.feature('player', ['player-loop', 'player-counts'])}

    <section class="section" id="editor" aria-labelledby="editor-title" style="padding-top:0">
      <div class="container">
        <div class="feature is-flip">
          <div class="feature-copy" data-reveal>
            {self.chip(ed['chip'])}
            <h2 id="editor-title">{title(ed['title'])}</h2>
            <p>{esc(ed['lead'])}</p>
            <p class="editor-after">{esc(ed['after'])}</p>
          </div>
          <div class="feature-visual is-pair" data-reveal style="--delay:.08s">
            <span class="beam" aria-hidden="true"></span>
            <span class="tape floor from-left" aria-hidden="true"></span>
            {self.phone('editor', 'pose-left')}
            {self.phone('editor-adjust', 'pose-right')}
          </div>
        </div>
        <ul class="bento">
{tools}
        </ul>
      </div>
    </section>

    <section class="section" id="premium" aria-labelledby="premium-title">
      <div class="container">
        {self.head('premium')}
        {self.trio(['compare', 'reel', 'pose'], c['premium']['cards'])}
      </div>
    </section>

    <section class="section" id="privacy" aria-labelledby="privacy-title">
      <div class="container">
        <div class="privacy-card card" data-reveal>
          <div>
            {self.chip(pr['chip'])}
            <h2 id="privacy-title">{title(pr['title'])}</h2>
            <p>{esc(pr['lead'])}</p>
            <div class="label-badge">{icon('shield')}<small>{esc(pr['badge'][0])}</small><b>{esc(pr['badge'][1])}</b></div>
            <p><a class="privacy-more" href="/privacy/" hreflang="en">{esc(pr['more'])}</a></p>
          </div>
          <ul class="privacy-list">
{privacy_items}
          </ul>
        </div>
      </div>
    </section>

    <section class="section" id="pricing" aria-labelledby="pricing-title" style="padding-top:0">
      <div class="container">
        {self.head('pricing')}
        <div class="plans">
{chr(10).join(plans)}
        </div>
        <p class="plans-note">{esc(c['pricing']['note'])}</p>
      </div>
    </section>

    <section class="section" id="faq" aria-labelledby="faq-title" style="padding-top:0">
      <div class="container faq-wrap">
        {self.head('faq', center=False)}
        <div class="faq" data-reveal>
{faqs}
        </div>
      </div>
    </section>

    <section class="section" id="blog" aria-labelledby="blog-title" style="padding-top:0">
      <div class="container">
        <div class="section-head" data-reveal>
          {self.chip(c['blog']['chip'])}
          <h2 id="blog-title">{title(c['blog']['title'])}</h2>
        </div>
        <!-- blog-cards:start -->
        <ul class="post-cards post-cards-home"></ul>
        <!-- blog-cards:end -->
        <p class="blog-more"><a class="btn btn-ghost" href="{SITE['languages'][self.lang]['blog']}">{esc(c['blog']['more'])}</a></p>
      </div>
    </section>

    <section class="finale">
      <span class="beam" aria-hidden="true"></span>
      <div class="container finale-inner" data-reveal>
        <div class="finale-mark" aria-hidden="true">
          <img class="finale-dancer" src="/assets/img/dancer.svg" width="595" height="300" alt="">
          <span class="tape floor-strip"></span>
        </div>
        <h2>{title(c['cta']['title'])}</h2>
        <p>{esc(c['cta']['lead'])}</p>
        {self.store_button()}
      </div>
    </section>
  </main>"""

    def faq_ld(self) -> str:
        items = []
        for q, a in self.c["faq"]["items"]:
            text = html.unescape(re.sub(r"<[^>]+>", "", a))
            items.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": text}})
        block = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items}, ensure_ascii=False, indent=2)
        return f'<script type="application/ld+json">\n{block}\n  </script>'

    def render(self) -> str:
        part = lambda name: (HERE / "parts" / f"{self.lang}-{name}.html").read_text().replace("{base}", BASE).strip()
        head = part("head").replace("<!-- faq-ld -->", self.faq_ld())
        return f"""<!doctype html>
<html lang="{self.lang}">
<head>
  {head}
</head>
<body>
  {SPRITE}
  <a class="skip-link" href="#main">{esc(self.c.get('skip', 'Skip to content'))}</a>

  {part('nav')}

{self.main()}

  {part('footer')}
</body>
</html>
"""


def build() -> None:
    for lang, path in PAGES.items():
        (ROOT / path).write_text(Page(lang).render())
        print("built", path)


if __name__ == "__main__":
    build()
