# dancify.apphq.online

Website for [Dancify](https://apps.apple.com/app/id6830154598), the camera, practice diary and video editor for dancers (iPhone and iPad). Served by GitHub Pages from `main` (root) behind Cloudflare. Plain HTML, CSS and JS with no build step on Pages (`.nojekyll` turns off Jekyll); the blog is generated locally and committed.

| Path | Contents |
| --- | --- |
| `index.html` | Landing page (English, also `x-default`) |
| `es/`, `de/` | Spanish and German landing pages |
| `blog/`, `es/blog/`, `de/blog/` | Blog indexes, posts and RSS feeds per language (generated, see below) |
| `tools/blog/` | Blog generator, its templates and the posts (not linked, disallowed in `robots.txt`) |
| `tools/check_site.py` | Local checks: every internal link and asset resolves, JSON-LD parses |
| `sitemap.xml`, `llms.txt`, `llms-full.txt` | Generated with the blog: every page with its `hreflang` alternates, a plain summary for AI assistants, and the full text of every English article in one file |
| `index.md` next to every page | Generated with the blog: the page's `<main>` as Markdown, served to agents that send `Accept: text/markdown` (see Cloudflare below) |
| `auth.md` | Tells AI agents that reading the site needs no credentials and that there is no agent registration, account or public API |
| `<key>.txt` | The IndexNow key (a 32-character hex file name, its content is the same key). `tools/blog/indexnow.py` submits the sitemap's URLs to Bing and other IndexNow engines |
| `privacy/`, `terms/` | Privacy policy and terms of use (English, shared by all languages), linked from the app and the App Store listing |
| `404.html` | Not found page; follows the `/es/` or `/de/` prefix of the missing address |
| `assets/` | Styles, script, self-hosted Geist (`assets/fonts`, OFL in `OFL.txt`), icons, the grain tile, share images (`assets/img/og`), blog covers (`assets/img/covers`) and localized app screens (`assets/img/app/{en,es,de}`) |
| `.well-known/apple-app-site-association` | Universal links (no paths yet) and web credentials for `XW75F94L2B.com.kkoskenvirta.dancify` |
| `CNAME` | Custom domain |

`robots.txt` is hand-written. Its `Content-Signal` lines (https://contentsignals.org) allow search, AI answers and AI training, to match the crawlers it welcomes.

Preview locally with `python3 -m http.server 8000` and open http://localhost:8000.

## Design

"Studio Night", the app's own look (`Dancify/DesignSystem/Theme.swift`, `Surfaces.swift`, `SpikeTape.swift` in the app repo): a near-black stage (`#0A0A0B`) under a faint violet wash with sparse purple grain specks (`assets/img/grain.png`), lavender `#A98BFF` as the one accent (deep `#7C5CFA`), camera red `#FF3B3B` only for the REC dot, ink `#F5F2FB`, cards `#19181C` with a `#2A2830` rim and a soft top light. Geist for headings (self-hosted, Latin subset WOFF2), the system font for reading. Spike tape (a strip of gaffer tape with torn ends) is the one loud mark: under the hero phones, before section labels in the activity colours, under the marked headline word, and on the blog covers. A light "rehearsal room" variant follows `prefers-color-scheme: light`. Motion is gentle and turns off under Reduce Motion.

## Languages

English is the default and lives at the root. Spanish is under `/es/` and German under `/de/`, with localized blog slugs (`/es/blog/como-grabarte-bailando/`, `/de/blog/sich-beim-tanzen-filmen/`). The privacy policy, terms and 404 page are English only and shared by all three.

- Every localized page has a self-referencing canonical and `hreflang` links to its translations plus `x-default` (English). `sitemap.xml` repeats them.
- The language menu in the header and the footer links go to the same page in the other language, not to its home page.
- A language picked in the menu is remembered in `localStorage` (`dancify-lang`, disclosed in the privacy policy, section 9). Then `/` opens the saved language, and the English-only pages (`<body data-shared>`) point their home, section and blog links at it.
- Visitors whose browser prefers another available language see a small hint to switch, never a redirect, so search engines always get the page they asked for.

The Spanish and German landing pages are hand-written HTML like `index.html`. Keep their structure in step when the English page changes. The one exception is the "From the blog" cards between the `blog-cards` comments: the blog build rewrites them with the newest six posts, so don't edit them by hand.

The German site never names other apps. Comparative advertising follows the same EU rules everywhere, but in Germany (UWG §6) competitors and associations enforce them with costly cease-and-desist letters, so the comparison post (`best-dance-apps`) has no German version (`untranslated` in `site.json`) and German posts don't link to it. Keep competitor names out of `tools/blog/content/de/` and `de/`.

## Blog

Posts are written once per language and built into static pages by `tools/blog/build.py` (Python 3, no dependencies). The generated HTML is committed, so GitHub Pages still has no build step.

```bash
python3 tools/blog/build.py        # posts, blog indexes, feeds, sitemap.xml, llms.txt, llms-full.txt, home page blog cards, index.md per page
python3 tools/blog/build.py --og   # also renders the covers and 1200×630 share images (Google Chrome, cwebp)
python3 tools/check_site.py        # internal links, assets and JSON-LD
python3 tools/blog/indexnow.py     # after publishing: tell Bing and other IndexNow engines about every URL
```

| File | Contents |
| --- | --- |
| `tools/blog/site.json` | Shared strings per language (nav, footer, labels, dates, author, call to action), post order, `untranslated`, `llms.txt` text, home share images, cover screens per post |
| `tools/blog/content/<lang>/<post>.json` | Slug, title tag, headline, description, cover screens, FAQ, sources, keywords |
| `tools/blog/content/<lang>/<post>.html` | The article body. `{img}` is the language's screenshot folder, `{post:<id>}` links another post in the same language, `{store}` is the App Store link |
| `tools/blog/sprite.svg` | The icon sprite every page carries (`<use href="#i-…">`); add an icon here before using it in a post |
| `tools/blog/og.html` | Template for the share images |
| `tools/blog/cover.html` | Template for the article covers (three phones under a spotlight on a strip of tape). Screens and tape colour per post are under `covers` in `site.json`; output is `assets/img/covers/<lang>-<post>-{1200,2400}.webp` |

Each post page gets `BlogPosting`, `BreadcrumbList` and `FAQPage` structured data, a table of contents built from the `<h2 id>` headings, related posts and the localized call to action. To add a post, add the same `id` in all three content folders (the build warns about a missing translation), add the id to `order` in `site.json`, run both commands and check the pages locally. Half-written posts (a `.json` without its `.html`, JSON that doesn't parse) are skipped with a warning, so the build always finishes. Claims about other apps need a source in the post's `sources` list and a check date; prices change too often to quote.

## App screens

`assets/img/app/<lang>/<name>.webp` are 720 px wide captures of the current app (dark appearance, demo journal) from the Debug build on the `Dancify App Store iPhone 6.9` simulator: `journal`, `day`, `recording`, `timeline`, `reel`, `compare`, `camera`, `camera-countin`, `camera-follow`, `camera-reference`, `editor`, `editor-adjust`, `player-loop`, `player-counts`, `pieces`, `pieces-list`, `pose`. To recapture (app repo: `~/.t3/projects/dancify`):

```bash
cd ~/.t3/projects/dancify
source scripts/use_xcode.sh
xcodebuild build -project Dancify.xcodeproj -scheme Dancify -configuration Debug \
  -destination 'platform=iOS Simulator,name=Dancify App Store iPhone 6.9' -derivedDataPath /tmp/dancify-dd-site
UDID=$(xcrun simctl list devices | grep 'Dancify App Store iPhone 6.9' | grep -oE '[0-9A-F-]{36}')
xcrun simctl boot $UDID; xcrun simctl bootstatus $UDID -b
xcrun simctl install $UDID /tmp/dancify-dd-site/Build/Products/Debug-iphonesimulator/Dancify.app
xcrun simctl status_bar $UDID override --time 9:41 --batteryLevel 100 --batteryState charged --cellularBars 4 --wifiBars 3

# One screen: language (en/es/de with en_US/es_ES/de_DE), then the screen's demo arguments
xcrun simctl launch --terminate-running-process $UDID com.kkoskenvirta.dancify -AppleLanguages "(es)" -AppleLocale es_ES \
  -demo YES -demoFootageDir ~/.t3/projects/dancify/appstore/demo-footage -demoAppearance dark -demoToday 2026-10-27 \
  -demoTab journal
sleep 8; xcrun simctl io $UDID screenshot es-journal.png
cwebp -resize 720 0 -q 82 -sharp_yuv es-journal.png -o assets/img/app/es/journal.webp
xcrun simctl shutdown $UDID
```

| Screen | Demo arguments (after the common ones above) | Wait |
| --- | --- | --- |
| `journal` | `-demoTab journal` | 8 s |
| `day` | `-demoTab journal -demoDay latest -demoScroll bottom` | 10 s |
| `recording` | `-demoTab journal -demoRecording hero` | 10 s |
| `timeline` | `-demoTab timeline -demoDay none` (without `-demoDay none` the default latest day switches back to Journal) | 9 s |
| `reel` | `-demoTab reels -demoSheet reelBuilder` | 10 s |
| `compare` | `-demoTab journal -demoRecording hero -demoSheet compare` | 11 s |
| `camera` | `-demoSheet record` | 10 s |
| `camera-countin` | `-demoSheet record -demoCapture countIn` | 10 s |
| `camera-follow` | `-demoSheet record -demoCapture follow` | 10 s |
| `camera-reference` | `-demoSheet record -demoCapture reference` | 11 s |
| `editor` | `-demoTab journal -demoRecording hero -demoEditor YES -demoEditorSample YES -demoEditorTool trim` | 13 s |
| `editor-adjust` | same with `-demoEditorTool adjust` | 13 s |
| `player-loop` | `-demoTab journal -demoRecording hero -demoPlayerLoop YES` | 11 s |
| `player-counts` | `-demoTab journal -demoRecording hero -demoPlayerCounts YES` | 11 s |
| `pieces` | `-demoPiece "Slow Burn"` | 9 s |
| `pieces-list` | `-demoTab pieces -demoDay none` | 9 s |
| `pose` | `-demoTab journal -demoRecording hero -demoPose YES` | 11 s |

The seeded demo content (piece names such as "Slow Burn", take names such as "Full run") stays English in every language; the app's own UI is localized. The footage is the app repo's `appstore/demo-footage`.

## Hosting: GitHub Pages and Cloudflare

1. Create the GitHub repository and push `main`. Settings → Pages → Build and deployment: **Deploy from a branch**, branch `main`, folder `/ (root)`. No Actions workflow is needed.
2. Settings → Pages → Custom domain: `dancify.apphq.online` (the `CNAME` file already says so). Wait for the DNS check, then tick **Enforce HTTPS** once GitHub has issued the certificate.
3. Cloudflare, `apphq.online` zone → DNS: add `CNAME` `dancify` → `appriseventures.github.io` (repo `AppRiseVentures/dancify-site`), **Proxied** (orange cloud). If GitHub's certificate check stalls, set it to DNS only until Pages shows the certificate, then switch the proxy back on.
4. Cloudflare → SSL/TLS: encryption mode **Full** (GitHub Pages serves HTTPS). SSL/TLS → Edge Certificates: **Always Use HTTPS** on.

GitHub Pages can't set response headers or look at the `Accept` header, so three rules in the Cloudflare dashboard (apphq.online zone, Rules > Overview) do it. They aren't in this repo, so keep this list in step with the dashboard.

1. **URL Rewrite Rule** "Dancify: Markdown for agents". Custom filter expression:

   ```
   (http.host eq "dancify.apphq.online" and any(http.request.headers["accept"][*] contains "text/markdown") and ends_with(http.request.uri.path, "/") and not starts_with(http.request.uri.path, "/tools/"))
   ```

   Path: Rewrite to, Dynamic, `concat(http.request.uri.path, "index.md")`. Query: Preserve. GitHub Pages serves `.md` files as `text/markdown; charset=utf-8`, so agents get Markdown and browsers still get HTML.

2. **Response Header Transform Rule** "Dancify: agent discovery links". Expression `(http.host eq "dancify.apphq.online" and http.request.uri.path in {"/" "/index.md"})`. Set static, header `Link`:

   ```
   </llms.txt>; rel="describedby"; type="text/plain", </llms-full.txt>; rel="describedby"; type="text/plain", </index.md>; rel="alternate"; type="text/markdown"
   ```

3. **Response Header Transform Rule** "Dancify: vary on Accept". Expression `(http.host eq "dancify.apphq.online" and (ends_with(http.request.uri.path, "/") or ends_with(http.request.uri.path, "/index.md")))`. Add, header `Vary`, value `Accept`, so caches keep the HTML and Markdown versions apart.

Check with `curl -sI https://dancify.apphq.online | grep -i link` and `curl -s -H 'Accept: text/markdown' https://dancify.apphq.online | head`, or scan the site at https://isitagentready.com. `curl -s https://dancify.apphq.online/.well-known/apple-app-site-association` should return the JSON without a redirect.

After the first deploy: run `python3 tools/blog/indexnow.py`, add the site to Google Search Console and Bing Webmaster Tools, and submit `https://dancify.apphq.online/sitemap.xml`.
