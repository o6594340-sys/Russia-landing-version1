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
--ink:   #141018   (primary dark, aubergine-black — violet undertone, cold vs warm gold tension)
--green: #1A1520   (dark sections: stats, register, exhibitors, MP card)
--cream: #F9F6F0   (light section backgrounds)
--chalk: #FAFAF8   (lightest background, body)
--gold:  #C8A44A   (accent — buttons, borders, icons, numbers)
--warm:  #7A736B   (secondary text)
--line:  #E2DAD0   (dividers)
```

## Typography

- Display / headings: `'Space Grotesk'`, weight 700
- Body / nav / buttons: `'Jost'`, weight 300–600
- Splash signature: `'Pinyon Script'` — loaded from Google Fonts alongside the main pair

## Entry experience (splash → gate → content)

Three screens before the main site:

### 1. Splash — signature animation
- Full-screen `#141018` overlay (`#splash`)
- "MICE Signature" rendered in **Pinyon Script** inside an SVG
- **Technique:** SVG `<mask>` + growing white stroke. The text is hidden behind a black mask rect; a path (`#writing-path`) with `stroke="white" stroke-width="160"` grows via `stroke-dashoffset` animation, revealing the Pinyon Script text beneath as the "pen" passes through
- Path is built **dynamically in JS** after `document.fonts.ready` using `getStartPositionOfChar()` / `getEndPositionOfChar()` to measure actual letter positions
- Per-letter path logic: capitals enter at cap-height (~y 72), lowercase at x-height (~y 112), descenders exit below baseline; connecting arcs simulate pen lifts between letters
- **GSAP** (loaded from CDN: `cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js`) drives the animation — duration 5.5s, ease `power1.inOut`
- Gold pen-tip `<circle>` tracks the leading edge using `getPointAtLength()` on the actual animated `stroke-dashoffset` attribute (not time-progress, to stay in sync with easing)
- After drawing: 2.2s pause → splash fades out → gate appears
- If role is already in `sessionStorage`, splash is skipped entirely

### 2. Gate — role chooser
- Full-screen two-panel screen (`#gate`), dark background
- Left: **Exhibitor / Экспонент** — both languages shown simultaneously (no switcher)
- Right: **Buyer / Посетитель** — same
- Gold vertical divider with centre dot
- Hover: radial gold glow + bottom gold border + "Enter →" arrow fades in
- Click → `chooseRole(role)` → stores role in `sessionStorage`, shows `#main`

### 3. Content — role-specific views
- `#main` is `hidden` until role is chosen
- `body.body-role-exhibitor` or `body.body-role-buyer` class controls visibility
- Elements with class `.ex-only` show for exhibitors, `.buyer-only` show for buyers
- Role-specific copy: hero headline, register section heading/body/CTA, nav CTA, exhibitors section tag
- Language switcher (EN/RU) works normally within each view
- "← Switch role" button in nav resets `sessionStorage` and returns to gate

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
