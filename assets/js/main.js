const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

// The bar turns to glass once the page has scrolled past the top.
const initNav = () => {
  const nav = document.querySelector("[data-nav]");
  const sentinel = document.querySelector("[data-nav-sentinel]");
  if (!nav) return;
  if (!sentinel || !("IntersectionObserver" in window)) return nav.classList.add("is-scrolled");
  new IntersectionObserver(([entry]) => nav.classList.toggle("is-scrolled", !entry.isIntersecting)).observe(sentinel);
};

// Sections settle into place as they arrive (CSS turns this off under Reduce Motion).
const initReveal = () => {
  const items = $$("[data-reveal]");
  if (!("IntersectionObserver" in window)) return items.forEach((item) => item.classList.add("is-visible"));
  const observer = new IntersectionObserver(
    (entries) =>
      entries
        .filter((entry) => entry.isIntersecting)
        .forEach(({ target }) => {
          target.classList.add("is-visible");
          observer.unobserve(target);
        }),
    { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
  );
  items.forEach((item) => observer.observe(item));
};

// ---------- Languages ----------
// English lives at the root, Spanish under /es/ and German under /de/. Every page lists its translations as
// <link rel="alternate" hreflang>. A language picked in the menu (or kept from the hint) is remembered in this
// browser only (localStorage "dancify-lang"), so English-only pages (privacy, terms, 404) link back to the right
// home and blog. Nobody is ever redirected away from the page they asked for, except "/" for someone who chose.
// The site's path on its host ("" at a domain root). tools/rebase.py sets it from site.json "base".
const ROOT = "";
const LANGS = ["en", "es", "de"];
const HOME = { en: ROOT + "/", es: ROOT + "/es/", de: ROOT + "/de/" };
const BLOG = { en: ROOT + "/blog/", es: ROOT + "/es/blog/", de: ROOT + "/de/blog/" };
const LANG_KEY = "dancify-lang";
const pageLang = () => (LANGS.includes(document.documentElement.lang) ? document.documentElement.lang : "en");
const storedLang = () => {
  try {
    const value = localStorage.getItem(LANG_KEY);
    return LANGS.includes(value) ? value : null;
  } catch {
    return null;
  }
};
const storeLang = (lang) => {
  try {
    localStorage.setItem(LANG_KEY, lang);
  } catch {}
};
const alternates = () =>
  Object.fromEntries($$('link[rel="alternate"][hreflang]').map((link) => [link.hreflang, new URL(link.href).pathname]));

const initLangMenu = () => {
  $$("[data-lang]").forEach((menu) => {
    menu.addEventListener("click", (event) => {
      const link = event.target.closest("a[hreflang]");
      if (link) storeLang(link.hreflang);
    });
    if (menu.tagName !== "DETAILS") return;
    document.addEventListener("click", (event) => menu.open && !menu.contains(event.target) && (menu.open = false));
    menu.addEventListener("keydown", (event) => {
      if (event.key !== "Escape" || !menu.open) return;
      menu.open = false;
      menu.querySelector("summary").focus();
    });
  });
};

// English-only pages: point home, section and blog links at the reader's language.
const initSharedPage = () => {
  if (!document.body.hasAttribute("data-shared")) return;
  const lang = storedLang();
  if (!lang || lang === "en") return;
  $$("a[href]").forEach((link) => {
    const href = link.getAttribute("href");
    if (href === ROOT + "/" || href.startsWith(ROOT + "/#")) link.setAttribute("href", HOME[lang] + href.slice(ROOT.length + 1));
    else if (href === ROOT + "/blog/") link.setAttribute("href", BLOG[lang]);
  });
};

const HINTS = {
  en: { text: "This page is also in English.", go: "Read in English", close: "Close" },
  es: { text: "Esta página también está en español.", go: "Leer en español", close: "Cerrar" },
  de: { text: "Diese Seite gibt es auch auf Deutsch.", go: "Auf Deutsch lesen", close: "Schließen" },
};

// A gentle suggestion instead of a redirect: search engines and people who chose a language are never moved.
const initLangHint = () => {
  if (storedLang() || document.body.hasAttribute("data-shared")) return;
  const current = pageLang();
  const wanted = (navigator.languages || [navigator.language])
    .map((tag) => String(tag).slice(0, 2).toLowerCase())
    .find((tag) => LANGS.includes(tag));
  const target = wanted && wanted !== current ? alternates()[wanted] : null;
  if (!target) return;
  const hint = document.createElement("div");
  hint.className = "lang-hint";
  hint.lang = wanted;
  hint.setAttribute("role", "region");
  hint.setAttribute("aria-label", HINTS[wanted].text);
  hint.innerHTML = `<p></p><a class="btn btn-primary" hreflang="${wanted}"></a><button type="button">×</button>`;
  hint.querySelector("p").textContent = HINTS[wanted].text;
  const go = hint.querySelector("a");
  go.href = target;
  go.textContent = HINTS[wanted].go;
  go.addEventListener("click", () => storeLang(wanted));
  const close = hint.querySelector("button");
  close.setAttribute("aria-label", HINTS[wanted].close);
  close.addEventListener("click", () => {
    storeLang(current);
    hint.remove();
  });
  document.body.append(hint);
};

// ---------- Articles ----------
const initToc = () => {
  const toc = document.querySelector("[data-toc]");
  if (!toc) return;
  const compact = matchMedia("(max-width: 1080px)");
  if (compact.matches) toc.open = false;
  const links = new Map($$("a[href^='#']", toc).map((link) => [decodeURIComponent(link.hash.slice(1)), link]));
  const headings = [...links.keys()].map((id) => document.getElementById(id)).filter(Boolean);
  const visible = new Set();
  const update = () => {
    const current = headings.find((heading) => visible.has(heading));
    if (current) links.forEach((link, id) => link.classList.toggle("is-current", id === current.id));
  };
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => (entry.isIntersecting ? visible.add(entry.target) : visible.delete(entry.target)));
      update();
    },
    { rootMargin: "-80px 0px -60% 0px" }
  );
  headings.forEach((heading) => observer.observe(heading));
  toc.addEventListener("click", (event) => event.target.closest("a") && compact.matches && (toc.open = false));
};

// Wide tables scroll sideways; fade the right edge while columns are still hidden.
const initTables = () => {
  $$(".cmp").forEach((table) => {
    const scroller = table.querySelector(".cmp-scroll");
    const foot = table.querySelector(".cmp-legend");
    if (!scroller) return;
    const update = () => {
      table.style.setProperty("--cmp-foot", `${foot ? foot.offsetHeight : 0}px`);
      table.classList.toggle("can-scroll", scroller.scrollLeft + scroller.clientWidth < scroller.scrollWidth - 2);
    };
    scroller.addEventListener("scroll", update, { passive: true });
    new ResizeObserver(update).observe(scroller);
    update();
  });
};

const initYear = () => $$("[data-year]").forEach((el) => (el.textContent = String(new Date().getFullYear())));

initNav();
initReveal();
initYear();
initLangMenu();
initSharedPage();
initLangHint();
initToc();
initTables();
