#!/usr/bin/env python3
"""
Tile a high-res image across multiple print pages and
output a single PDF ready for printing.
Requirements:
  pip install Pillow reportlab
"""

import os
import math
import io

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# ─── CONFIG ────────────────────────────────────────────────────────────────
INPUT_FILE        = "input.jpg"       # path to your source image
OUTPUT_PDF        = "tiled_output.pdf"
DPI               = 300               # print resolution
PAPER_SIZE_IN     = (8.5, 11)         # (width, height) in inches
ORIENTATION       = "portrait"        # "portrait" or "landscape"
MARGIN_IN         = 0.25              # margin on each side in inches
NUM_SHEETS_WIDE   = 4                 # number of pages across
NUM_SHEETS_HIGH   = None              # number of pages tall; set to None to auto-calculate
# ────────────────────────────────────────────────────────────────────────────

def calculate_sheet_counts(img_w, img_h, tile_w_px, tile_h_px):
    if NUM_SHEETS_WIDE and not NUM_SHEETS_HIGH:
        full_w = tile_w_px * NUM_SHEETS_WIDE
        full_h = int(img_h / img_w * full_w)
        sheets_h = math.ceil(full_h / tile_h_px)
        return NUM_SHEETS_WIDE, sheets_h, full_w, full_h

    if NUM_SHEETS_HIGH and not NUM_SHEETS_WIDE:
        full_h = tile_h_px * NUM_SHEETS_HIGH
        full_w = int(img_w / img_h * full_h)
        sheets_w = math.ceil(full_w / tile_w_px)
        return sheets_w, NUM_SHEETS_HIGH, full_w, full_h

    if NUM_SHEETS_WIDE and NUM_SHEETS_HIGH:
        full_w = tile_w_px * NUM_SHEETS_WIDE
        full_h = tile_h_px * NUM_SHEETS_HIGH
        return NUM_SHEETS_WIDE, NUM_SHEETS_HIGH, full_w, full_h

    raise ValueError("Set at least one of NUM_SHEETS_WIDE or NUM_SHEETS_HIGH")

def crop_tiles(resized_img, sheets_w, sheets_h, tile_w_px, tile_h_px):
    tiles = []
    for row in range(sheets_h):
        for col in range(sheets_w):
            left   = col * tile_w_px
            upper  = row * tile_h_px
            right  = left + tile_w_px
            lower  = upper + tile_h_px
            tile = resized_img.crop((left, upper, right, lower))
            tiles.append(tile)
    return tiles

def save_tiles_to_pdf(tiles, sheets_w, sheets_h):
    page_w_pt = PAPER_SIZE_IN[0] * inch
    page_h_pt = PAPER_SIZE_IN[1] * inch
    pdf = canvas.Canvas(OUTPUT_PDF, pagesize=(page_w_pt, page_h_pt))

    printable_w = (PAPER_SIZE_IN[0] - 2*MARGIN_IN) * inch
    printable_h = (PAPER_SIZE_IN[1] - 2*MARGIN_IN) * inch
    offset_x    = MARGIN_IN * inch
    offset_y    = MARGIN_IN * inch

    for tile in tiles:
        buf = io.BytesIO()
        tile_rgb = tile.convert("RGB")
        tile_rgb.save(buf, format="JPEG")
        buf.seek(0)
        pdf.drawImage(buf, offset_x, offset_y,
                      width=printable_w, height=printable_h)
        pdf.showPage()

    pdf.save()
    print(f"Saved PDF: {OUTPUT_PDF}")

def main():
    img = Image.open(INPUT_FILE)
    img_w, img_h = img.size

    # swap if landscape
    paper_w, paper_h = PAPER_SIZE_IN
    if ORIENTATION.lower() == "landscape":
        paper_w, paper_h = paper_h, paper_w

    tile_w_px = int((paper_w - 2*MARGIN_IN) * DPI)
    tile_h_px = int((paper_h - 2*MARGIN_IN) * DPI)

    sheets_w, sheets_h, full_w, full_h = calculate_sheet_counts(
        img_w, img_h, tile_w_px, tile_h_px
    )

    resized = img.resize((full_w, full_h), Image.LANCZOS)

    print(f"Image resized to {full_w}×{full_h} px")
    print(f"Tiling into {sheets_w}×{sheets_h} pages")

    tiles = crop_tiles(resized, sheets_w, sheets_h, tile_w_px, tile_h_px)

    save_tiles_to_pdf(tiles, sheets_w, sheets_h)

if __name__ == "__main__":
    main()