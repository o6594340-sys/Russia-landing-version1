# CLAUDE.md — MICE Signature

## Project

Single static HTML file for a B2B MICE event site. No framework, no build step — edit `index.html` directly.

## Rules

- **One file only.** All CSS and JS stay inline in `index.html`. Do not create separate `.css` or `.js` files.
- **No prices on the site.** Package prices ($1,600–$3,800) are internal only — never add them to any public-facing section.
- **Exhibitors = international companies only.** Russian companies do not exhibit. Do not imply otherwise in copy.
- **Registration is closed.** All former "Registration" / "Apply to Exhibit" CTA buttons (nav, mobile menu, hero, mobile floating bar, Register section) are now inert `<span class="reg-closed">` elements reading "Registration closed" / "Регистрация закрыта" for both roles — `.reg-closed` sets `pointer-events: none; opacity: .45`. The old Google Forms links were removed. Exception: the buyer-only button in the Register section stays a live link — "Get in Touch" / "Связаться с нами" via WhatsApp (`https://api.whatsapp.com/send?phone=79164250150`), since buyers were never open-registration (personal invitation only). Don't add new links that imply applications are still open (e.g. an "apply" link pointing at `#register`).
- **Language switcher** — all user-facing text must have both `data-en` and `data-ru` attributes. Never add EN-only text without a RU translation.

## Design tokens

```
--ink:      #1A1610   (primary dark — hero, marquee, exhibitors, gate — Ночной янтарь)
--green:    #211C14   (MP card background only)
--green-mid:#282218   (mid-dark, used in gate gradients)
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
- Left: **Exhibitor / Экспонент**, Right: **Buyer / Байер** — both languages shown simultaneously
- Gold vertical divider with centre dot
- Hover: radial gold glow + bottom gold border + "Enter →" arrow fades in
- Click → `chooseRole(role)` → fades out gate, shows **consent screen** (`#consent-screen`)
- If role already in `sessionStorage` on load: gate skipped, go straight to content (no consent re-shown)
- **Skip button** — `#gate-skip` appears top-right after 2s (`setTimeout 2000`), calls `skipGate()` which kills all GSAP tweens and immediately shows panels. Hidden on desktop at rest (opacity 0), fades in. Do not remove.

**CSS naming note:** gate panels use `.gate-panels.gate-revealed` (not `.reveal`) to avoid conflict with scroll-reveal base class.

### 1.5. Consent screen (`#consent-screen`)
Separate full-screen dark step between role panels and main content:
- Has `hidden` attribute in HTML (not just CSS `display:none`) — removed via JS when shown
- Shows MICE Signature gold logo + role label + bilingual heading "Before you enter / Прежде чем войти"
- 3 checkboxes: `cs-pd` (personal data consent, **required**), `cs-marketing`, `cs-distribution`
- Each checkbox has RU text + `.gc-en-line` EN line (italic, opacity .5)
- "Enter →" button calls `enterSite()` — validates `cs-pd` checked, then fades to `#main`
- "← Change role / Сменить роль" calls `resetRole()` — returns to gate panels (no animation replay)
- `_pendingRole` variable holds selected role until `enterSite()` finalises it
- `enterSite()` calls `applyRole()`, `setLang()`, `animateHeroTagline()`, scroll-reveal inits

### 2. Content — role-specific views
- `#main` is `hidden` until role is chosen
- `body.body-role-exhibitor` or `body.body-role-buyer` class controls visibility
- Elements with class `.ex-only` show for exhibitors, `.buyer-only` show for buyers
- Role-specific copy: hero headline, register section heading/body/CTA, nav CTA, exhibitors section tag
- Language switcher (EN/RU) works normally within each view
- "← Switch role" button in nav resets `sessionStorage` and returns to gate
- **Nav section links** — `.nav-links` div between logo and nav-right: Programme / Exhibitors / Contact anchors. Hidden on mobile (≤620px). Styled as `.nav-link` (Instrument Sans, .65rem, uppercase, opacity .32, gold on hover).

**Role-specific Exhibitors section heading:**
- Buyers see: "International partners. Russian market." / "Международные партнёры. Российский рынок."
- Exhibitors see: "Meet your audience." / "Ваша аудитория."
- Both h2 tags carry `.buyer-only` / `.ex-only` respectively

