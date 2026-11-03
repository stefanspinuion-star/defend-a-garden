"""Build the Defend a Garden website into docs/ (GitHub Pages serves that folder).

Standard library only. Content lives in content/: site.json (links, ids, prices), i18n/<lang>.json (every
visible string) and news.json (devlog entries in every language). Run:  python build.py
Each language is a folder (English at the root), pages link relatively so the site works under any path.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
OUT = ROOT / "docs"
LANGS = ["en", "ro", "ru"]  # first one is served at the root
PAGES = ["index", "news", "store", "roadmap", "codes", "press", "privacy"]
NAV = ["index", "news", "store", "roadmap", "codes", "press"]


def load(name: str):
    return json.loads((CONTENT / name).read_text(encoding="utf-8"))


SITE = load("site.json")
NEWS = load("news.json")
T = {lang: load(f"i18n/{lang}.json") for lang in LANGS}

for lang in LANGS[1:]:
    missing = set(T["en"]) - set(T[lang])
    if missing:
        sys.exit(f"i18n/{lang}.json is missing keys: {sorted(missing)}")


def e(text: str) -> str:
    return html.escape(text, quote=True)


def rich(text: str) -> str:
    """Escape, then allow **bold** — the only markup content files may use."""
    out, bold = [], False
    for i, part in enumerate(e(text).split("**")):
        if i:
            bold = not bold
            out.append("<strong>" if bold else "</strong>")
        out.append(part)
    if bold:
        out.append("</strong>")
    return "".join(out)


def paras(lines: list[str]) -> str:
    return "".join(f"<p>{rich(p)}</p>" for p in lines)


def prefix(lang: str) -> str:
    return "" if lang == LANGS[0] else "../"


def page_path(lang: str, page: str) -> str:
    folder = "" if lang == LANGS[0] else f"{lang}/"
    return f"{folder}{page}.html"


def href(lang: str, page: str, from_lang: str) -> str:
    """Relative link from a page of `from_lang` to `page` in `lang`."""
    return prefix(from_lang) + page_path(lang, page)


def fmt_date(iso: str, lang: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {T[lang]['months'][d.month - 1]} {d.year}"


def play_button(lang: str, extra: str = "") -> str:
    t = T[lang]
    return (f'<a class="btn btn-play{extra}" href="{e(SITE["playUrl"])}" rel="noopener">'
            f'{e(t["play"])}</a>')


# ---------------------------------------------------------------- page bodies

def body_index(lang: str) -> str:
    t, p = T[lang], prefix(lang)
    features = "".join(
        f'<article class="card feature"><h3>{e(f["title"])}</h3><p>{rich(f["text"])}</p></article>'
        for f in t["features"])
    gallery = "".join(
        f'<figure><img src="{p}static/img/{g["img"]}.webp" alt="{e(g["alt"])}" loading="lazy" '
        f'width="1216" height="684"><figcaption>{e(g["alt"])}</figcaption></figure>'
        for g in t["gallery"])
    latest = "".join(news_card(n, lang, short=True) for n in NEWS[:3])
    return f"""
<section class="hero">
  <picture class="hero-art">
    <source media="(max-width: 720px)" srcset="{p}static/img/hero-mobile.webp">
    <img src="{p}static/img/hero.webp" alt="{e(t["hero_alt"])}" width="1652" height="684" fetchpriority="high">
  </picture>
  <div class="hero-inner wrap">
    <p class="eyebrow">{e(t["hero_eyebrow"])}</p>
    <h1>{e(t["hero_title"])}</h1>
    <p class="lede">{e(t["hero_lede"])}</p>
    <div class="actions">{play_button(lang)}
      <a class="btn btn-ghost" href="{href(lang, 'news', lang)}">{e(t["hero_secondary"])}</a></div>
    <p class="fine">{e(t["hero_fine"])}</p>
  </div>
</section>
<section class="wrap story">
  <h2>{e(t["story_title"])}</h2>
  {paras(t["story"])}
</section>
<section class="wrap">
  <h2>{e(t["features_title"])}</h2>
  <div class="grid3">{features}</div>
</section>
<section class="wrap">
  <h2>{e(t["gallery_title"])}</h2>
  <div class="gallery">{gallery}</div>
</section>
<section class="wrap">
  <div class="section-head"><h2>{e(t["latest_title"])}</h2>
    <a href="{href(lang, 'news', lang)}">{e(t["all_news"])} →</a></div>
  <div class="news-list">{latest}</div>
</section>
<section class="wrap cta">
  <h2>{e(t["cta_title"])}</h2>
  <p>{rich(t["cta_text"])}</p>
  <div class="actions">{play_button(lang)}
    <a class="btn btn-ghost" href="{e(SITE["community"])}" rel="noopener">{e(t["community"])}</a>
    <a class="btn btn-ghost" href="{e(SITE["bluesky"])}" rel="noopener">Bluesky</a></div>
