"""Render the supplied PDF and apply the requested schedule refinements."""

from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'artifacts' / 'program-at-a-glance.pdf'
OUTPUT = ROOT / 'assets' / 'images' / 'program-at-a-glance.png'
POPPLER = Path(r'C:\Users\henry\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe')
SCALE = 8  # 576 dpi; PDF geometry below is measured in points.

subprocess.run([
    str(POPPLER), '-f', '1', '-singlefile', '-png', '-r', str(72 * SCALE),
    str(SOURCE), str(OUTPUT.with_suffix('')),
], check=True)

img = Image.open(OUTPUT).convert('RGB')
draw = ImageDraw.Draw(img)
font = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 7 * SCALE)
label_font = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', round(6.75 * SCALE))

def px(value):
    return round(value * SCALE)


# All schedule times use the 6.96 pt size. The Nov 4 column in the source PDF
# uses smaller text, so replace those eight times inside their existing rows.
group_rows = [
    (143.16, 157.68, '09:00'),
    (158.76, 173.28, '09:00 - 09:30'),
    (174.24, 188.76, '09:30 - 11:00'),
    (189.84, 204.24, '11:00 - 13:00'),
    (205.32, 219.84, '13:00 - 15:00'),
    (220.92, 235.32, '15:00 - 15:30'),
    (236.40, 250.92, '15:30 - 16:30'),
    (251.88, 266.40, '16:30 - 18:00'),
]
for top, bottom, time in group_rows:
    center = (top + bottom) / 2
    background = img.getpixel((px(475), px(top + 3)))
    # Shift the original PDF label without changing its font or wording.
    label_crop = img.crop((px(480.5), px(top + 1.2),
                           px(548), px(bottom - 1.2)))
    draw.rectangle((px(480.5), px(top + 1.2),
                    px(548), px(bottom - 1.2)), fill=background)
    img.paste(label_crop, (px(488.5), px(top + 1.2)))
    draw.rectangle((px(435.8), px(top + 1.2), px(480.5), px(bottom - 1.2)),
                   fill=background)
    draw.text((px(436.2), px(center)), time, font=font,
              fill='#687E99' if top not in (174.24, 205.32, 236.40) else
                   '#D62828' if top == 174.24 else '#0055A4',
              anchor='lm')


# The PDF has 10.92 pt Tea break bars and 12.96 pt Lunch bars. Make the two
# Lunch bars 10.92 pt high while keeping their center lines and text positions.
RED = '#D87A7A'
PALE = '#F5DCE0'
for x1, x2, title in [
    (140.16, 409.80, 'Lunch & TACC Poster'),
    (432.12, 701.88, 'Lunch & posters'),
]:
    old_top, old_bottom = 439.32, 452.28
    center = (old_top + old_bottom) / 2
    new_top, new_bottom = center - 5.46, center + 5.46
    draw.rectangle((px(x1), px(old_top), px(x2), px(old_bottom)), fill='#FFFFFF')
    draw.rounded_rectangle((px(x1), px(new_top), px(x2), px(new_bottom)),
                           radius=2 * SCALE, fill=RED)
    draw.rounded_rectangle((px(x1), px(new_top + 2.0), px(x1 + 1.5), px(new_bottom - 2.0)),
                           radius=round(0.75 * SCALE), fill=PALE)
    time = '12:00 - 13:30'
    draw.text((px(x1 + 5.9), px(center)), time, font=font,
              fill='#FFFFFF', anchor='lm')
    draw.text((px((x1 + x2) / 2), px(center)), title, font=label_font,
              fill='#FFFFFF', anchor='mm')


def recolor_box(x1, y1, x2, y2, old_fill, old_accent,
                new_fill, new_accent, corner_radius=1.8):
    """Change a box's fill and colored time/stripe, retaining its dark text."""
    region = (px(x1), px(y1), px(x2), px(y2))
    pixels = np.asarray(img.crop(region)).astype(np.float32)
    old_fill = np.asarray(old_fill, dtype=np.float32)
    old_accent = np.asarray(old_accent, dtype=np.float32)
    new_fill = np.asarray(new_fill, dtype=np.float32)
    new_accent = np.asarray(new_accent, dtype=np.float32)

    vector = old_accent - old_fill
    alpha = np.clip(np.sum((pixels - old_fill) * vector, axis=2) /
                    np.sum(vector * vector), 0, 1)
    predicted = old_fill + alpha[..., None] * vector
    residual = np.max(np.abs(pixels - predicted), axis=2)
    weight = np.clip((30 - residual) / 20, 0, 1)
    shape = Image.new('L', (pixels.shape[1], pixels.shape[0]), 0)
    ImageDraw.Draw(shape).rounded_rectangle(
        (0, 0, pixels.shape[1] - 1, pixels.shape[0] - 1),
        radius=round(corner_radius * SCALE), fill=255)
    weight *= np.asarray(shape, dtype=np.float32) / 255
    replacement = new_fill + alpha[..., None] * (new_accent - new_fill)
    updated = pixels * (1 - weight[..., None]) + replacement * weight[..., None]
    img.paste(Image.fromarray(updated.astype(np.uint8), 'RGB'), region[:2])


