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
--ink:      #121828   (primary dark — hero, marquee, exhibitors, gate — Ночной scheme)
--green:    #1A2035   (MP card background only)
--green-mid:#202840   (mid-dark, used in gate gradients)
--cream:    #F9F6F0   (light section backgrounds — stats, program)
--chalk:    #FAFAF8   (lightest — about, contact, body)
--gold:     #C8A44A   (accent — buttons, borders, icons, numbers)
--gold-dim: #8B6E2F   (dimmer gold, hover states)
--warm:     #7A736B   (secondary text on light sections)
--line:     #E2DAD0   (dividers on light sections)
```

## Section rhythm (light/dark)

| Section | Background |
|---|---|
| Hero | `--ink` (dark) |
| Marquee | `--ink` (dark, mixed gold caps + chalk italic) |
| About | `--chalk` (light) |
| Manifesto quote | `--ink` (dark) |
| Stats | `--cream` (light) |
| Programme | `--cream` (light) |
| Exhibitors | `--ink` (dark) |
| Register | `--ink` (dark) |
| Contact | `--chalk` (light) |

## Typography

- Display / headings: `'Cormorant Garamond'`, weight 600–700 (italic variant for `em` elements)
- Body / nav / buttons: `'Instrument Sans'`, weight 400–700
- Gate signature: `'Pinyon Script'` — loaded from Google Fonts alongside the main pair

## Entry experience (gate → content)

Two screens before the main site:

### 1. Gate — brand animation + role chooser
Full-screen dark (`--ink`) screen, two phases:

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

- **Date:** 20 August 2026
- **Venue:** ENZO Hotel Moscow 5★ (opened spring 2026 — new hotel, relevant detail)
- **Organiser:** Match Point
  - Olga Kharlenok, olga@matchpoints.ru, +7 (910) 400-34-60
  - Daria Ignatieva, daria@matchpoints.ru, +7 (916) 425-01-50
- **Database:** 1,500+ qualified MICE buyers
- **Experience:** 20 years in Russian MICE market
- **Stat:** 80% of Russian corporate MICE trips are international
- **Meeting platform:** EventRocks (external, not yet connected)

## Audience split

- **Buyers** — Russian: MICE agencies, incentive agencies, corporate buyers, PCOs, travel agencies. Invited by Match Point, do not pay.
- **Exhibitors** — International only: hotels 4–5★, DMCs, airlines, congress centres, national tourism offices. Pay to participate.

## Hero structure

- Small `MICE` label (Cormorant, faded gold, spaced caps)
- Main headline: tagline in large italic Cormorant Garamond (`clamp(3.2rem, 6vw, 7.2rem)`, bold, chalk)
- Sub: "No noise. No random visitors. Real business." (caps, faded)
- Meta line: Date · Venue · Format — inline, gold dots as separators; on mobile stacks vertically with hairline dividers
- Single CTA button on desktop; **floating gold bar** fixed to bottom on mobile (appears after hero scroll)
- Background watermark: `20.08` in huge faded gold (`clamp(8rem, 18vw, 22rem)`), bottom-right

## Design decisions (do not revert without asking)

- **Ночной colour scheme** — `--ink: #121828`, midnight blue. Final choice, do not revert.
- **No `s-tag` repeats** — gold line + uppercase label removed from all sections except Contact.
- **Marquee — mixed typefaces** — alternates uppercase Instrument Sans (gold, .8rem) and italic Cormorant Garamond (chalk at low opacity, 1.35rem). 38s speed, architectural top/bottom gold hairlines. Content mixes EN slogans and dates.
- **Stats = editorial rows** — full-width horizontal rows, number left (`clamp(5rem, 10vw, 12rem)`), label right-aligned. Hairline `--line` dividers top and bottom each row. Not a 3-column grid.
- **Programme = 2-column** — Morning / Evening side by side on desktop, vertical hairline separator. Time as tiny gold label above each activity. Activity text in italic Cormorant (`clamp(1rem, 1.6vw, 1.35rem)`). No table grid, no row borders.
- **No numbered pillars** (01/02/03) — removed as cliché; pillars in About are title + description only.
- **SIGNATURE removed from hero** — nav logo already carries the name; repetition in large type was redundant.
- **Manifesto section** — standalone dark section between About and Stats with the key quote.
- **Exhibitors = typographic list** — full-width rows, large italic category name (Cormorant), hover → name turns gold + description fades in right. No icons, no rectangles.
- **Register = dark** — `--ink` background, large italic h2, one meta line, full-width gold button on mobile.
- **About grid = 60/40** — left column (text) dominates editorially. Pillar titles evocative: *"No floor wandering." / "Everyone here books." / "Two debuts, one platform."*
- **Photos planned** — joint portrait of Olga + Dasha → About/Contact; ENZO hotel photos → Hero/Register. Placeholder until ready.

## Mobile (≤620px) — premium patterns

- **Stats horizontal scroll** — peek pattern: cards are 72vw wide, user swipes to see all three. No vertical stack.
- **Floating CTA** — `.mob-cta` fixed bottom bar with gold button. Appears after hero bottom exits viewport, hides when Register section is in view. JS-driven.
- **Hero buttons hidden** on mobile — replaced by floating CTA.
- **vw typography** — hero tagline `14vw`, manifesto `8vw`, register h2 `13vw`, stat numbers `22vw`.
- **Padding** — 80px vertical, 24px horizontal (was 64/20).
- Gate panels stack vertically; architectural lines hidden.

## What not to change without asking

- The gate animation (Phase 1 pen + Phase 2 role panels) — considered final
- The "two debuts" angle in pillar 03 (MICE Signature inaugural + ENZO Hotel new opening)
- The quote: "We do not waste your time. We do not waste theirs."
- The tagline: "No noise. No random visitors. Real business."
- The Ночной colour scheme (`--ink: #121828`)

## Deploy

- GitHub Pages: https://o6594340-sys.github.io/mice-signature/
- Working folder: `c:\Users\usrr\OneDrive\Документы\Projects\mice-signature` (внутри монорепо `Projects`)
- Remotes: `origin` → Russia-landing-version1, `github` → mice-signature (GitHub Pages)
- После каждого изменения — из корня монорепо (`Projects`):
  ```
  git add mice-signature/index.html mice-signature/CLAUDE.md
  git commit -m "..."
  git push origin main
  git subtree split --prefix=mice-signature -b deploy-mice
  git push github deploy-mice:main --force
  git branch -D deploy-mice
  ```
