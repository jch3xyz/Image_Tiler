#!/usr/bin/env python3
"""
Tile a high-res image across multiple print pages and
output a single PDF ready for printing.

Requirements:
  pip install Pillow reportlab
"""

import math
import io
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

# ─── CONFIG ────────────────────────────────────────────────────────────────
INPUT_FILE      = "/Users/johnholmes/Library/CloudStorage/Dropbox/Photos/Collages/2025/250611 Step 3.png"
OUTPUT_PDF      = "tiled_output2.pdf"
DPI             = 300                 # print resolution in dots per inch
PAPER_SIZE_IN   = (8.5, 11)           # (width, height) in inches
ORIENTATION     = "landscape"         # "portrait" or "landscape"
MARGIN_IN       = 0                   # margin on each side in inches
NUM_SHEETS_WIDE = 3                   # pages across
NUM_SHEETS_HIGH = 2                   # pages tall; set to None to auto-calc
# ────────────────────────────────────────────────────────────────────────────

# apply orientation
if ORIENTATION.lower() == "landscape":
    PAGE_SIZE_IN = (PAPER_SIZE_IN[1], PAPER_SIZE_IN[0])
else:
    PAGE_SIZE_IN = PAPER_SIZE_IN

def calculate_sheet_counts(img_w, img_h, tile_w_px, tile_h_px):
    """
    Determine how many sheets wide/tall and
    compute full image pixel dimensions.
    Returns (sheets_w, sheets_h, full_w_px, full_h_px).
    """
    if NUM_SHEETS_WIDE and not NUM_SHEETS_HIGH:
        full_w  = tile_w_px * NUM_SHEETS_WIDE
        full_h  = int(img_h / img_w * full_w)
        sheets_h = math.ceil(full_h / tile_h_px)
        return NUM_SHEETS_WIDE, sheets_h, full_w, full_h

    if NUM_SHEETS_HIGH and not NUM_SHEETS_WIDE:
        full_h  = tile_h_px * NUM_SHEETS_HIGH
        full_w  = int(img_w / img_h * full_h)
        sheets_w = math.ceil(full_w / tile_w_px)
        return sheets_w, NUM_SHEETS_HIGH, full_w, full_h

    if NUM_SHEETS_WIDE and NUM_SHEETS_HIGH:
        full_w = tile_w_px * NUM_SHEETS_WIDE
        full_h = tile_h_px * NUM_SHEETS_HIGH
        return NUM_SHEETS_WIDE, NUM_SHEETS_HIGH, full_w, full_h

    raise ValueError("Set at least one of NUM_SHEETS_WIDE or NUM_SHEETS_HIGH")

def crop_tiles(image, sheets_w, sheets_h, tile_w_px, tile_h_px):
    """
    Crop the resized image into individual tile images.
    Returns a list of PIL Image tiles.
    """
    tiles = []
    for row in range(sheets_h):
        for col in range(sheets_w):
            left   = col * tile_w_px
            upper  = row * tile_h_px
            right  = left + tile_w_px
            lower  = upper + tile_h_px
            tile = image.crop((left, upper, right, lower))
            tiles.append(tile)
    return tiles

def save_tiles_to_pdf(tiles):
    """
    Save each tile into a PDF page.
    Preserves transparency via mask="auto".
    """
    page_w_pt, page_h_pt = (dim * inch for dim in PAGE_SIZE_IN)
    pdf = canvas.Canvas(OUTPUT_PDF, pagesize=(page_w_pt, page_h_pt))

    printable_w = (PAGE_SIZE_IN[0] - 2 * MARGIN_IN) * inch
    printable_h = (PAGE_SIZE_IN[1] - 2 * MARGIN_IN) * inch
    offset_x    = MARGIN_IN * inch
    offset_y    = MARGIN_IN * inch

    for tile in tiles:
        buf = io.BytesIO()
        tile.save(buf, format="PNG")
        buf.seek(0)
        img = ImageReader(buf)
        pdf.drawImage(
            img,
            offset_x, offset_y,
            width=printable_w,
            height=printable_h,
            mask="auto"
        )
        pdf.showPage()

    pdf.save()
    print(f"Saved PDF: {OUTPUT_PDF}")

def main():
    # load source image
    img = Image.open(INPUT_FILE)
    img_w, img_h = img.size

    # compute tile dimensions in pixels
    tile_w_px = int((PAGE_SIZE_IN[0] - 2 * MARGIN_IN) * DPI)
    tile_h_px = int((PAGE_SIZE_IN[1] - 2 * MARGIN_IN) * DPI)

    # determine layout and full size
    sheets_w, sheets_h, full_w, full_h = calculate_sheet_counts(
        img_w, img_h, tile_w_px, tile_h_px
    )

    # resize source to exact full dimensions
    resized = img.resize((full_w, full_h), Image.LANCZOS)

    print(f"Image resized to {full_w}×{full_h} px")
    print(f"Tiling into {sheets_w}×{sheets_h} pages")

    # crop and export
    tiles = crop_tiles(resized, sheets_w, sheets_h, tile_w_px, tile_h_px)
    save_tiles_to_pdf(tiles)

if __name__ == "__main__":
    main()
