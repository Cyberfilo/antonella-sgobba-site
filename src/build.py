#!/usr/bin/env python3
"""Static site generator for antonella.menghi.dev.

Reads content.py, writes HTML into ../docs (GitHub Pages source).
Run:  python3 build.py
"""
import html
import os
import shutil
from pathlib import Path

from content import DOMAIN, LANGS, LINKEDIN, PATHS, PRESS, TIMELINE

SRC = Path(__file__).resolve().parent
OUT = SRC.parent / "docs"
ASSET_VERSION = "2"
from PIL import Image as _Img
HERO_W, HERO_H = _Img.open(SRC / "assets/img/hero-1000.png").size


def e(s: str) -> str:
    return html.escape(s, quote=True)


# ---------- shared fragments -------------------------------------------------

MONOGRAM = (
    '<svg class="monogram" viewBox="0 0 100 100" role="img" aria-label="AS monogram">'
    '<circle cx="50" cy="50" r="47" fill="none" stroke="currentColor" stroke-width="1.5"/>'
    '<text x="50" y="66" text-anchor="middle" font-family="\'Cormorant Garamond\',Georgia,serif" '
    'font-size="46" font-weight="500" letter-spacing="1"><tspan class="m-a">A</tspan><tspan class="m-s">S</tspan></text>'
    '</svg>'
)


def head(L, page_id, title, description, extra=""):
    lang = L["lang"]
    path = PATHS[page_id][lang]
    other = "it" if lang == "en" else "en"
    canonical = DOMAIN + path
    alt_en = DOMAIN + PATHS[page_id]["en"]
    alt_it = DOMAIN + PATHS[page_id]["it"]
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Antonella Sgobba",
        "jobTitle": "Group Director of Commercial Strategy",
        "worksFor": {"@type": "Organization", "name": "Italian Hospitality Collection"},
        "address": {"@type": "PostalAddress", "addressLocality": "Milan", "addressCountry": "IT"},
        "url": DOMAIN + "/",
        "image": DOMAIN + "/assets/img/portrait-square-800.jpg",
        "sameAs": [LINKEDIN],
        "knowsLanguage": ["it", "en"],
    }
    import json
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="it" href="{alt_it}">
<link rel="alternate" hreflang="x-default" href="{alt_en}">
<meta property="og:type" content="profile">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{DOMAIN}/assets/img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{'en_GB' if lang == 'en' else 'it_IT'}">
<meta property="og:locale:alternate" content="{'it_IT' if lang == 'en' else 'en_GB'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0E1F38">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={ASSET_VERSION}">
<script type="application/ld+json">{json.dumps(person, ensure_ascii=False)}</script>
{extra}
</head>
"""


def header(L, page_id):
    lang = L["lang"]
    other = "it" if lang == "en" else "en"
    home = PATHS["home"][lang]
    items = []
    for pid, label in L["nav"]:
        cur = ' aria-current="page"' if pid == page_id else ""
        items.append(f'<li><a href="{PATHS[pid][lang]}"{cur}>{e(label)}</a></li>')
    switch = PATHS[page_id][other]
    return f"""<a class="skip" href="#main">{e(L['skip'])}</a>
<header class="site-head">
  <div class="wrap head-row">
    <a class="brand" href="{home}" aria-label="{e(L['name'])}, home">{MONOGRAM}<span class="brand-name">{e(L['name'])}</span></a>
    <nav class="site-nav" aria-label="Main">
      <ul>{''.join(items)}</ul>
    </nav>
    <a class="lang" href="{switch}" lang="{other}" hreflang="{other}" title="{e(L['switch_title'])}">{e(L['switch_label'])}</a>
  </div>
</header>
"""


def footer(L):
    lang = L["lang"]
    return f"""<footer class="site-foot">
  <div class="wrap foot-grid">
    <div class="foot-id">{MONOGRAM}<p><strong>{e(L['name'])}</strong><br>{e(L['footer_note'])}</p></div>
    <ul class="foot-links">
      <li><a href="{LINKEDIN}" rel="me noopener" target="_blank">{e(L['linkedin_label'])}</a></li>
      <li><a href="{PATHS['contact'][lang]}">{e(dict(L['nav'])['contact'])}</a></li>
      <li><a href="{PATHS['privacy'][lang]}">{e(L['footer_privacy'])}</a></li>
    </ul>
    <p class="foot-rights">{e(L['footer_rights'])}</p>
  </div>
</footer>
</body>
</html>
"""


def page_band(h1, lead):
    return f"""<section class="band">
  <div class="wrap">
    <h1>{e(h1)}</h1>
    <p class="lead">{e(lead)}</p>
  </div>