**Role-specific Exhibitors section (`.ex-items` list):**
- Buyers see: Hotels & Resorts 5★, DMCs & Ground Operators, Destinations & Tourism Boards, Airlines & Charter, MICE Venues & Congress Centres, Services & Technology
- Exhibitors see: MICE Agencies, Event Agencies & Producers, Corporate Buyers, PCOs & Travel Agencies
- CSS cascade fix required: `.ex-item.ex-only { display: none }` and `.ex-item.buyer-only { display: none }` must be declared **after** `.ex-item { display: flex }` to win specificity

**Role-specific About pillars (`.pillars` grid):**
- Exhibitors (`.ex-only` pillars): "Только нужные встречи" / "Те, кто вывозит группы" / "Два дебюта, одна платформа"
- Buyers (`.buyer-only` pillars): "Они приехали к вам" / "Азия. Ближний Восток. СНГ." / "Встречи и немного магии."
- Same CSS cascade fix applies: `.pillar.ex-only` / `.pillar.buyer-only` declared after `.pillar { display: grid }`

**Buyer pillar 01 ("Они приехали к вам") description:**
- RU: "Каждый зарубежный партнёр приехал в Москву специально ради этой встречи. Не выставка с тысячами случайных контактов, а переговоры, которые действительно стоят вашего времени."
- EN: "Every international partner flew in to Moscow specifically for this meeting. Not a trade show with thousands of random contacts — but negotiations that are truly worth your time."

**CSS role visibility fix (specificity 0,2,0 — overrides .btn-fill and .flex):**
```css
.body-role-buyer .ex-only { display: none; }
.body-role-exhibitor .buyer-only { display: none; }
```
These must be declared after all component display rules.

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
  - Buyers are split into two groups for the programme: morning (special breakfast — not publicly highlighted) and evening (cocktail). Do not draw attention to this split in copy; mention only "pre-scheduled meetings, networking, and surprises from the organizers."
- **Exhibitors** — International only: hotels 4–5★, DMCs, airlines, congress centres, national tourism offices. Pay to participate.
- **Scale:** up to ~30 exhibitors total. Never write copy implying global or mass scale ("world MICE in one hall", "весь мировой MICE" etc.).

## Hero structure

- Small `MICE` label (Cormorant, faded gold, spaced caps)
- Main headline: tagline in large italic Cormorant Garamond (`clamp(3.2rem, 6vw, 7.2rem)`, bold, chalk)
- Sub: "No noise. No random visitors. Real business. And good company." (caps, faded)
- Meta line: Date · Venue · Format — inline, gold dots as separators; on mobile stacks vertically with hairline dividers
- Single CTA button on desktop; **floating gold bar** fixed to bottom on mobile (appears after hero scroll)
- Background watermark: `20.08` in huge faded gold (`clamp(8rem, 18vw, 22rem)`), bottom-right

## Design decisions (do not revert without asking)

