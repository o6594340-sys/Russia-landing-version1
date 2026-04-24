# Tailor Studio — Landing Page

B2B landing page for **Tailor Studio** DMC — inbound tourism in Russia for Arab travel agencies.

**Live:** https://o6594340-sys.github.io/Russia-landing-version1/my-fisrt-landing/index-en.html

---

## About the project

Tailor Studio is a DMC company specialising in receiving Arab tourists in Russia.  
Founded by **Olga** (Co-founder · Russia) and **Ahmed** (Co-founder · GCC).  
Target audience: travel agencies from UAE, Qatar, Jordan, Saudi Arabia, Kuwait.  
End clients: families, couples, individuals. Premium segment.

---

## Stack

- Pure HTML + CSS + JS — no framework, no bundler
- Google Fonts: Cormorant Garamond (serif), Inter (sans), Almarai (Arabic)
- Scroll animations: IntersectionObserver + CSS transitions
- Language toggle: EN / AR (RTL) via JS `setLang()` function
- Hosting: GitHub Pages

---

## Files

```
my-fisrt-landing/
├── index-en.html     ← main working file (EN + AR toggle)
├── index.html        ← Russian version (reference only, do not edit)
├── mowwinter.jpg     ← hero photo (Moscow, winter, Bolshoi area)
├── mow3.jpg          ← Moscow destination card
├── spb.jpg           ← St. Petersburg destination card
├── sochi.jpg         ← Sochi destination card
├── brief.md          ← full project brief
├── research.md       ← market research
├── CLAUDE.md         ← AI assistant instructions
└── README.md         ← this file
```

---

## Design tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-light` | `#FAF7F0` | Warm Ivory — main background |
| `--bg-dark` | `#0A1628` | Midnight Navy — dark sections |
| `--bg-alt` | `#F5F0E8` | Linen — alternate sections |
| `--brand` | `#6B1F2A` | Deep Burgundy |
| `--gold` | `#C9A84C` | Khaleeji Gold — main accent, all CTAs |
| `--teal` | `#1A6B6B` | Arabian Teal — pain solutions |

---

## Page structure

1. **NAV** — sticky, Tailor Studio logo, lang toggle EN/AR, WhatsApp button
2. **HERO** — full-screen photo, "Russia designed for you", trust pills
3. **TRUST BAR** — Russia facts (20M Muslims, 300 years history, 6 UNESCO, 50+ halal restaurants)
4. **PAIN** — 3 strips with agency pain points + solutions
5. **PROCESS** — 4 steps: inquiry → proposal → confirmation → delivery
6. **DESTINATIONS** — Moscow / St. Petersburg / Sochi + Kazan bonus strip
7. **PACKAGES** — tabbed itineraries (Moscow / SPb / Sochi), 3–4 nights each
8. **SERVICES** — 2 signature cards: hookah culture + Russian designer boutiques
9. **CUSTOMIZE** — 8 experience categories (gastronomy, wellness, shisha, etc.)
10. **ABOUT** — November dinner story + team cards (Olga + Ahmed)
11. **FAQ** — 7 questions for Arab agencies
12. **CTA FORM** — contact form + WhatsApp + email
13. **FOOTER**
14. **WhatsApp float button**

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
| PDF catalogue | — | Olga preparing (Kazan + city programmes) |

---

## To do

- [ ] Real founder photos
- [ ] Real domain + email
- [ ] PDF catalogue (Kazan, Moscow, SPb, Sochi programmes)
- [ ] Real testimonials from agencies
- [ ] Full Arabic translation of remaining sections
- [ ] Analytics: Yandex.Metrica + GA4
- [ ] Separate city pages: moscow.html, saint-petersburg.html, sochi.html
