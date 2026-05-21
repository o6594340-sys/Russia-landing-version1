# MICE Signature — Event Website

Bilingual single-page website for **MICE Signature** — a debut B2B MICE workshop + evening cocktail, Moscow, 20 May 2026.

Organised by [Match Point](https://matchpoints.ru) (Olga Kharlenok).

## What this site is

A portal for registered participants — international exhibitors and invited Russian MICE buyers — to view event info and schedule pre-scheduled B2B meetings via EventRocks platform.

**Prices are not shown on the site.**

## Stack

- Single `index.html` file — inline CSS + vanilla JS, no build step
- Fonts: Space Grotesk (700) + Jost via Google Fonts
- EN / RU language switcher (localStorage)
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
7. **Register** — CTA to EventRocks meeting planner
8. **Contact** — Olga Kharlenok, Match Point card
9. **Footer**

## To deploy

Static file — drag `index.html` to any hosting: GitHub Pages, Netlify, or organiser's server.

## Pending

- Replace `href="#"` on the "Open Meeting Planner" button with the actual EventRocks URL once the platform is set up.

## Contact

Olga Kharlenok · olga@matchpoints.ru · +7 (910) 400-34-60 · matchpoints.ru
