from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / 'assets/images/program-at-a-glance.png'
W, H = 2400, 2300
BG = '#f7f9fc'
WHITE = '#ffffff'
INK = '#17345a'
MUTED = '#687e99'
LINE = '#d9e3ee'
BLUE = '#0055a4'
RED = '#d62828'
FILLS = {
    'plain': '#ffffff',
    'visit': '#e6f0fa',
    'social': '#fdebea',
    'session': '#e6f0fa',
    'poster': '#fdebea',
    'evening': '#fdebea',
    'break': '#f1f5f9',
}
ACCENTS = {
    'plain': MUTED,
    'visit': BLUE,
    'social': RED,
    'session': BLUE,
    'poster': RED,
    'evening': RED,
    'break': MUTED,
}

img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
arial = 'C:/Windows/Fonts/arial.ttf'
arial_bold = 'C:/Windows/Fonts/arialbd.ttf'

def f(size, bold=False):
    return ImageFont.truetype(arial_bold if bold else arial, size)

TITLE = f(83, True)
SUB = f(33)
SMALL = f(25)
DATE_FONT = f(58, True)
CARD_TITLE = f(42, True)
TIME = f(27, True)
LABEL = f(30, True)
DETAIL = f(23)
GROUP_HEAD = f(26, True)
GROUP_TIME = f(22, True)
GROUP_LABEL = f(25, True)

def wrap(text, font, width):
    lines, line = [], ''
    for word in text.split(' '):
        candidate = (line + ' ' + word).strip()
        if line and d.textlength(candidate, font=font) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines

MARGIN, GAP = 90, 36
CARD_W = (W - 2*MARGIN - GAP)//2

def card(x, y, h, day, title, color, rows):
    d.rounded_rectangle((x, y, x+CARD_W, y+h), radius=25,
                        fill=WHITE, outline=LINE, width=2)
    d.rounded_rectangle((x+18, y+18, x+CARD_W-18, y+117),
                        radius=16, fill=color)
    d.text((x+43, y+68), day, font=DATE_FONT, fill=WHITE, anchor='lm')
    d.text((x+31, y+138), title, font=CARD_TITLE, fill=INK)
    yy = y+200
    workshop_day = day in ('THU 5 NOV', 'FRI 6 NOV')
    for start, end, label, detail, category in rows:
        rh = ({'session': 96, 'break': 42, 'poster': 50}
              .get(category, 54) if workshop_day else 56)
        if workshop_day and label.startswith('Parallel '):
            security, ai = (part.strip() for part in detail.split('|'))
            security = security.removeprefix('Security: ')
            d.text((x+48, yy+31), label, font=f(21, True),
                   fill=BLUE, anchor='lm')
            d.text((x+48, yy+66), f'{start}–{end}', font=TIME,
                   fill=BLUE, anchor='lm')
            boxes = [(x+260, x+659), (x+671, x+CARD_W-25)]
            for bx1, bx2 in boxes:
                d.rounded_rectangle((bx1, yy, bx2, yy+rh),
                                    radius=10, fill='#c8ddf1')
                d.rounded_rectangle((bx1, yy+8, bx1+6, yy+rh-8),
                                    radius=3, fill=BLUE)
            parallel_topic_font = f(25, True)
            if d.textlength(security, font=parallel_topic_font) > boxes[0][1]-boxes[0][0]-30:
                raise RuntimeError(f'{day}: parallel topic too long: {security}')
            d.text(((boxes[0][0]+boxes[0][1])/2, yy+rh/2), security,
                   font=parallel_topic_font, fill=INK, anchor='mm')
            d.text(((boxes[1][0]+boxes[1][1])/2, yy+rh/2), ai,
                   font=LABEL, fill=INK, anchor='mm')
            yy += rh+4
            continue
        strong_session = workshop_day and category == 'session'
        soft_poster = workshop_day and category == 'poster'
        soft_break = workshop_day and category == 'break'
        fill = '#c8ddf1' if strong_session else RED if soft_poster or soft_break else FILLS[category]
        outline = LINE if category == 'plain' else None
        d.rounded_rectangle((x+25, yy, x+CARD_W-25, yy+rh),
                            radius=10, fill=fill,
                            outline=outline,
                            width=1)
        d.rounded_rectangle((x+25, yy+8, x+31, yy+rh-8),
                            radius=3, fill=BLUE if strong_session else '#f5dce0' if soft_poster or soft_break else ACCENTS[category])
        time_text = start if not end else f'{start}–{end}'
        center_y = yy + rh/2
        time_color = BLUE if strong_session else WHITE if soft_poster or soft_break else ACCENTS[category]
        label_color = INK if strong_session else WHITE if soft_poster or soft_break else INK
        detail_color = '#4d7095' if strong_session else '#f8e8ea' if soft_poster or soft_break else MUTED
        compact_font = f(24, True) if soft_poster or soft_break else TIME
        d.text((x+48, center_y), time_text, font=compact_font,
               fill=time_color, anchor='lm')
        meal_or_break = 'lunch' in label.lower() or 'break' in label.lower()
        label_x = x+CARD_W/2 if meal_or_break else x+435 if workshop_day else x+285
        label_anchor = 'mm' if meal_or_break or workshop_day else 'lm'
        row_label_font = f(26, True) if soft_poster or soft_break else LABEL
        d.text((label_x, center_y), label, font=row_label_font,
               fill=label_color, anchor=label_anchor)
        if detail:
            detail_x = x+765 if meal_or_break else x+585
            detail_width = CARD_W-790 if meal_or_break else CARD_W-610
            row_detail_font = f(21) if soft_poster or soft_break else DETAIL
            if d.textlength(detail, font=row_detail_font) > detail_width:
                raise RuntimeError(f'{day}: detail too long: {detail}')
            d.text((detail_x, center_y), detail, font=row_detail_font,
                   fill=detail_color, anchor='lm')
        yy += rh+4
    if yy > y+h-18:
        raise RuntimeError(f'{day} content exceeds card by {yy-(y+h-18)} px')