WHITE = (255, 255, 255)
GRAY = (239, 243, 247)
MUTED = (104, 126, 153)
PINK = (253, 235, 234)
RED_ACCENT = (214, 40, 40)
VISIT_SOURCE = (230, 240, 250)
VISIT = (220, 234, 247)
SESSION_SOURCE = (200, 221, 241)
SESSION = (190, 214, 236)
BLUE_ACCENT = (0, 85, 164)

# Nov 3 and 4: Social Event shares Visit's blue palette, while supporting
# rows use light gray. The academic-exchange panel keeps the PDF's pale red.
for y1, y2 in [(125.64, 140.04), (141.12, 155.64),
               (172.20, 186.72), (187.68, 202.20), (218.76, 233.28)]:
    recolor_box(140.16, y1, 409.80, y2, WHITE, MUTED, GRAY, MUTED)
recolor_box(140.16, 234.36, 409.80, 248.76,
            PINK, RED_ACCENT, VISIT, BLUE_ACCENT)
for y1, y2 in [(156.72, 171.12), (203.28, 217.80)]:
    recolor_box(140.16, y1, 409.80, y2,
                VISIT_SOURCE, BLUE_ACCENT, VISIT, BLUE_ACCENT)

recolor_box(432.12, 126.84, 564.60, 140.04,
            VISIT_SOURCE, BLUE_ACCENT, VISIT, BLUE_ACCENT)
for y1, y2, old_fill in [
    (143.16, 157.68, WHITE), (158.76, 173.28, WHITE),
    (189.84, 204.24, WHITE), (220.92, 235.32, (241, 245, 249)),
    (251.88, 266.40, WHITE),
]:
    recolor_box(432.12, y1, 564.60, y2, old_fill, MUTED, GRAY, MUTED)
recolor_box(432.12, 174.24, 564.60, 188.76,
            PINK, RED_ACCENT, VISIT, BLUE_ACCENT)
for y1, y2 in [(205.32, 219.84), (236.40, 250.92)]:
    recolor_box(432.12, y1, 564.60, y2,
                VISIT_SOURCE, BLUE_ACCENT, VISIT, BLUE_ACCENT)

# Nov 5 and 6: gray supporting rows have matching gray times and stripes.
for x1, x2 in [(140.16, 409.80), (432.12, 701.88)]:
    for y1, y2 in [(345.60, 359.64), (360.60, 374.64),
                   (516.96, 531.00)]:
        recolor_box(x1, y1, x2, y2, WHITE, MUTED, GRAY, MUTED)
    recolor_box(x1, 531.96, x2, 546.00,
                PINK, RED_ACCENT, GRAY, MUTED)

# Workshop sessions and both parallel-session columns are slightly deeper blue.
for y1, y2 in [(375.72, 400.56), (413.40, 438.36),
               (453.36, 478.20), (491.16, 516.00)]:
    recolor_box(140.16, y1, 409.80, y2,
                SESSION_SOURCE, BLUE_ACCENT, SESSION, BLUE_ACCENT)
recolor_box(432.12, 375.72, 701.88, 400.56,
            SESSION_SOURCE, BLUE_ACCENT, SESSION, BLUE_ACCENT)
for y1, y2 in [(413.40, 438.36), (453.36, 478.20),
               (491.16, 516.00)]:
    for x1, x2 in [(492.96, 596.16), (599.28, 701.88)]:
        recolor_box(x1, y1, x2, y2,
                    SESSION_SOURCE, BLUE_ACCENT, SESSION, BLUE_ACCENT)

img.save(OUTPUT, optimize=True)
print(f'{OUTPUT} {img.size}')
