"""
Tailor Studio — Marketing PDF generator
Uses xhtml2pdf (reportlab backend) — pure Python, no GTK needed
"""

import re
import markdown
from xhtml2pdf import pisa
from pathlib import Path

BASE     = Path(__file__).parent
MD_FILE  = BASE / "tailor-studio-marketing-EN.md"
PDF_FILE = BASE / "tailor-studio-marketing-EN.pdf"

# ── read & convert markdown ────────────────────────────────────────────────
text = MD_FILE.read_text(encoding="utf-8")

# strip first 3 header lines (used for cover separately)
cover_match = re.match(r"^(#[^\n]+)\n(##[^\n]+)\n(###[^\n]+)\n\n---\n\n", text)
if cover_match:
    body_text = text[cover_match.end():]
else:
    body_text = text

md_parser = markdown.Markdown(extensions=["tables"])
body_html = md_parser.convert(body_text)

# ── post-process: mark safety block ───────────────────────────────────────
body_html = re.sub(
    r"(<h1>ONE QUESTION, ANSWERED DIRECTLY</h1>)(.*?)(<h1>MOSCOW</h1>)",
    r'<div class="safety-block">\1\2</div>\3',
    body_html,
    flags=re.DOTALL,
)

# ── inline styles (xhtml2pdf subset) ──────────────────────────────────────
CSS = """
@page {
    size: A4;
    margin: 22mm 18mm 24mm 18mm;
    @frame footer {
        -pdf-frame-content: footerContent;
        bottom: 10mm; left: 18mm; right: 18mm;
        height: 8mm;
    }
}

body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 10pt;
    color: #1A1A2E;
    line-height: 1.65;
    background: #FAF7F0;
}

/* ── headings ── */
h1 {
    font-family: Georgia, serif;
    font-size: 22pt;
    font-weight: normal;
    color: #0A1628;
    margin-top: 14pt;
    margin-bottom: 6pt;
    padding-bottom: 4pt;
    border-bottom: 1pt solid #C9A84C;
}
h2 {
    font-family: Georgia, serif;
    font-size: 15pt;
    font-weight: normal;
    color: #0A1628;
    margin-top: 10pt;
    margin-bottom: 4pt;
}
h3 {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 8pt;
    font-weight: bold;
    color: #C9A84C;
    letter-spacing: 1.5pt;
    text-transform: uppercase;
    margin-top: 9pt;
    margin-bottom: 3pt;
}
h4 {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 9pt;
    font-weight: bold;
    color: #1A1A2E;
    margin-top: 6pt;
    margin-bottom: 2pt;
}

/* ── body ── */
p {
    margin-top: 0;
    margin-bottom: 5pt;
}
em  { font-style: italic; }
strong { font-weight: bold; }
a { color: #C9A84C; }

/* ── hr ── */
hr {
    border-top: 0.5pt solid #C9A84C;
    margin-top: 10pt;
    margin-bottom: 10pt;
}

/* ── blockquote ── */
blockquote {
    margin-left: 10pt;
    margin-right: 0;
    padding-left: 8pt;
    border-left: 2pt solid #C9A84C;
    color: #6B7280;
    font-style: italic;
    font-size: 9.5pt;
}

/* ── tables ── */
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 6pt;
    margin-bottom: 6pt;
    font-size: 8.5pt;
}
th {
    background-color: #0A1628;
    color: #FAF7F0;
    padding: 4pt 5pt;
    text-align: left;
    font-size: 7.5pt;
    text-transform: uppercase;
    letter-spacing: 0.5pt;
}
td {
    padding: 3.5pt 5pt;
    border-bottom: 0.5pt solid #E8D5B7;
    vertical-align: top;
}
tr:nth-child(even) td { background-color: #FBF8F2; }
tr:nth-child(odd)  td { background-color: #FFFFFF; }

/* ── lists ── */
ul, ol {
    margin-left: 12pt;
    margin-top: 3pt;
    margin-bottom: 5pt;
}
li { margin-bottom: 2pt; }

/* ── safety block ── */
.safety-block {
    background-color: #0A1628;
    color: #FAF7F0;
    padding: 10pt 12pt;
    margin-bottom: 10pt;
}
.safety-block h1 {
    color: #C9A84C;
    border-bottom: 0.5pt solid #C9A84C;
    font-size: 17pt;
    margin-top: 0;
}
.safety-block p { color: #D4CECC; }

/* ── italic note paragraph ── */
p > em { color: #6B7280; }

/* ── section label (small caps gold) ── */
.label {
    font-size: 7.5pt;
    font-weight: bold;
    letter-spacing: 1.5pt;
    text-transform: uppercase;
    color: #C9A84C;
}
"""

