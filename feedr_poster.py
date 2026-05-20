#!/usr/bin/env python3
"""
Feedr Weekly Vendor Poster Generator
Generates a 1080x1920px PNG poster from weekly vendor data.

Usage:
    python3 feedr_poster.py --data '{"week":"19–21 May 2026","days":[...]}' --output poster.png

The data JSON structure:
{
  "week": "19–21 May 2026",
  "days": [
    {"day": "Tuesday", "date": "19th May", "vendors": ["Lazy Geppetto", "Papa-Dum", "K10 Sushi"]},
    {"day": "Wednesday", "date": "20th May", "vendors": ["Bewliehill", "Satay Street", "German Doner Kebab"]},
    {"day": "Thursday", "date": "21st May", "vendors": ["PICK.YOUR.OWN.", "Baba Ganoush"]}
  ]
}
"""

import json, base64, sys, os, argparse, re
from pathlib import Path

ASSETS_PATH = Path(__file__).parent / "assets.json"
KLAVIYO_LOGO_PATH = Path(__file__).parent / "skills/klaviyo-2026-brand-standards/assets/logos/Klaviyo-Logo-White.svg"

# Feedr brand green + Klaviyo palette
FEEDR_GREEN   = "#2ECC7B"
FEEDR_DARK    = "#1A7A4A"   # deeper green for text
CHARCOAL      = "#1D1E20"
WHITE         = "#FFFFFF"
MIST          = "#F3F2F1"
POPPY         = "#FF4B32"


def load_assets():
    with open(ASSETS_PATH) as f:
        a = json.load(f)
    fonts = a.get("fonts", a)  # support both structures
    return fonts