</section>
"""


def portrait_picture(alt, sizes="(min-width: 900px) 46vw, 100vw", cls="portrait"):
    return f"""<picture class="{cls}">
  <source type="image/webp" srcset="/assets/img/portrait-600.webp 600w, /assets/img/portrait-1000.webp 1000w, /assets/img/portrait-1600.webp 1600w" sizes="{sizes}">
  <img src="/assets/img/portrait-1000.jpg" srcset="/assets/img/portrait-600.jpg 600w, /assets/img/portrait-1000.jpg 1000w, /assets/img/portrait-1600.jpg 1600w" sizes="{sizes}" width="1000" height="1250" alt="{e(alt)}" fetchpriority="high" decoding="async">
</picture>"""


# ---------- pages ------------------------------------------------------------

def page_home(L):
    H = L["home"]
    lang = L["lang"]
    W = L["work"]
    ledger = "".join(
        f'<div class="ledger-item"><p class="ledger-num">{e(n)}</p><p class="ledger-label">{e(t)}</p></div>'
        for n, t in H["ledger"]
    )
    cases = "".join(
        f'<li><a href="{PATHS["work"][lang]}#{c["id"]}"><span class="case-title">{e(c["title"])}</span>'
        f'<span class="case-meta">{e(c["place"])}, {e(c["years"])}</span>'
        f'<span class="case-short">{e(c["short"])}</span></a></li>'
        for c in W["cases"]
    )
    outlets = "".join(f"<li>{e(o)}</li>" for o in H["outlets"])
    body = f"""<main id="main">
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-text">
      <p class="hero-name">{e(L['name'])}</p>
      <h1 class="hero-h1">{e(H['headline'])} <span class="hero-h1-2">{e(H['headline_2'])}</span></h1>
      <p class="hero-role">{e(L['role'])}</p>
      <p class="hero-actions"><a class="btn" href="{PATHS['about'][lang]}">{e(H['cta_primary'])}</a><a class="btn btn-quiet" href="{LINKEDIN}" rel="me noopener" target="_blank">{e(H['cta_secondary'])}</a></p>
    </div>
    <div class="hero-figure">
      <span class="ring" aria-hidden="true"></span>
      <picture class="portrait">
        <source type="image/webp" srcset="/assets/img/hero-1000.webp 1000w, /assets/img/hero-1600.webp 1600w" sizes="(min-width: 900px) 40vw, 80vw">
        <img src="/assets/img/hero-1000.png" width="{HERO_W}" height="{HERO_H}" alt="{e(H['portrait_alt'])}" fetchpriority="high" decoding="async">
      </picture>
    </div>
  </div>
</section>

<section class="ledger">
  <div class="wrap ledger-grid">{ledger}</div>
</section>

<section class="section">
  <div class="wrap two-col">
    <h2>{e(H['intro_heading'])}</h2>
    <div>
      <p class="prose-lg">{e(H['intro'])}</p>
      <p><a class="more" href="{PATHS['about'][lang]}">{e(H['intro_link'])}</a></p>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    <div class="two-col">
      <h2>{e(H['work_heading'])}</h2>
      <p class="prose-lg">{e(H['work_lead'])}</p>
    </div>
    <ul class="case-list">{cases}</ul>
    <p class="align-end"><a class="more" href="{PATHS['work'][lang]}">{e(H['work_link'])}</a></p>
  </div>
</section>

<section class="section">
  <div class="wrap two-col">
    <h2>{e(H['thread_heading'])}</h2>
    <p class="prose-lg">{e(H['thread'])}</p>
  </div>
</section>

<section class="section section-navy">
  <div class="wrap two-col">
    <h2>{e(H['press_heading'])}</h2>
    <div>
      <p class="prose-lg">{e(H['press_lead'])}</p>
      <ul class="outlets">{outlets}</ul>
      <p><a class="more more-light" href="{PATHS['press'][lang]}">{e(H['press_link'])}</a></p>
    </div>
  </div>