def nov4_groups(x, y):
    inset, gap = 25, 18
    col_w = (CARD_W - 2*inset - gap)//2
    lx = x+inset
    rx = lx+col_w+gap
    head_y = y+205
    rows_y = head_y+63
    rows = [
        ('09:00', 'Meet', 'plain'),
        ('09:00–09:30', 'Transfer', 'plain'),
        ('09:30–11:00', 'Social Event', 'social'),
        ('11:00–13:00', 'Lunch & transfer', 'plain'),
        ('13:00–15:00', 'Visit', 'visit'),
        ('15:00–15:30', 'Transfer / break', 'break'),
        ('15:30–16:30', 'Visit', 'visit'),
        ('16:30–18:00', 'Return / free time', 'plain'),
    ]
    d.rounded_rectangle((lx, head_y, lx+col_w, head_y+51),
                        radius=10, fill=FILLS['visit'])
    d.rounded_rectangle((rx, head_y, rx+col_w, head_y+51),
                        radius=10, fill=FILLS['social'])
    d.text((lx+18, head_y+26), 'MAIN GROUP', font=GROUP_HEAD,
           fill=BLUE, anchor='lm')
    d.text((rx+18, head_y+26), "PROF. MARION'S GROUP", font=GROUP_HEAD,
           fill=RED, anchor='lm')
    ry = rows_y
    for time_text, label, category in rows:
        rh = 56
        d.rounded_rectangle((lx, ry, lx+col_w, ry+rh), radius=9,
                            fill=FILLS[category],
                            outline=LINE if category == 'plain' else None,
                            width=1)
        d.rounded_rectangle((lx, ry+8, lx+6, ry+rh-8),
                            radius=3, fill=ACCENTS[category])
        center = ry+rh/2
        d.text((lx+16, center), time_text, font=GROUP_TIME,
               fill=ACCENTS[category], anchor='lm')
        if d.textlength(label, font=GROUP_LABEL) > col_w-196:
            raise RuntimeError('Nov 4 group label too wide: '+label)
        meal_or_break = 'lunch' in label.lower() or 'break' in label.lower()
        label_x = lx+col_w/2 if meal_or_break else lx+190
        label_anchor = 'mm' if meal_or_break else 'lm'
        d.text((label_x, center), label, font=GROUP_LABEL,
               fill=INK, anchor=label_anchor)
        ry += rh+4
    panel_bottom = ry-4
    d.rounded_rectangle((rx, rows_y, rx+col_w, panel_bottom),
                        radius=13, fill=FILLS['social'])
    d.rounded_rectangle((rx, rows_y+14, rx+7, panel_bottom-14),
                        radius=3, fill=RED)
    d.text((rx+32, rows_y+38), 'ALL DAY', font=GROUP_HEAD,
           fill=RED, anchor='lm')
    d.text((rx+32, rows_y+133), 'Academic exchange',
           font=f(34, True), fill=INK, anchor='lm')
    d.text((rx+32, rows_y+187), 'Academia Sinica',
           font=f(27), fill=MUTED, anchor='lm')
    d.text((rx+32, panel_bottom-52), 'Program details TBC',
           font=SMALL, fill=MUTED, anchor='lm')

