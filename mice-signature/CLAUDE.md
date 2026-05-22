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

- Display / headings: `'Cormorant Garamond'`, weight 600–700 (italic variant for `em` elements)
- Body / nav / buttons: `'Instrument Sans'`, weight 400–700
- Gate signature: `'Pinyon Script'` — loaded from Google Fonts alongside the main pair

## Entry experience (gate → content)

Two screens before the main site:

### 1. Gate — brand animation + role chooser
Full-screen dark (`#141018`) screen, two phases:

**Phase 1 — pen sweeps MICE + writes Signature:**
- Large white Cormorant Garamond Bold letters **M I C E** (`clamp(5.5rem, 17vw, 15rem)`, letter-spacing 0.18em), initially opacity 0
- Gold pen-tip circle (`r=3.5`, gold glow) sweeps left→right along a nearly flat arc at cap baseline
- Letters light up (0.18s fade) as pen reaches each letter's left edge — binary search finds exact path length for each trigger point
- After MICE sweep: pen moves to start of **Signature** SVG text
- **Wipe-mask technique**: `<rect id="gsig-wipe">` inside SVG `<mask>` grows width 0→890 (viewBox coords), revealing Pinyon Script "Signature" left→right; pen tracks mathematically on the leading edge via `getScreenCTM()`
- Signature: Pinyon Script, `font-size: 168px`, SVG `width: min(90vw, 820px)`, viewBox `0 0 860 200`
- MICE:Signature visual ratio ≈ 1.6:1 (contrast-luxury proportions)
- **GSAP** (CDN `cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js`): MICE sweep 3.6s `power1.inOut`, Signature wipe 4.2s `power1.inOut`

**Phase 2 — role panels:**
- After 1.1s pause: brand fades (0.8s), two panels materialise from blur
- Left: **Exhibitor / Экспонент**, Right: **Buyer / Посетитель** — both languages shown simultaneously
- Gold vertical divider with centre dot
- Hover: radial gold glow + bottom gold border + "Enter →" arrow fades in
- Click → `chooseRole(role)` → stores role in `sessionStorage`, shows `#main`
- If role already in `sessionStorage` on load: gate skipped, go straight to content

**CSS naming note:** gate panels use `.gate-panels.gate-revealed` (not `.reveal`) to avoid conflict with scroll-reveal base class.

### 2. Content — role-specific views
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
