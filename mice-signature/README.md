# MICE Signature — Event Website

Bilingual single-page website for **MICE Signature** — a debut B2B MICE workshop + evening cocktail, Moscow, 20 August 2026.

Organised by [Match Point](https://matchpoints.ru) (Olga Kharlenok, Daria Ignatieva).

## What this site is

An info site for international exhibitors and invited Russian MICE buyers. **Registration is closed** (event is fully booked) — all CTA buttons show "Registration closed" instead of a sign-up link. Buyers can still reach the organisers via a "Get in Touch" WhatsApp link.

**Prices are not shown on the site.**

## Stack

- Single `index.html` file — inline CSS + vanilla JS, no build step
- Fonts: Cormorant Garamond + Instrument Sans + Pinyon Script via Google Fonts
- GSAP 3.12.5 (CDN) for gate animation
- EN / RU language switcher (sessionStorage)
- Responsive: CSS Grid + Flexbox, breakpoints at 1000px and 620px

## Files

| File | Purpose |
|------|---------|
| `index.html` | The website |
| `brief.md` | Event brief: program, audience, packages, site structure |
| `research.md` | Competitor analysis, final design decisions, color palette |
| `about workshop.pdf` | Source materials (Russian) |
| `business program.docx` | Source materials (Russian) |

## Sections

1. **Hero** — event name, date, venue, two CTAs
2. **Marquee strip** — gold scrolling ticker
3. **About** — concept, quote, three pillars
4. **Stats** — 1,500+ buyers / 20 years / 80% international
5. **Programme** — two business sessions schedule
6. **Exhibitors** — six exhibitor categories (international only)
7. **Register** — registration closed; buyers see a "Get in Touch" WhatsApp link instead
8. **Contact** — Olga Kharlenok, Match Point card
9. **Footer**

## To deploy

GitHub Pages, custom domain **micesignature.ru** (DNS pending). See `CLAUDE.md` for the exact deploy commands (subtree split from the monorepo).

## Contact

Olga Kharlenok · olga@matchpoints.ru · +7 (910) 400-34-60
Daria Ignatieva · daria@matchpoints.ru · +7 (916) 425-01-50
matchpoints.ru