</section>"""


def news_card(n: dict, lang: str, short: bool = False) -> str:
    loc = n[lang]
    body = loc["body"][:1] if short else loc["body"]
    img = ""
    if n.get("img") and not short:
        img = (f'<img src="{prefix(lang)}static/img/{n["img"]}.webp" alt="" loading="lazy" '
               f'width="1216" height="684">')
    tag = T[lang]["tags"].get(n["tag"], n["tag"])
    return (f'<article class="card news" id="{e(n["id"])}"><p class="meta"><time datetime="{n["date"]}">'
            f'{fmt_date(n["date"], lang)}</time> · {e(tag)}</p><h3>{e(loc["title"])}</h3>'
            f'{img}{paras(body)}'
            + (f'<a href="{href(lang, "news", lang)}#{e(n["id"])}">{e(T[lang]["read_more"])} →</a>' if short else "")
            + "</article>")


def body_news(lang: str) -> str:
    t = T[lang]
    items = "".join(news_card(n, lang) for n in NEWS)
    return f"""
<section class="wrap page-head"><h1>{e(t["news_title"])}</h1><p class="lede">{e(t["news_lede"])}</p></section>
<section class="wrap news-list">{items}</section>"""


def body_store(lang: str) -> str:
    t, p = T[lang], prefix(lang)
    passes = []
    for ps in SITE["passes"]:
        loc = t["passes"][ps["key"]]
        passes.append(
            f'<article class="card pass"><img src="{p}static/img/{ps["img"]}" alt="" width="96" height="96" loading="lazy">'
            f'<div><h3>{e(loc["name"])}</h3><p>{rich(loc["what"])}</p>'
            f'<p class="free">{e(t["free_path"])}: {rich(loc["free"])}</p>'
            f'<p class="price">{ps["price"]} R$</p>'
            f'<a class="btn btn-small" href="https://www.roblox.com/game-pass/{ps["id"]}" rel="noopener">'
            f'{e(t["view_on_roblox"])}</a></div></article>')
    products = "".join(
        f'<li><strong>{e(t["products"][pr["key"]]["name"])}</strong> — {pr["price"]} R$. '
        f'{rich(t["products"][pr["key"]]["what"])}</li>'
        for pr in SITE["products"])
    return f"""
<section class="wrap page-head"><h1>{e(t["store_title"])}</h1><p class="lede">{rich(t["store_lede"])}</p></section>
<section class="wrap"><div class="grid2">{''.join(passes)}</div></section>
<section class="wrap"><h2>{e(t["products_title"])}</h2><p>{rich(t["products_lede"])}</p><ul class="plain">{products}</ul>
<p class="fine">{rich(t["store_fine"])}</p></section>"""


def body_roadmap(lang: str) -> str:
    t = T[lang]
    rows = []
    for r in SITE["roadmap"]:
        loc = t["roadmap_items"][r["key"]]
        when = fmt_date(r["date"], lang) if r.get("date") else t["status"][r["status"]]
        rows.append(f'<li class="rm rm-{r["status"]}"><span class="rm-when">{e(when)}</span>'
                    f'<span class="rm-badge">{e(t["status"][r["status"]])}</span>'
                    f'<h3>{e(loc["title"])}</h3><p>{rich(loc["text"])}</p></li>')
    return f"""
<section class="wrap page-head"><h1>{e(t["roadmap_title"])}</h1><p class="lede">{rich(t["roadmap_lede"])}</p></section>
<section class="wrap"><ol class="roadmap">{''.join(rows)}</ol></section>"""


def body_codes(lang: str) -> str:
    t = T[lang]
    active = [c for c in SITE["codes"] if c.get("active")]
    if active:
        lis = "".join(f'<li><code>{e(c["code"])}</code> — {e(c[lang])}</li>' for c in active)
        listing = f'<ul class="codes">{lis}</ul>'
    else:
        listing = f'<p class="card empty">{rich(t["codes_none"])}</p>'
    return f"""
<section class="wrap page-head"><h1>{e(t["codes_title"])}</h1><p class="lede">{rich(t["codes_lede"])}</p>
<p class="fine">{e(t["codes_checked"])}: {fmt_date(SITE["codesChecked"], lang)}</p></section>
<section class="wrap">{listing}<h2>{e(t["codes_how_title"])}</h2><ol class="plain">{''.join(f'<li>{rich(s)}</li>' for s in t["codes_how"])}</ol></section>"""


def body_press(lang: str) -> str:
    t, p = T[lang], prefix(lang)
    facts = "".join(f"<dt>{e(k)}</dt><dd>{rich(v)}</dd>" for k, v in t["press_facts"])
    shots = "".join(
        f'<a href="{p}static/press/{s}.jpg"><img src="{p}static/img/{s}.webp" alt="" loading="lazy" width="1216" height="684"></a>'
        for s in SITE["pressShots"])
    return f"""
