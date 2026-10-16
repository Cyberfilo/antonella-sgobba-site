# antonella.menghi.dev

Personal website of Antonella Sgobba, luxury hospitality executive, Milan. Bilingual (English at `/`, Italian at `/it/`), static, no JavaScript, no cookies.

## How it is built

- `src/content.py` holds every word on the site, English and Italian, plus the career timeline and the press list.
- `src/build.py` turns the content into HTML and writes the finished site into `docs/`.
- `src/assets/site.css` is the only stylesheet. `src/assets/img/` holds the portrait variants, the OG image and the icons.

Rebuild after any change:

```
python3 src/build.py
```

Preview locally:

```
cd docs && python3 -m http.server 8765
```

## Hosting

GitHub Pages serves `docs/` on the `main` branch. The custom domain is set by `docs/CNAME` (`antonella.menghi.dev`). DNS: a CNAME record `antonella` pointing to `cyberfilo.github.io`, DNS-only (grey cloud) in Cloudflare so GitHub can issue the certificate.

## Portrait

The black-and-white portrait came from the Holding Carisma team page (Webflow CDN, file "antonella sgobba4080"), recovered through the Wayback Machine after the page stopped listing her. The hero version has the studio backdrop keyed out. The October 2026 press portrait belongs to Italian Hospitality Collection and is not used.

## Before adding content

See `../03_Checklist_before_publishing.md` in the source pack: figures to confirm (Grand Hotel San Pietro), titles as printed in the press, Cornell credential wording, logo and client-name permissions.