def b64_png(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def build_html(data: dict) -> str:
    fonts = load_assets()
    with open(KLAVIYO_LOGO_PATH) as f:
        logo_svg = f.read()

    week_label = data.get("week", "This Week")
    days = data.get("days", [])

    def font(key):
        return fonts.get(key, fonts.get("fonts", {}).get(key, ""))

    # Calculate card heights based on number of days
    n_days = len(days)
    # Fixed heights: top_stripe(8) + header(310) + green_band(76) + footer(88) = 482
    # Remaining for day cards:
    available = 1920 - 482
    card_h = available // n_days if n_days else available

    # Build day cards HTML
    day_cards_html = ""
    for i, d in enumerate(days):
        day_name   = d.get("day", "")
        day_date   = d.get("date", "")
        vendors    = d.get("vendors", [])
        is_last    = (i == n_days - 1)
        border     = "none" if is_last else f"1px solid rgba(255,255,255,0.08)"

        vendor_items = ""
        for v in vendors:
            vendor_items += f"""
            <div class="vendor-row">
              <div class="vendor-dot"></div>
              <div class="vendor-name">{v}</div>
            </div>"""

        day_cards_html += f"""
    <div class="day-card" style="height:{card_h}px; border-bottom:{border};">
      <div class="day-header">
        <div class="day-pill">{day_name}</div>
        <div class="day-date">{day_date}</div>
        <div class="lunch-time">12:00 – 12:30</div>
      </div>
      <div class="vendor-list">{vendor_items}</div>
    </div>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
@font-face {{ font-family:'KlaviyoDegular'; font-weight:300; src:url('data:font/woff2;base64,{font("degular_light")}') format('woff2'); }}
@font-face {{ font-family:'KlaviyoDegular'; font-weight:400; src:url('data:font/woff2;base64,{font("degular_regular")}') format('woff2'); }}
@font-face {{ font-family:'KlaviyoDegular'; font-style:italic; font-weight:400; src:url('data:font/woff2;base64,{font("degular_italic")}') format('woff2'); }}
@font-face {{ font-family:'KlaviyoDegular'; font-weight:600; src:url('data:font/woff2;base64,{font("degular_semibold")}') format('woff2'); }}
@font-face {{ font-family:'InstrumentSans'; font-weight:400; src:url('data:font/woff2;base64,{font("sans_regular")}') format('woff2'); }}
@font-face {{ font-family:'InstrumentSans'; font-weight:500; src:url('data:font/woff2;base64,{font("sans_medium")}') format('woff2'); }}
@font-face {{ font-family:'InstrumentSans'; font-weight:600; src:url('data:font/woff2;base64,{font("sans_semibold")}') format('woff2'); }}
@font-face {{ font-family:'InstrumentSans'; font-weight:700; src:url('data:font/woff2;base64,{font("sans_bold")}') format('woff2'); }}
@font-face {{ font-family:'DMMono'; font-weight:500; src:url('data:font/woff2;base64,{font("mono_medium")}') format('woff2'); }}

* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:1080px; height:1920px; overflow:hidden; background:{CHARCOAL}; }}
.poster {{ width:1080px; height:1920px; display:flex; flex-direction:column; overflow:hidden; }}

/* Top stripe — Feedr green */
.top-stripe {{ background:{FEEDR_GREEN}; height:8px; flex-shrink:0; }}

/* Header */
.header {{
  background:{CHARCOAL};
  padding:44px 80px 36px;
  flex-shrink:0;
  display:flex;
  flex-direction:column;
}}
.header-top {{
  display:flex;
  align-items:center;
  justify-content:space-between;
  margin-bottom:32px;
}}
.feedr-badge {{
  font-family:'KlaviyoDegular',serif; font-weight:600; font-style:italic;
  font-size:22px; color:{CHARCOAL};
  background:{FEEDR_GREEN}; border-radius:8px;
  padding:6px 18px; letter-spacing:-0.01em;
}}
.week-eyebrow {{
  font-family:'DMMono',monospace; font-weight:500;
  font-size:15px; letter-spacing:0.18em; text-transform:uppercase;
  color:{FEEDR_GREEN}; margin-bottom:14px;
}}
.headline {{
  font-family:'KlaviyoDegular',serif; font-weight:400;
  font-size:72px; line-height:0.97; letter-spacing:-0.03em;
  color:{WHITE};
}}
.headline em {{
  font-style:italic; color:{FEEDR_GREEN};
}}
.week-range {{
  font-family:'InstrumentSans',sans-serif; font-weight:400;
  font-size:20px; color:rgba(255,255,255,0.4);
  margin-top:16px;
}}

/* Green band */
.green-band {{
  background:{FEEDR_GREEN};
  padding:0 80px;
  height:76px;
  display:flex; align-items:center; justify-content:space-between;
  flex-shrink:0;
}}
.green-band-text {{
  font-family:'KlaviyoDegular',serif; font-weight:600;
  font-size:26px; color:{CHARCOAL}; letter-spacing:-0.01em;
}}
.green-band-sub {{
  font-family:'DMMono',monospace; font-weight:500;
  font-size:14px; color:rgba(29,30,32,0.6); letter-spacing:0.1em; text-transform:uppercase;
}}

/* Day cards */
.day-card {{
  background:{CHARCOAL};
  padding:32px 80px;
  flex-shrink:0;
  display:flex;
  align-items:stretch;
  gap:48px;
}}
.day-header {{
  flex-shrink:0;
  width:240px;
  display:flex;
  flex-direction:column;
  justify-content:flex-start;
  padding-top:4px;
}}
.day-pill {{
  display:inline-block;
  font-family:'InstrumentSans',sans-serif; font-weight:700;
  font-size:13px; letter-spacing:0.12em; text-transform:uppercase;
  color:{CHARCOAL}; background:{FEEDR_GREEN};
  padding:5px 14px; border-radius:6px;
  margin-bottom:12px; align-self:flex-start;
}}
.day-date {{
  font-family:'KlaviyoDegular',serif; font-weight:600;
  font-size:32px; color:{WHITE}; line-height:1.05;
  letter-spacing:-0.02em; margin-bottom:8px;
}}
.lunch-time {{
  font-family:'InstrumentSans',sans-serif; font-weight:400;
  font-size:15px; color:rgba(255,255,255,0.35);
}}
.vendor-list {{
  flex:1;
  display:flex;
  flex-direction:column;
  justify-content:center;
  gap:18px;
  border-left:2px solid rgba(46,204,123,0.25);
  padding-left:48px;
}}
.vendor-row {{
  display:flex; align-items:center; gap:16px;
}}
.vendor-dot {{
  width:10px; height:10px; border-radius:50%;
  background:{FEEDR_GREEN}; flex-shrink:0;
}}
.vendor-name {{
  font-family:'KlaviyoDegular',serif; font-weight:600;
  font-size:32px; color:{WHITE};
  letter-spacing:-0.02em; line-height:1.1;
}}

/* Footer */
.footer {{
  background:{CHARCOAL};
  border-top:1px solid rgba(255,255,255,0.06);
  padding:0 80px;
  height:88px;
  display:flex; align-items:center; justify-content:space-between;
  flex-shrink:0;
  margin-top:auto;
}}
.footer-left {{
  font-family:'InstrumentSans',sans-serif; font-weight:500;
  font-size:16px; color:rgba(255,255,255,0.25);
}}
.footer-right {{
  font-family:'DMMono',monospace; font-weight:500;
  font-size:12px; letter-spacing:0.1em; text-transform:uppercase;
  color:rgba(255,255,255,0.18);
}}
</style>
</head>
<body>
<div class="poster">
  <div class="top-stripe"></div>

  <div class="header">
    <div class="header-top">
      {logo_svg}
      <div class="feedr-badge">feedr</div>
    </div>
    <div class="week-eyebrow">This Week's Lunch</div>
    <div class="headline">What's<br>being<br><em>served.</em></div>
    <div class="week-range">Week of {week_label}</div>
  </div>

  <div class="green-band">
    <div class="green-band-text">Cloud Canteen · London Office</div>
    <div class="green-band-sub">Order via Feedr</div>
  </div>

  {day_cards_html}

  <div class="footer">
    <span class="footer-left">Klaviyo · London Office</span>
    <span class="footer-right">feedr.co</span>
  </div>
</div>
</body>
</html>"""
    return html


def render_poster(data: dict, output_path: str):
    """Render poster to PNG using Playwright."""
    import subprocess, tempfile

    html = build_html(data)

    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", delete=False) as f:
        f.write(html)
        html_path = f.name

    script = f"""
const {{ chromium }} = require('playwright-chromium');
(async () => {{
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({{ width: 1080, height: 1920 }});
  const html = require('fs').readFileSync('{html_path}', 'utf8');
  await page.setContent(html, {{ waitUntil: 'networkidle' }});
  await page.waitForTimeout(500);
  await page.screenshot({{ path: '{output_path}', fullPage: false, clip: {{ x:0, y:0, width:1080, height:1920 }} }});
  await browser.close();
}})().catch(e => {{ console.error(e); process.exit(1); }});
"""
    with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
        f.write(script)
        js_path = f.name

    result = subprocess.run(["node", js_path], capture_output=True, text=True, cwd=str(Path(__file__).parent))
    os.unlink(html_path)
    os.unlink(js_path)

    if result.returncode != 0:
        raise RuntimeError(f"Playwright failed: {result.stderr}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, help="JSON vendor data")
    parser.add_argument("--output", type=str, default="feedr_poster.png")
    args = parser.parse_args()

    if args.data:
        data = json.loads(args.data)
    else:
        # Default: use this week's data for testing
        data = {
            "week": "19–21 May 2026",
            "days": [
                {"day": "Tuesday",   "date": "19th May", "vendors": ["Lazy Geppetto", "Papa-Dum", "K10 Sushi"]},
                {"day": "Wednesday", "date": "20th May", "vendors": ["Bewliehill", "Satay Street", "German Doner Kebab"]},
                {"day": "Thursday",  "date": "21st May", "vendors": ["PICK.YOUR.OWN.", "Baba Ganoush"]}
            ]
        }

    out = render_poster(data, args.output)
    print(f"Poster saved: {out}")