- **Ночной янтарь colour scheme** — `--ink: #1A1610`, тёплый тёмный amber. Финальный выбор, пробник удалён.
- **No `s-tag` repeats** — gold line + uppercase label removed from all sections except Contact.
- **Marquee — mixed typefaces** — alternates uppercase Instrument Sans (gold, .8rem) and italic Cormorant Garamond (chalk at low opacity, 1.35rem). 38s speed, architectural top/bottom gold hairlines. Content mixes EN slogans and dates.
- **Stats = editorial rows** — full-width horizontal rows, number left (`clamp(5rem, 10vw, 12rem)`), label right-aligned. Hairline `--line` dividers top and bottom each row. Not a 3-column grid.
- **Programme = 2-column** — Morning / Evening side by side on desktop, vertical hairline separator. Time as tiny gold label above each activity. Activity text in italic Cormorant (`clamp(1rem, 1.6vw, 1.35rem)`). No table grid, no row borders.
- **No numbered pillars** (01/02/03) — removed as cliché; pillars in About are title + description only.
- **SIGNATURE removed from hero** — nav logo already carries the name; repetition in large type was redundant.
- **Manifesto section** — standalone dark section between About and Stats with the key quote. Quote at `clamp(2.4rem, 4.8vw, 5.2rem)` desktop / `clamp(2rem, 9.5vw, 3.6rem)` mobile — big, commanding, line-height 1.1. Do not shrink.
- **Exhibitors = typographic list** — full-width rows, large italic category name (Cormorant), hover → name turns gold + description fades in right. No icons, no rectangles.
- **Register = dark** — `--ink` background, large italic h2, one meta line, full-width gold button on mobile.
- **About grid = 60/40** — left column (text) dominates editorially. Pillars are role-specific (see Role-specific views above).
- **Personal names in About** — exhibitor copy reads "Every buyer is personally invited by Olga or Daria. No automated lists, no random registrations." Names humanise B2B trust for a first-edition event. Do not revert to generic "Match Point" phrasing.
- **Parallax on 20.08** — `.hero-date-bg` has `will-change: transform`; JS moves it at `scrollY * 0.22` on scroll. Hero has `overflow: hidden` to clip. Do not remove.
- **Gold stat numbers** — `.stat-num { color: var(--gold) }`. Numbers (80%, 20, 1500+) render in gold on cream background.
- **Paper grain on light sections** — `.about::after`, `.program::after`, `.contact::after` have a fractal SVG noise texture at opacity 0.028, `mix-blend-mode: multiply`. Subtle paper warmth, do not remove.
- **Manifesto gold treatment** — `border-top/bottom: 1px solid rgba(200,164,74,.35)` + `::after` radial gradient (gold fog from bottom, opacity ~0.07) + SVG grain at `mix-blend-mode: screen`. Adds warmth without lightening dark bg.
- **Marquee opacity boost** — border opacity 0.1→0.25, item opacity 0.55→0.85. More visible, feels airier.
- **Programme headings in gold** — `.prog-part-label { color: var(--gold) }` — "Morning / Evening" labels are gold.
- **Photos planned** — joint portrait of Olga + Dasha → About/Contact; ENZO hotel photos → Hero/Register. Placeholder until ready.
- **Hero buyer tagline — line break structure** — "For you." / "Специально для вас." lives in a separate inner `<span class="hero-tagline-break">` (CSS `display:block`). Do not collapse into a single span with inline style — inline `display:block` inside data attributes is unreliable. Structure: `<span class="buyer-only"><span data-en="..." data-ru="...">main text</span><span class="hero-tagline-break" data-en="For you." data-ru="Специально для вас.">For you.</span></span>`
- **MP card (Contact section)** — tag line: "Securing new opportunities" (same EN/RU). Stat line: "Надёжные поставщики в Европе, Азии и на Ближнем Востоке" / "Trusted suppliers across Europe, Asia & the Middle East". Do not revert to "Двадцать лет в российском выездном MICE."

## Mobile (≤620px) — premium patterns

- **Stats horizontal scroll** — peek pattern: cards are 72vw wide, user swipes to see all three. No vertical stack.
- **Floating CTA** — `.mob-cta` fixed bottom bar with gold button. Appears after hero bottom exits viewport, hides when Register section is in view. JS-driven.
- **Hero buttons hidden** on mobile — replaced by floating CTA.
- **vw typography** — hero tagline `14vw`, manifesto `8vw`, register h2 `13vw`, stat numbers `22vw`.
- **Padding** — 80px vertical, 24px horizontal (was 64/20).
- Gate panels stack vertically; architectural lines hidden.

## What not to change without asking

- The gate animation (Phase 1 pen + Phase 2 role panels) — considered final
- The "two debuts" angle in exhibitor pillar 03 (MICE Signature inaugural + ENZO Hotel new opening)
- The manifesto quote (RU): "Здесь не ищут нужного человека. Здесь с ним встречаются."
- The manifesto quote (EN): "No one is searching for the right person here. They are meeting them."
- The tagline (EN): "No noise. No random visitors. Real business. And good company."
- The tagline sub (RU): "Без шума. Без случайных лиц. Только работа. И приятное общение."
- The Ночной янтарь colour scheme (`--ink: #1A1610`) — финальный выбор
- Scale rule: the event has **up to ~30 exhibitors** — no copy that implies mass or global scale

## Deploy

- GitHub Pages: https://o6594340-sys.github.io/mice-signature/
- Custom domain: **micesignature.ru** (DNS pending — reg.ru A records → 185.199.108-111.153; GitHub repo Settings → Custom domain)
- Working folder: `c:\Users\usrr\OneDrive\Документы\Projects\mice-signature` (внутри монорепо `Projects`)
- Remotes: `origin` → Russia-landing-version1, `github` → mice-signature (GitHub Pages)
- После каждого изменения — из корня монорепо (`Projects`):
  ```
  git add mice-signature/index.html mice-signature/CLAUDE.md mice-signature/CNAME
  git commit -m "..."
  git push origin main
  git subtree split --prefix=mice-signature -b deploy-mice
  git push github deploy-mice:main --force
  git branch -D deploy-mice
  ```
