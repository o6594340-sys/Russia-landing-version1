# CLAUDE.md — MICE Signature

## Project

Single static HTML file for a B2B MICE event site. No framework, no build step — edit `index.html` directly.

## Rules

- **One file only.** All CSS and JS stay inline in `index.html`. Do not create separate `.css` or `.js` files.
- **No prices on the site.** Package prices ($1,600–$3,800) are internal only — never add them to any public-facing section.
- **Exhibitors = international companies only.** Russian companies do not exhibit. Do not imply otherwise in copy.
- **EventRocks button** — the "Open Meeting Planner" button uses `href="#"` as placeholder. Replace with real URL when provided. Do not invent or guess the URL.
- **Language switcher** — all user-facing text must have both `data-en` and `data-ru` attributes. Never add EN-only text without a RU translation.

## Design tokens

```
--ink:   #14140F   (primary dark, almost-black warm)
--green: #1C1814   (dark sections: stats, register, exhibitors, MP card)
--cream: #F9F6F0   (light section backgrounds)
--chalk: #FAFAF8   (lightest background, body)
--gold:  #C8A44A   (accent — buttons, borders, icons, numbers)
--warm:  #7A736B   (secondary text)
--line:  #E2DAD0   (dividers)
```

## Typography

- Display / headings: `'Space Grotesk'`, weight 700
- Body / nav / buttons: `'Jost'`, weight 300–600

## Key content facts

- **Date:** 20 May 2026
- **Venue:** ENZO Hotel Moscow 5★ (opened spring 2026 — new hotel, relevant detail)
- **Organiser:** Match Point, Olga Kharlenok, olga@matchpoints.ru, +7 (910) 400-34-60
- **Database:** 1,500+ qualified MICE buyers
- **Experience:** 20 years in Russian MICE market
- **Stat:** 80% of Russian corporate MICE trips are international
- **Meeting platform:** EventRocks (external, not yet connected)

## Audience split

- **Buyers** — Russian: MICE agencies, incentive agencies, corporate buyers, PCOs, travel agencies. Invited by Match Point, do not pay.
- **Exhibitors** — International only: hotels 4–5★, DMCs, airlines, congress centres, national tourism offices. Pay to participate.

## What not to change without asking

- The "two debuts" angle in pillar 03 (MICE Signature inaugural + ENZO Hotel new opening)
- The quote: "We do not waste your time. We do not waste theirs."
- The tagline: "No noise. No random visitors. Real business."