# ── cover HTML ─────────────────────────────────────────────────────────────
COVER_HTML = """
<div style="
    background-color: #0A1628;
    width: 100%;
    padding: 0;
    margin: 0;
    page-break-after: always;
">
  <!-- top label -->
  <p style="
      text-align: center;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 7pt;
      letter-spacing: 3pt;
      text-transform: uppercase;
      color: #4A5568;
      margin: 0;
      padding-top: 38pt;
  ">Destination Management Company &middot; Russia</p>

  <!-- spacer -->
  <p style="margin: 36pt 0 0 0; text-align: center; color: #C9A84C; font-size: 11pt; letter-spacing: 8pt;">
  &mdash;&mdash;&mdash;
  </p>

  <!-- title -->
  <p style="
      text-align: center;
      font-family: Georgia, serif;
      font-size: 44pt;
      font-weight: normal;
      color: #FAF7F0;
      letter-spacing: 5pt;
      text-transform: uppercase;
      margin: 12pt 0 0 0;
      line-height: 1.05;
  ">
      <span style="color:#C9A84C;">Tailor</span> Studio
  </p>

  <!-- subtitle -->
  <p style="
      text-align: center;
      font-family: Georgia, serif;
      font-size: 14pt;
      font-weight: normal;
      font-style: italic;
      color: #9CA3AF;
      margin: 10pt 0 0 0;
      letter-spacing: 0.5pt;
  ">Russia &middot; Summer 2026</p>

  <!-- tagline -->
  <p style="
      text-align: center;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 7.5pt;
      font-weight: bold;
      letter-spacing: 3.5pt;
      text-transform: uppercase;
      color: #C9A84C;
      margin: 10pt 0 0 0;
  ">Russia, properly.</p>

  <p style="margin: 30pt 0 0 0; text-align: center; color: #C9A84C; font-size: 11pt; letter-spacing: 8pt;">
  &mdash;&mdash;&mdash;
  </p>

  <!-- city pills -->
  <table style="
      width: 200pt;
      margin: 22pt auto 0 auto;
      border-collapse: collapse;
  ">
    <tr>
      <td style="
          text-align: center;
          font-family: Helvetica, Arial, sans-serif;
          font-size: 7pt;
          letter-spacing: 2pt;
          text-transform: uppercase;
          color: #6B7280;
          border: none;
          background: transparent;
          padding: 0 8pt;
      ">Moscow</td>
      <td style="
          text-align: center;
          font-family: Helvetica, Arial, sans-serif;
          font-size: 7pt;
          letter-spacing: 2pt;
          text-transform: uppercase;
          color: #6B7280;
          border: none;
          background: transparent;
          padding: 0 8pt;
      ">St. Petersburg</td>
      <td style="
          text-align: center;
          font-family: Helvetica, Arial, sans-serif;
          font-size: 7pt;
          letter-spacing: 2pt;
          text-transform: uppercase;
          color: #6B7280;
          border: none;
          background: transparent;
          padding: 0 8pt;
      ">Sochi</td>
    </tr>
  </table>

  <!-- footer -->
  <p style="
      text-align: center;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 6.5pt;
      letter-spacing: 1pt;
      color: #374151;
      margin-top: 200pt;
      padding-bottom: 0;
      text-transform: uppercase;
  ">B2B Partner Document &nbsp;&middot;&nbsp; For agency use only &nbsp;&middot;&nbsp; Not for distribution to end clients</p>
</div>
"""

# ── footer content ─────────────────────────────────────────────────────────
FOOTER_HTML = """
<div id="footerContent" style="
    text-align: center;
    font-family: Helvetica, Arial, sans-serif;
    font-size: 7pt;
    color: #9CA3AF;
    border-top: 0.5pt solid #E8D5B7;
    padding-top: 3pt;
">
    Tailor Studio &nbsp;&middot;&nbsp; Russia DMC &nbsp;&middot;&nbsp; B2B only
    &nbsp;&nbsp;&nbsp;
    <pdf:pagenumber />
</div>
"""

# ── assemble full HTML ─────────────────────────────────────────────────────
full_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>{CSS}</style>
</head>
<body>

{FOOTER_HTML}

{COVER_HTML}

{body_html}

</body>
</html>"""

# ── render ─────────────────────────────────────────────────────────────────
print("Rendering PDF...")
with open(PDF_FILE, "wb") as f:
    result = pisa.CreatePDF(
        full_html.encode("utf-8"),
        dest=f,
        encoding="utf-8",
    )

if result.err:
    print(f"Errors: {result.err}")
else:
    print("Done: " + str(PDF_FILE))