</section>
</main>
"""
    return head(L, "home", H["title"], H["description"]) + "<body class=\"home\">" + header(L, "home") + body + footer(L)


def page_about(L):
    A = L["about"]
    lang = L["lang"]
    bio = "".join(f"<p>{e(p)}</p>" for p in A["bio"])
    themes = "".join(f"<div class=\"theme\"><h3>{e(t)}</h3><p>{e(d)}</p></div>" for t, d in A["themes"])
    rows = []
    for years, org, place, title, imp_en, imp_it in TIMELINE:
        imp = imp_en if lang == "en" else imp_it
        rows.append(
            f'<li class="tl-row"><p class="tl-years">{e(years)}</p>'
            f'<div class="tl-body"><h3 class="tl-org">{e(org)}<span class="tl-place">{e(place)}</span></h3>'
            f'<p class="tl-title">{e(title)}</p><p class="tl-impact">{e(imp)}</p></div></li>'
        )
    edu = "".join(
        f'<li class="edu-row"><p class="edu-year">{e(y)}</p><div><p class="edu-school">{e(s)}</p><p class="edu-what">{e(w)}</p></div></li>'
        for y, s, w in A["education"]
    )
    body = f"""<main id="main">
{page_band(A['h1'], A['lead'])}
<section class="section">
  <div class="wrap about-grid">
    <div class="about-portrait">
      <picture>
        <source type="image/webp" srcset="/assets/img/portrait-600.webp 600w, /assets/img/portrait-1000.webp 1000w" sizes="(min-width: 900px) 34vw, 100vw">
        <img src="/assets/img/portrait-600.jpg" srcset="/assets/img/portrait-600.jpg 600w, /assets/img/portrait-1000.jpg 1000w" sizes="(min-width: 900px) 34vw, 100vw" width="600" height="750" alt="{e(L['home']['portrait_alt'])}" loading="lazy" decoding="async">
      </picture>
      <p class="caption"><a href="{LINKEDIN}" rel="me noopener" target="_blank">{e(A['linkedin_text'])}</a></p>
    </div>
    <div class="about-bio prose">{bio}</div>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    <h2 class="h2-rule">{e(A['themes_heading'])}</h2>
    <div class="themes">{themes}</div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <h2 class="h2-rule">{e(A['timeline_heading'])}</h2>
    <ol class="timeline" reversed>{''.join(rows)}</ol>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap two-col">
    <h2>{e(A['education_heading'])}</h2>
    <div>
      <ul class="edu">{edu}</ul>
      <h3 class="h3-small">{e(A['languages_heading'])}</h3>
      <p>{e(A['languages'])}</p>
    </div>
  </div>
</section>
</main>
"""
    return head(L, "about", A["title"], A["description"]) + "<body>" + header(L, "about") + body + footer(L)


def page_expertise(L):
    X = L["expertise"]
    areas = "".join(f'<div class="area"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in X["areas"])
    method = "".join(
        f'<li class="phase"><div class="phase-head"><h3>{e(t)}</h3><p class="phase-when">{e(w)}</p></div><p>{e(d)}</p></li>'
        for t, w, d in X["method"]
    )
    principles = "".join(f"<li>{e(p)}</li>" for p in X["principles"])
    body = f"""<main id="main">
{page_band(X['h1'], X['lead'])}
<section class="section">
  <div class="wrap">
    <h2 class="h2-rule">{e(X['areas_heading'])}</h2>
    <div class="areas">{areas}</div>
  </div>
</section>

<section class="section section-navy">
  <div class="wrap">
    <div class="two-col">
      <h2>{e(X['method_heading'])}</h2>
      <p class="prose-lg">{e(X['method_lead'])}</p>
    </div>
    <ol class="phases">{method}</ol>
    <div class="two-col principles">
      <h3>{e(X['principles_heading'])}</h3>
      <ul class="plain">{principles}</ul>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap two-col">
    <h2>{e(X['markets_heading'])}</h2>
    <p class="prose-lg">{e(X['markets'])}</p>
  </div>
  <div class="wrap two-col">
    <h2>{e(X['brands_heading'])}</h2>
    <p class="prose-lg">{e(X['brands'])}</p>
  </div>
</section>
</main>
"""
    return head(L, "expertise", X["title"], X["description"]) + "<body>" + header(L, "expertise") + body + footer(L)


def page_work(L):
    W = L["work"]
    lab = W["labels"]
    blocks = []
    for c in W["cases"]:
        did = "".join(f"<li>{e(d)}</li>" for d in c["did"])
        blocks.append(f"""<article class="case" id="{c['id']}">
  <header class="case-head">
    <p class="case-kind">{e(c['kind'])}</p>
    <h2>{e(c['title'])}</h2>
    <p class="case-place">{e(c['place'])}, {e(c['years'])}</p>
  </header>
  <div class="case-body">
    <h3>{e(lab['challenge'])}</h3>
    <p>{e(c['challenge'])}</p>
    <h3>{e(lab['did'])}</h3>
    <ul>{did}</ul>
    <h3>{e(lab['result'])}</h3>
    <p class="case-result">{e(c['result'])}</p>
    <p class="case-context"><span class="ctx-label">{e(lab['context'])}.</span> {e(c['context'])}</p>
  </div>
