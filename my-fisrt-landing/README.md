# Tailor Studio — Landing Page

B2B landing page for **Tailor Studio** DMC — inbound tourism in Russia for Arab travel agencies.

**Live:** https://o6594340-sys.github.io/Russia-landing-version1/my-fisrt-landing/index-en.html  
**GitHub:** https://github.com/o6594340-sys/Russia-landing-version1

---

## About the project

Tailor Studio is a DMC company specialising in receiving Arab tourists in Russia.  
Founded by **Olga** (Co-founder · Russia) and **Ahmed** (Co-founder · GCC · Dubai).  
Target audience: travel agencies from UAE, Qatar, Jordan, Saudi Arabia, Kuwait.  
End clients: families, couples, individuals. Premium segment.  
Device split: 85%+ iPhone / mobile.

---

## Stack

- Pure HTML + CSS + JS — no framework, no bundler
- Google Fonts: Cormorant Garamond (serif display), Inter (sans), Almarai (Arabic)
- Scroll animations: IntersectionObserver + CSS transitions
- Language toggle: EN / AR (RTL) via JS `setLang()` function
- Hosting: GitHub Pages

---

## Files

```
my-fisrt-landing/
├── index-en.html     ← MAIN working file (EN + AR toggle)
├── index.html        ← Russian version (reference only, do not edit)
├── mowwinter.jpg     ← hero photo (Moscow, winter)
├── mow3.jpg          ← Moscow destination card
├── spb.jpg           ← St. Petersburg destination card
├── sochi.jpg         ← Sochi destination card
├── shisha.jpg        ← experience carousel slide
├── dining.jpg        ← experience carousel slide
├── brief.md          ← full project brief
├── research.md       ← market research
├── CLAUDE.md         ← AI assistant instructions
└── README.md         ← this file
```

---

## Design tokens (current)

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-light` | `#FAFAFA` | Near-white — main background |
| `--bg-dark` | `#1C3D5C` | Midnight Navy — dark sections |
| `--bg-alt` | `#F5F4F2` | Neutral warm — alternate sections |
| `--bg-card` | `#FFFFFF` | Cards |
| `--brand` | `#C0392B` | Deep Red |
| `--gold` | `#D4A843` | Amber Gold — main accent, CTAs |
| `--gold-light` | `#E2C06A` | Champagne |
| `--teal` | `#1A7070` | Arabian Teal — pain solutions |
| `--text-muted` | `#6B7280` | Secondary text |

---

## Page structure

1. **NAV** — sticky, Tailor Studio logo, lang toggle EN/AR, WhatsApp button
2. **HERO** — full-screen photo, *"Russia, made to measure"*, two CTAs, trust pills
3. **TRUST BAR** — light section: 4 Russia facts + country flags
4. **PAIN** — 3 strips with agency pain points + solutions
5. **DESTINATIONS** — Moscow / St. Petersburg / Sochi + Kazan bonus strip
6. **PACKAGES** — tabbed itineraries (Moscow / SPb / Sochi), 3–4 nights each
7. **SERVICES** — 2 signature dark cards + 4 standard cards
8. **EXPERIENCE** — horizontal carousel of experiences
9. **ABOUT** — November dinner story + team cards (Olga + Ahmed)
10. **FAQ** — 7 questions for Arab agencies
11. **PROCESS** — 4 partnership steps (placed before CTA)
12. **CTA FORM** — contact form + WhatsApp + email
13. **FOOTER**
14. **WhatsApp float button**

---

## Key design decisions

- **Buttons** — pill shape (`border-radius: 50px`) throughout
- **Cards** — shadow-only, no borders (floating card style)
- **Trust Bar** — light background (white + gold numbers), not dark navy
- **Gold labels** — removed from routine sections, kept only at key anchors
- **Halal** — present but not dominant: mentioned in trust bar, pain section, packages, FAQ only
- **Noise grain** — removed
- **Hero CTA** — primary gold "Start a Conversation →" + secondary "View Programmes"

---

## Placeholder data — replace before launch

| What | Current | Replace with |
|------|---------|--------------|
| WhatsApp | `+971 50 343 4428` | confirm with Ahmed |
| Email | `olga@tailorstudio.ru` | confirm |
| Domain in meta | `https://russiawelcome.ru` | real domain |
| OG image | placeholder URL | real 1200×630 |
| Founder photos | emoji 👤 | real portraits |
| Founder surnames | — | confirm |
| Testimonials | — | real agency reviews |
| PDF catalogue | — | Olga preparing |
| Logo | text wordmark | designed logo file |

---

## To do

### Content
- [ ] Real founder photos (portraits)
- [ ] Real domain + email
- [ ] Real testimonials from agencies
- [ ] Full Arabic translation of remaining sections
- [ ] PDF catalogue (programmes)

### Design / Tech
- [ ] Logo: wordmark Tailor Studio (Cormorant Garamond direction)
- [ ] Hero animation: Kling AI video loop (living photo)
- [ ] Reduce contact form from 5 fields to 3
- [ ] Analytics: Yandex.Metrica + GA4

### Future pages
- [ ] moscow.html
- [ ] saint-petersburg.html
- [ ] sochi.html
- [ ] tours.html
