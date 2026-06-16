#!/usr/bin/env python3
"""
build_banners.py — Lighthouse Macro Substack header + footer banners.

Renders branded banners as HTML (real Montserrat / Source Code Pro, the site
palette) and screenshots them headless via Chrome, so they match the website
typography exactly. Output PNGs are static images (not clickable), sized for
Substack.

Run: python3 Scripts/website/build_banners.py
"""
import base64
import os
import subprocess
import tempfile

ROOT = "/Users/bob/LHM"
FONTS = "/tmp/lhm_fonts"
LOGO = os.path.join(ROOT, "Brand/lighthouse_mark.png")
OUT = os.path.join(ROOT, "Brand")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

DEEP = "#123456"; OCEAN = "#2389BB"; SKY = "#89CCFF"; DUSK = "#FF6723"


def b64(path, mime):
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


LOGO_URI = b64(LOGO, "image/png")
XB = b64(f"{FONTS}/Montserrat-ExtraBold.ttf", "font/ttf")
BD = b64(f"{FONTS}/Montserrat-Bold.ttf", "font/ttf")
SCP = b64(f"{FONTS}/SourceCodePro-Semibold.ttf", "font/ttf")

FONTCSS = f"""
@font-face {{ font-family:'Mont'; font-weight:800; src:url({XB}) format('truetype'); }}
@font-face {{ font-family:'Mont'; font-weight:700; src:url({BD}) format('truetype'); }}
@font-face {{ font-family:'SCP'; font-weight:600; src:url({SCP}) format('truetype'); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
"""

HEADER_HTML = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{FONTCSS}
body {{ width:1100px; height:220px; background:{DEEP}; overflow:hidden; position:relative; }}
.row {{ display:flex; align-items:center; height:100%; padding:0 0 0 30px; gap:34px; }}
.mark {{ width:176px; height:176px; flex:none; }}
.wm {{ font-family:'Mont'; font-weight:800; line-height:0.92; letter-spacing:-1.5px; font-size:62px; }}
.wm .lh {{ color:#FFFFFF; }} .wm .mc {{ color:{SKY}; }}
.tag {{ font-family:'SCP'; font-weight:600; font-size:15px; letter-spacing:7px; color:{SKY};
        text-transform:uppercase; margin-top:14px; }}
.accent {{ position:absolute; left:0; right:0; bottom:0; height:6px;
           background:linear-gradient(90deg,{OCEAN} 66%,{DUSK} 66%); }}
</style></head><body>
  <div class="row">
    <img class="mark" src="{LOGO_URI}">
    <div>
      <div class="wm"><span class="lh">LIGHTHOUSE</span><br><span class="mc">MACRO</span></div>
      <div class="tag">Macro, Illuminated.</div>
    </div>
  </div>
  <div class="accent"></div>
</body></html>"""

FOOTER_HTML = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{FONTCSS}
body {{ width:1100px; height:200px; background:{DEEP}; overflow:hidden; position:relative; }}
.accent {{ position:absolute; left:0; right:0; top:0; height:6px;
           background:linear-gradient(90deg,{OCEAN} 66%,{DUSK} 66%); }}
.row {{ display:flex; align-items:center; justify-content:space-between; height:100%; padding:0 44px; }}
.left {{ display:flex; align-items:center; gap:22px; }}
.mark {{ width:104px; height:104px; flex:none; }}
.wm {{ font-family:'Mont'; font-weight:800; font-size:27px; letter-spacing:-0.6px; color:#FFFFFF; }}
.wm .mc {{ color:{SKY}; }}
.tag {{ font-family:'SCP'; font-weight:600; font-size:11px; letter-spacing:5px; color:{SKY};
        text-transform:uppercase; margin-top:9px; }}
.right {{ text-align:right; }}
.cta {{ font-family:'Mont'; font-weight:700; font-size:18px; color:#FFFFFF; }}
.links {{ font-family:'SCP'; font-weight:600; font-size:13px; color:{OCEAN}; margin-top:11px; }}
.mail {{ font-family:'SCP'; font-weight:600; font-size:13px; color:{SKY}; margin-top:6px; }}
</style></head><body>
  <div class="accent"></div>
  <div class="row">
    <div class="left">
      <img class="mark" src="{LOGO_URI}">
      <div>
        <div class="wm">LIGHTHOUSE <span class="mc">MACRO</span></div>
        <div class="tag">Macro, Illuminated.</div>
      </div>
    </div>
    <div class="right">
      <div class="cta">Don't navigate in the dark.</div>
      <div class="links">lighthousemacro.com&nbsp;&nbsp;&middot;&nbsp;&nbsp;@LHMacro</div>
      <div class="mail">bob@lighthousemacro.com</div>
    </div>
  </div>
</body></html>"""


def shoot(html, w, h, out_name):
    tmp = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False)
    tmp.write(html); tmp.close()
    out = os.path.join(OUT, out_name)
    subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=2",  # 2x retina
        f"--screenshot={out}", f"--window-size={w},{h}",
        "--default-background-color=00000000", tmp.name,
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.unlink(tmp.name)
    return out


if __name__ == "__main__":
    h = shoot(HEADER_HTML, 1100, 220, "substack_header.png")
    f = shoot(FOOTER_HTML, 1100, 200, "substack_footer.png")
    from PIL import Image
    for p in (h, f):
        print(f"{os.path.basename(p):24} {Image.open(p).size}  {os.path.getsize(p)//1024}KB")