<section class="wrap page-head"><h1>{e(t["press_title"])}</h1><p class="lede">{rich(t["press_lede"])}</p></section>
<section class="wrap grid2 press">
  <div><h2>{e(t["press_facts_title"])}</h2><dl class="facts">{facts}</dl></div>
  <div><h2>{e(t["press_about_title"])}</h2>{paras(t["press_about"])}
  <h2>{e(t["press_features_title"])}</h2><ul class="plain">{''.join(f'<li>{rich(x)}</li>' for x in t["press_features"])}</ul></div>
</section>
<section class="wrap"><h2>{e(t["press_images_title"])}</h2><p>{rich(t["press_images_text"])}</p>
  <div class="gallery">{shots}</div>
  <p><a class="btn btn-small" href="{p}static/press/icon.png">{e(t["press_icon"])}</a>
  <a class="btn btn-small btn-ghost" href="{p}static/press/hero.jpg">{e(t["press_hero"])}</a></p></section>
<section class="wrap"><h2>{e(t["press_contact_title"])}</h2><p>{rich(t["press_contact"])}</p></section>"""


def body_privacy(lang: str) -> str:
    t = T[lang]
    return f"""
<section class="wrap page-head"><h1>{e(t["privacy_title"])}</h1></section>
<section class="wrap prose">{paras(t["privacy"])}<p class="fine">{e(t["updated"])}: {fmt_date(SITE["privacyUpdated"], lang)}</p></section>"""


BODIES = {"index": body_index, "news": body_news, "store": body_store, "roadmap": body_roadmap,
          "codes": body_codes, "press": body_press, "privacy": body_privacy}


# ---------------------------------------------------------------- shell

def shell(lang: str, page: str, body: str) -> str:
    t, p = T[lang], prefix(lang)
    title = t["titles"][page]
    full_title = t["site_name"] if page == "index" else f'{title} · {t["site_name"]}'
    desc = t["descriptions"][page]
    canonical = f'{SITE["siteUrl"]}/{page_path(lang, page)}'.replace("/index.html", "/")
    alternates = "".join(
        f'<link rel="alternate" hreflang="{l}" href="{SITE["siteUrl"]}/{page_path(l, page)}">'.replace("/index.html", "/")
        for l in LANGS)
    nav = "".join(
        f'<a href="{href(lang, n, lang)}"{" aria-current=\"page\"" if n == page else ""}>{e(t["nav"][n])}</a>'
        for n in NAV)
    langs = "".join(
        f'<a href="{href(l, page, lang)}" hreflang="{l}" lang="{l}"{" aria-current=\"true\"" if l == lang else ""}>{l.upper()}</a>'
        for l in LANGS)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
{alternates}
<link rel="alternate" hreflang="x-default" href="{SITE["siteUrl"]}/{page_path(LANGS[0], page)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE["siteUrl"]}/static/img/og.jpg">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0e1a16">
<link rel="icon" href="{p}static/img/favicon.png">
<link rel="stylesheet" href="{p}static/style.css">
</head>
<body class="page-{page}">
<a class="skip" href="#main">{e(t["skip"])}</a>
<header class="top"><div class="wrap top-inner">
  <a class="brand" href="{href(lang, 'index', lang)}"><img src="{p}static/img/icon.webp" alt="" width="36" height="36">{e(t["site_name"])}</a>
  <nav class="nav" aria-label="{e(t["nav_label"])}">{nav}</nav>
  <div class="langs" aria-label="{e(t["lang_label"])}">{langs}</div>
</div></header>
<main id="main">{body}</main>
<footer class="foot"><div class="wrap">
  <p>{play_button(lang, " btn-small")} <a href="{e(SITE["community"])}" rel="noopener">{e(t["community"])}</a> ·
  <a href="{e(SITE["bluesky"])}" rel="noopener">Bluesky</a> · <a href="{href(lang, 'press', lang)}">{e(t["nav"]["press"])}</a> ·
  <a href="{href(lang, 'privacy', lang)}">{e(t["titles"]["privacy"])}</a></p>
  <p class="fine">{e(t["disclaimer"])}</p>
</div></footer>
</body>
</html>
"""


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT / "static")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    urls = []
    for lang in LANGS:
        for page in PAGES:
            path = OUT / page_path(lang, page)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(shell(lang, page, BODIES[page](lang)), encoding="utf-8")
            urls.append(f'{SITE["siteUrl"]}/{page_path(lang, page)}'.replace("/index.html", "/"))
    t = T[LANGS[0]]
    not_found = shell(LANGS[0], "index", f"""
<section class="wrap page-head"><h1>{e(t["notfound_title"])}</h1><p class="lede">{e(t["notfound_text"])}</p>
<p><a class="btn" href="index.html">{e(t["nav"]["index"])}</a></p></section>""")
    # GitHub Pages serves 404.html at whatever path was missing, so relative links must become absolute.
    not_found = re.sub(r'(href|src)="(?!https?:|#|mailto:)', rf'\1="{SITE["basePath"]}', not_found)
    (OUT / "404.html").write_text(not_found, encoding="utf-8")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE["siteUrl"]}/sitemap.xml\n',
                                    encoding="utf-8")
    print(f"built {len(urls)} pages into {OUT}")


if __name__ == "__main__":
    build()
