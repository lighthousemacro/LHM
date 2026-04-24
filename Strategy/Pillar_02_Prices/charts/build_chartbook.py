"""
Build the Pillar 2 Prices chartbook PDF.

Stitches every PNG in this folder (sorted by filename) into a single
branded PDF at the pillar root: Pillar_02_Prices_Chartbook.pdf

Run after chart regeneration:
    python build_chartbook.py
"""

from datetime import date
from pathlib import Path

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
import matplotlib.pyplot as plt


PILLAR_NAME = "PRICES"
PILLAR_NUMBER = 2
PILLAR_SUBTITLE = "The Transmission Belt"

CHARTS_DIR = Path(__file__).parent
PILLAR_DIR = CHARTS_DIR.parent
OUTPUT_PDF = PILLAR_DIR / f"{PILLAR_DIR.name}_Chartbook.pdf"
ICON_PATH = Path("/Users/bob/LHM/Brand/icon_transparent_128.png")

OCEAN = "#2389BB"
DUSK = "#FF6723"
DOLDRUMS = "#898989"


def cover_page(pdf: PdfPages) -> None:
    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor("white")

    if ICON_PATH.exists():
        icon_ax = fig.add_axes([0.08, 0.72, 0.12, 0.18])
        icon_ax.imshow(mpimg.imread(ICON_PATH))
        icon_ax.axis("off")

    fig.text(0.5, 0.62, "LIGHTHOUSE MACRO", ha="center",
             fontsize=14, fontweight="bold", color=DOLDRUMS, family="sans-serif")
    fig.text(0.5, 0.55, f"PILLAR {PILLAR_NUMBER}: {PILLAR_NAME}", ha="center",
             fontsize=32, fontweight="bold", color=OCEAN, family="sans-serif")
    fig.text(0.5, 0.49, PILLAR_SUBTITLE, ha="center",
             fontsize=18, style="italic", color=DOLDRUMS, family="serif")

    fig.text(0.5, 0.30, "C H A R T B O O K", ha="center",
             fontsize=20, fontweight="bold", color=OCEAN, family="sans-serif")
    fig.text(0.5, 0.25, date.today().strftime("%B %d, %Y"), ha="center",
             fontsize=12, color=DOLDRUMS, family="sans-serif")

    # Accent bar: 2/3 Ocean, 1/3 Dusk
    bar_ax = fig.add_axes([0.08, 0.12, 0.84, 0.012])
    bar_ax.axis("off")
    bar_ax.add_patch(plt.Rectangle((0, 0), 0.667, 1, color=OCEAN,
                                   transform=bar_ax.transAxes))
    bar_ax.add_patch(plt.Rectangle((0.667, 0), 0.333, 1, color=DUSK,
                                   transform=bar_ax.transAxes))

    fig.text(0.5, 0.08, "M A C R O ,   I L L U M I N A T E D .", ha="center",
             fontsize=10, style="italic", color=DOLDRUMS, family="sans-serif")
    fig.text(0.5, 0.05, "Bob Sheehan, CFA, CMT  |  bob@lighthousemacro.com  |  @LHMacro",
             ha="center", fontsize=8, color=DOLDRUMS, family="sans-serif")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def chart_page(pdf: PdfPages, png_path: Path, chart_number: int, total: int) -> None:
    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor("white")

    img_ax = fig.add_axes([0.05, 0.08, 0.90, 0.84])
    img_ax.imshow(mpimg.imread(png_path))
    img_ax.axis("off")

    # Footer
    fig.text(0.05, 0.04, f"Lighthouse Macro  |  Pillar {PILLAR_NUMBER}: {PILLAR_NAME}",
             fontsize=8, color=DOLDRUMS, family="sans-serif")
    fig.text(0.95, 0.04, f"{chart_number} / {total}",
             ha="right", fontsize=8, color=DOLDRUMS, family="sans-serif")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    pngs = sorted(p for p in CHARTS_DIR.glob("*.png"))
    if not pngs:
        raise SystemExit(f"No PNGs found in {CHARTS_DIR}")

    with PdfPages(OUTPUT_PDF) as pdf:
        cover_page(pdf)
        for i, png in enumerate(pngs, start=1):
            chart_page(pdf, png, i, len(pngs))

    print(f"Built {OUTPUT_PDF} with {len(pngs)} charts")


if __name__ == "__main__":
    main()