d.text((MARGIN, 65), 'Program At A Glance', font=TITLE, fill=BLUE)
d.text((MARGIN, 165), '2026 Taiwan–France Joint Research Workshop on Cybersecurity & AI',
       font=SUB, fill=MUTED)
d.text((MARGIN, 216), '3–6 November 2026  ·  Provisional program updated 6 October 2026',
       font=SMALL, fill=MUTED)
d.rounded_rectangle((MARGIN, 260, MARGIN+740, 269), radius=4, fill=BLUE)
d.rounded_rectangle((MARGIN+740, 260, MARGIN+1480, 269), radius=4, fill=WHITE, outline=LINE, width=1)
d.rounded_rectangle((MARGIN+1480, 260, W-MARGIN, 269), radius=4, fill=RED)

left = MARGIN
right = MARGIN+CARD_W+GAP
top = 285
top_h = 820
bottom = 1135
bottom_h = 1060

card(left, top, top_h, 'TUE 3 NOV', 'Taipei', BLUE, [
    ('09:20', '', 'Meet', 'Academia Sinica main gate', 'plain'),
    ('09:20', '10:00', 'Transfer', 'To NTU', 'plain'),
    ('10:00', '12:00', 'Visit', '', 'visit'),
    ('12:00', '12:30', 'Transfer', 'To lunch venue', 'plain'),
    ('12:30', '14:00', 'Lunch', 'At NTU', 'plain'),
    ('14:00', '15:30', 'Visit', 'To be confirmed', 'visit'),
    ('15:30', '16:00', 'Transfer', '', 'plain'),
    ('16:00', '18:00', 'Social Event', '', 'social'),
])

card(right, top, top_h, 'WED 4 NOV', 'Academia Sinica / Hsinchu', RED, [])
nov4_groups(right, top)

card(left, bottom, bottom_h, 'THU 5 NOV', 'Security workshop', BLUE, [
    ('09:00', '09:30', 'Registration', 'Poster set-up', 'plain'),
    ('09:30', '10:10', 'Opening', 'Ceremony & group photo', 'plain'),
    ('10:10', '10:40', 'Session 1', 'Malware Analysis', 'session'),
    ('10:40', '11:00', 'Tea break', '', 'break'),
    ('11:00', '12:00', 'Session 2', 'Malware & Threat Detection', 'session'),
    ('12:00', '13:30', 'Lunch & TACC Poster', '', 'poster'),
    ('13:30', '14:45', 'Session 3', 'Trustworthy Systems & AI Threats', 'session'),
    ('14:45', '15:15', 'Tea break', '', 'break'),
    ('15:15', '16:45', 'Session 4', 'Malware & Cyber Threats', 'session'),
    ('16:45', '17:00', 'Closing', '', 'plain'),
    ('19:00', '21:30', 'Banquet', '', 'evening'),
])

card(right, bottom, bottom_h, 'FRI 6 NOV', 'Joint + parallel', RED, [
    ('09:00', '09:30', 'Registration', 'Poster set-up', 'plain'),
    ('09:30', '09:50', 'Opening', 'Ceremony & group photo', 'plain'),
    ('09:50', '10:50', 'Joint session', 'AI Security · 20-minute talks', 'session'),
    ('10:50', '11:15', 'Tea break', 'Tracks split', 'break'),
    ('11:15', '12:00', 'Parallel 1', 'Security: AI Security  |  AI (1)', 'session'),
    ('12:00', '13:30', 'Lunch & posters', 'TACC Research Posters', 'poster'),
    ('13:30', '14:45', 'Parallel 2', 'Security: Cybersecurity & Wireless  |  AI (2)', 'session'),
    ('14:45', '15:15', 'Tea break', '', 'break'),
    ('15:15', '16:45', 'Parallel 3', 'Security: Hardware & Crypto  |  AI (3)', 'session'),
    ('16:45', '17:00', 'Closing', 'Joint ceremony', 'plain'),
    ('19:00', '21:30', 'Farewell party', '', 'evening'),
])

d.line((MARGIN, 2230, W-MARGIN, 2230), fill=LINE, width=2)
d.text((MARGIN, 2250), 'Poster presenters stand by their posters 13:00–13:30 on both days.  Session and speaker details remain in the full provisional program.',
       font=SMALL, fill=MUTED)

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, optimize=True)
print(OUT.resolve(), img.size)
