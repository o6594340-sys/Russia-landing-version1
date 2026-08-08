# PPTX build source

Regenerates `decks/NS-Tours-Concept2.pptx` from scratch. Not needed to just use the deck — only if you need to change layout/content later.

## Requirements

- `pip install python-pptx pillow pywin32`
- Microsoft PowerPoint installed (used via COM automation for font embedding and PNG export/QA — this is Windows+PowerPoint only, there is no cross-platform path for the embedding step)
- The three fonts installed for the current user (see `fonts_ttf/`) — copy the `.ttf` files into `%LOCALAPPDATA%\Microsoft\Windows\Fonts` and register them under `HKCU\Software\Microsoft\Windows NT\CurrentVersion\Fonts`, or just double-click each `.ttf` and choose Install.

## Build

```
python build_pptx.py
```

Produces `build/NS-Tours-Concept2.pptx` (fonts referenced by name, not embedded).

## Embed fonts (recommended before delivering to the client)

```
python embed_fonts.py build/NS-Tours-Concept2.pptx build/NS-Tours-Concept2-embedded.pptx
```

Uses PowerPoint's `SaveAs(..., EmbedTrueTypeFonts=True)` — requires the fonts to be installed locally (see above) since PowerPoint embeds whatever font files are currently active in the session. Copy the `-embedded` output to `../decks/NS-Tours-Concept2.pptx`.

## QA / visual check

```
python export_pptx_png.py build/NS-Tours-Concept2.pptx qa
```

Exports every slide as a PNG (via PowerPoint COM — this is how the deck was actually visually verified while building it, there's no other pptx renderer in this environment). Check `qa/slide/` for overflow, clipping, or misaligned shapes before re-embedding and delivering.

## Notes on the approach

- Diagonal slide backgrounds are freeform 4-point polygons (`shapes.build_freeform`), not gradients — matches the HTML deck's `linear-gradient(112deg, ... 57%, ... 100%)` hard-stop, calibrated to top-x=70%/bottom-x=48% of slide width.
- Doodle icons are rasterized PNGs (`assets/*.png`, transparent background) rendered from `assets/doodles.html` — the same SVG line art as the HTML deck, screenshotted per-element via Playwright since PPTX doesn't support inline SVG.
- Photos are pre-cropped square/portrait JPGs in `assets/ph_*.jpg`, matching the HTML deck's `object-position` crops.
- Fonts: Yeseva One (headlines), Manrope (body), Caveat (handwritten notes/humor lines) — same as the HTML deck. `fonts_ttf/` has the actual files (pulled from the google/fonts GitHub repo, OFL-licensed, embeddable).