</article>""")
    body = f"""<main id="main">
{page_band(W['h1'], W['lead'])}
<section class="section">
  <div class="wrap cases">{''.join(blocks)}</div>
</section>
</main>
"""
    return head(L, "work", W["title"], W["description"]) + "<body>" + header(L, "work") + body + footer(L)


def page_press(L):
    P = L["press"]
    lang = L["lang"]
    items = []
    for iso, d_en, d_it, outlet, title, url, t_en, t_it, n_en, n_it in PRESS:
        d = d_en if lang == "en" else d_it
        t = t_en if lang == "en" else t_it
        n = n_en if lang == "en" else n_it
        items.append(f"""<li class="press-row">
  <p class="press-date"><time datetime="{iso}">{e(d)}</time></p>
  <div class="press-body">
    <p class="press-outlet">{e(outlet)}</p>
    <h2 class="press-title"><a href="{url}" rel="noopener" target="_blank" lang="it">{e(title)}</a></h2>
    <p class="press-as">{e(P['her_title_label'])}: {e(t)}</p>
    <p class="press-note">{e(n)}</p>
  </div>
</li>""")
    body = f"""<main id="main">
{page_band(P['h1'], P['lead'])}
<section class="section">
  <div class="wrap">
    <ol class="press-list" reversed>{''.join(items)}</ol>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap two-col">
    <h2>{e(P['also_heading'])}</h2>
    <p class="prose-lg">{e(P['also'])} <a href="{LINKEDIN}" rel="me noopener" target="_blank">LinkedIn</a>.</p>
  </div>
</section>
</main>
"""
    return head(L, "press", P["title"], P["description"]) + "<body>" + header(L, "press") + body + footer(L)


def page_contact(L):
    C = L["contact"]
    body = f"""<main id="main">
{page_band(C['h1'], C['lead'])}
<section class="section">
  <div class="wrap contact">
    <p><a class="btn" href="{LINKEDIN}" rel="me noopener" target="_blank">{e(C['linkedin_cta'])}</a></p>
    <p class="prose-lg">{e(C['based'])}</p>
    <p class="muted">{e(C['note'])}</p>
  </div>
</section>
</main>
"""
    return head(L, "contact", C["title"], C["description"]) + "<body>" + header(L, "contact") + body + footer(L)


def page_privacy(L):
    V = L["privacy"]
    paras = "".join(f"<p>{e(p)}</p>" for p in V["body"])
    body = f"""<main id="main">
{page_band(V['h1'], '')}
<section class="section">
  <div class="wrap prose narrow">{paras}</div>
</section>
</main>
"""
    extra = '<meta name="robots" content="noindex">'
    return head(L, "privacy", V["title"], V["description"], extra) + "<body>" + header(L, "privacy") + body + footer(L)


def page_404():
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found, Antonella Sgobba</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500&family=Source+Sans+3:wght@400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={ASSET_VERSION}">
</head>
<body>
<main id="main">
<section class="band"><div class="wrap"><h1>Page not found</h1><p class="lead">The page you asked for is not here. <a href="/">Go to the home page</a> or <a href="/it/">alla pagina iniziale</a>.</p></div></section>
</main>
</body></html>
"""


BUILDERS = {
    "home": page_home, "about": page_about, "expertise": page_expertise,
    "work": page_work, "press": page_press, "contact": page_contact, "privacy": page_privacy,
}


def write(path: str, content: str):
    target = OUT / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copytree(SRC / "assets", OUT / "assets")

    urls = []
    for lang, L in LANGS.items():
        for pid, builder in BUILDERS.items():
            path = PATHS[pid][lang]
            write(path, builder(L))
            if pid != "privacy":
                urls.append((pid, lang, DOMAIN + path))

    write("/404.html", page_404())
    (OUT / "CNAME").write_text("antonella.menghi.dev\n")
    (OUT / ".nojekyll").write_text("")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")

    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for pid, lang, url in urls:
        sm.append(f"  <url><loc>{url}</loc>"
                  f'<xhtml:link rel="alternate" hreflang="en" href="{DOMAIN}{PATHS[pid]["en"]}"/>'
                  f'<xhtml:link rel="alternate" hreflang="it" href="{DOMAIN}{PATHS[pid]["it"]}"/>'
                  f"</url>")
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n")

    n = sum(1 for _ in OUT.rglob("*.html"))
    print(f"built {n} pages into {OUT}")


if __name__ == "__main__":
    main()
