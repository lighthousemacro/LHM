#!/usr/bin/env python3
"""
build_favicons.py — cut the full favicon + og-image set from one logo SVG.

Usage:
    python3 Scripts/website/build_favicons.py /Users/bob/LHM/Brand/lighthouse_mark_e.svg

Outputs into Website/: favicon-16/32/48, apple-touch-icon (180),
android-chrome 192/512, favicon.ico (multi-res), og-image (1200x630).
Renders SVG -> master PNG via qlmanage, resizes via Pillow.
"""
import os
import sys
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = "/Users/bob/LHM"
WEB = os.path.join(ROOT, "Website")
DEEP = (0x12, 0x34, 0x56)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

SIZES = {
    "favicon-16x16.png": 16,
    "favicon-32x32.png": 32,
    "favicon-48x48.png": 48,
    "apple-touch-icon.png": 180,
    "android-chrome-192x192.png": 192,
    "android-chrome-512x512.png": 512,
}


def render_svg(svg_path, px=1024):
    """SVG -> high-res PNG with TRUE transparency via Chrome headless.
    (qlmanage composited the rounded-corner transparency onto white, which
    baked the '4 white corners' into the mark — Chrome preserves alpha.)"""
    svg = open(svg_path, encoding="utf-8").read()
    html = (f"<!DOCTYPE html><html><head><style>*{{margin:0;padding:0}}"
            f"html,body{{width:{px}px;height:{px}px;overflow:hidden}}"
            f"svg{{display:block;width:{px}px;height:{px}px}}</style></head>"
            f"<body>{svg}</body></html>")
    tmp = tempfile.mkdtemp()
    hpath = os.path.join(tmp, "logo.html")
    out = os.path.join(tmp, "logo.png")
    with open(hpath, "w", encoding="utf-8") as f:
        f.write(html)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    f"--screenshot={out}", f"--window-size={px},{px}",
                    "--default-background-color=00000000", hpath],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(out):
        raise RuntimeError(f"Chrome produced no PNG for {svg_path}")
    return Image.open(out).convert("RGBA")


def find_font(bold=True):
    cands = [
        "/System/Library/Fonts/Supplemental/Montserrat-Bold.ttf",
        "/Library/Fonts/Montserrat-Bold.ttf",
        os.path.expanduser("~/Library/Fonts/Montserrat-Bold.ttf"),
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    return None


def main(svg_path):
    master = render_svg(svg_path, 1024)
    # opaque Deep version for OS icons that mask + fill corners with black
    flat = Image.new("RGBA", master.size, DEEP + (255,))
    flat.alpha_composite(master)
    # iOS apple-touch + Android maskable want opaque; browser favicons stay transparent
    OPAQUE = {"apple-touch-icon.png", "android-chrome-192x192.png", "android-chrome-512x512.png"}

    # square favicon/app icons
    for name, size in SIZES.items():
        src = flat if name in OPAQUE else master
        src.resize((size, size), Image.LANCZOS).save(os.path.join(WEB, name))

    # multi-res .ico
    ico = master.resize((64, 64), Image.LANCZOS)
    ico.save(os.path.join(WEB, "favicon.ico"),
             sizes=[(16, 16), (32, 32), (48, 48)])

    # og-image 1200x630 on Deep navy, logo left, wordmark right
    og = Image.new("RGBA", (1200, 630), DEEP + (255,))
    mark = master.resize((300, 300), Image.LANCZOS)
    og.alpha_composite(mark, (90, 165))
    d = ImageDraw.Draw(og)
    fp = find_font()
    if fp:
        try:
            f1 = ImageFont.truetype(fp, 96)
            f2 = ImageFont.truetype(fp, 34)
            d.text((440, 230), "LIGHTHOUSE", font=f1, fill=(255, 255, 255, 255))
            d.text((440, 330), "MACRO", font=f1, fill=(0x89, 0xCC, 0xFF, 255))
            d.text((446, 448), "MACRO, ILLUMINATED.", font=f2, fill=(0x89, 0xCC, 0xFF, 255))
        except Exception as e:
            print("font render skipped:", e)
    # ocean/dusk accent bar
    for x in range(1200):
        col = (0x23, 0x89, 0xBB) if x < 800 else (0xFF, 0x67, 0x23)
        d.line([(x, 0), (x, 8)], fill=col)
    og.convert("RGB").save(os.path.join(WEB, "og-image.png"), quality=92)

    made = list(SIZES) + ["favicon.ico", "og-image.png"]
    print("favicons cut from", os.path.basename(svg_path))
    for m in made:
        p = os.path.join(WEB, m)
        print(f"  {m:30} {os.path.getsize(p):>7} bytes")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: build_favicons.py <logo.svg>")
    main(sys.argv[1])
