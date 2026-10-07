"""Convert the workshop program DOCX into the site's detailed HTML page."""

from html import escape
from pathlib import Path
from sys import argv
from xml.etree import ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(argv[1]) if len(argv) > 1 else Path(
    r"C:\Users\henry\Downloads\Taiwan-France Workshop Program_261006.docx"
)
OUTPUT = ROOT / "program-overview.html"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def content(element):
    pieces = []
    for item in element.iter():
        if item.tag == W + "t":
            pieces.append(item.text or "")
        elif item.tag == W + "br":
            pieces.append("\n")
        elif item.tag == W + "tab":
            pieces.append("    ")
    return "".join(pieces)


def cell_lines(cell):
    return [content(paragraph) for paragraph in cell.findall(W + "p")]


def cell_span(cell):
    properties = cell.find(W + "tcPr")
    span = properties.find(W + "gridSpan") if properties is not None else None
    return int(span.get(W + "val", "1")) if span is not None else 1


def merge_state(cell):
    properties = cell.find(W + "tcPr")
    merge = properties.find(W + "vMerge") if properties is not None else None
    return merge.get(W + "val", "continue") if merge is not None else None


with ZipFile(SOURCE) as archive:
    root = ET.fromstring(archive.read("word/document.xml"))
body = root.find(W + "body")
blocks = list(body)
paragraphs = [content(block) for block in blocks if block.tag == W + "p"]
tables = [block for block in blocks if block.tag == W + "tbl"]


def render_table(table, index, label):
    rows = [row.findall(W + "tc") for row in table.findall(W + "tr")]
    result = [f'<div class="detail-table-scroll"><table class="detail-table detail-table-{index}" aria-label="{escape(label)}">']
    for row_index, cells in enumerate(rows):
        if row_index == 0:
            result.append("<thead>")
        elif row_index == 1:
            result.append("</thead><tbody>")

        row_text = " ".join(content(cell) for cell in cells)
        row_class = ""
        if row_index and (row_text.startswith("Session ") or row_text.startswith("Joint Session ")):
            row_class = ' class="detail-session-band"'
        elif index == 4 and row_index in (8, 9, 14, 21):
            row_class = ' class="detail-track-band"'
        elif row_index and len(cells) <= 2 and any(
            term in row_text for term in ("Tea Break", "Lunch & Poster", "Registration", "Opening Ceremony", "Closing", "Banquet", "Farewell Party")
        ):
            row_class = ' class="detail-event-row"'
        result.append(f"<tr{row_class}>")

        for column_index, cell in enumerate(cells):
            state = merge_state(cell)
            if state == "continue":
                continue
            span = cell_span(cell)
            rowspan = 1
            if state == "restart":
                for later in rows[row_index + 1:]:
                    if column_index >= len(later) or merge_state(later[column_index]) != "continue":
                        break
                    rowspan += 1
            tag = "th" if row_index == 0 else "td"
            attrs = []
            if row_index == 0:
                attrs.append('scope="col"')
            if span > 1:
                attrs.append(f'colspan="{span}"')
            if rowspan > 1:
                attrs.append(f'rowspan="{rowspan}"')
            if column_index == 0 and row_index > 0 and len(cells) > 1:
                attrs.append('class="detail-time"')
            attr_text = (" " + " ".join(attrs)) if attrs else ""
            lines = cell_lines(cell)
            value = "".join(
                f'<span class="detail-cell-line">{escape(line).replace(chr(10), "<br>")}</span>'
                for line in lines if line
            )
            result.append(f"<{tag}{attr_text}>{value}</{tag}>")
        result.append("</tr>")
    result.append("</tbody></table></div>")
    return "\n".join(result)


def line(value):
    return escape(value).replace("    ", "&emsp;")


nav = """<header class="site-header">
  <nav class="navbar" aria-label="Main navigation">
    <a class="brand" href="index.html#top" aria-label="Taiwan–France Cybersecurity & AI Workshop 2026 home"><span class="brand-mark">TW×FR</span><span class="brand-text">Research Workshop 2026</span></a>
    <button class="nav-toggle" aria-label="Open navigation" aria-expanded="false">☰</button>
    <ul class="nav-menu">
      <li><a href="index.html#top">Home</a></li>
      <li class="nav-dropdown"><a href="index.html#program">Program</a><button class="nav-submenu-toggle" type="button" aria-label="Show Program options" aria-expanded="false" aria-controls="program-submenu"></button>
        <ul class="nav-submenu" id="program-submenu"><li><a href="index.html#program-at-a-glance">Program At A Glance</a></li><li><a href="program-overview.html" aria-current="page">Program Overview</a></li><li><a href="index.html#speakers">Speakers</a></li></ul>
      </li>
      <li><a href="index.html#partners">Partners</a></li>
      <li class="nav-dropdown"><a href="index.html#submissions">Call for Posters</a><button class="nav-submenu-toggle" type="button" aria-label="Show Call for Posters options" aria-expanded="false" aria-controls="posters-submenu"></button>
        <ul class="nav-submenu" id="posters-submenu"><li><a href="call-for-posters.html#call-for-poster">Call for Poster</a></li><li><a href="call-for-posters.html#accepted-poster">Accepted Poster</a></li><li><a href="call-for-posters.html#best-poster-award">Best Poster Award</a></li></ul>
      </li>
      <li><a href="index.html#practical-info">Practical Information</a></li><li><a href="index.html#contact">Contact Us</a></li>
    </ul>
  </nav>
</header>"""

parts = [
    "<!DOCTYPE html>", '<html lang="en">', "<head>",
    '  <meta charset="UTF-8">',
    '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
    '  <meta name="description" content="Complete provisional program for the 2026 Taiwan–France Joint Research Workshop on Cybersecurity & AI.">',
    '  <title>Program Overview | Taiwan–France Cybersecurity &amp; AI Workshop 2026</title>',
    '  <link rel="preconnect" href="https://fonts.googleapis.com">',
    '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
    '  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">',
    '  <link rel="stylesheet" href="assets/css/style.css?v=20261008-18">',
    "</head>", '<body><div id="top"></div>', nav,
    '<main class="detail-page"><div class="container detail-content">',
    '<a class="detail-back" href="index.html#program">← Back to Program</a>',
    '<header class="detail-intro">',
    f'<h1>{line(paragraphs[0])}<br>{line(paragraphs[1])}</h1>',
    f'<p class="detail-version">{line(paragraphs[2])}</p>',
    f'<p class="detail-venue">{line(paragraphs[3])}</p>',
    '</header>',
    '<nav class="detail-contents" aria-label="On this page"><a href="#overview">Overview</a><a href="#talk-format">Talk Format</a><a href="#visits">Visits</a><a href="#workshop-program">Workshop Program</a></nav>',
    '<section id="overview" class="detail-section">',
    f'<h2>{line(paragraphs[4])}</h2>',
    render_table(tables[0], 0, "Workshop overview"),
    '</section>',
    '<section id="talk-format" class="detail-section">',
    f'<h2>{line(paragraphs[5])}</h2><ul class="detail-notes">',
    *(f'<li>{line(value)}</li>' for value in paragraphs[6:10]),
    '</ul></section>',
    '<section id="visits" class="detail-section">',
    f'<h2>{line(paragraphs[10])}</h2>',
    f'<h3 id="nov-3">{line(paragraphs[11])}</h3>',
    render_table(tables[1], 1, "Tuesday 3 November visits"),
    f'<h3 id="nov-4">{line(paragraphs[13])}</h3>',
    render_table(tables[2], 2, "Wednesday 4 November visits and exchange"),
    '</section>',
    '<section id="workshop-program" class="detail-section">',
    f'<h2>{line(paragraphs[14])}</h2>',
    f'<h3 id="nov-5">{line(paragraphs[15])}</h3>',
    f'<p class="detail-legend">{line(paragraphs[16])}</p>',
    render_table(tables[3], 3, "Thursday 5 November workshop program"),
    f'<h3 id="nov-6">{line(paragraphs[17])}</h3>',
    f'<p class="detail-legend">{line(paragraphs[18])}</p>',
    render_table(tables[4], 4, "Friday 6 November workshop program"),
    '</section>',
    '<p class="detail-return"><a href="index.html#program">← Back to Program</a></p>',
    '</div></main>',
    '<footer class="site-footer"><div class="container footer-inner"><p>© 2026 Taiwan–France Cybersecurity &amp; AI Workshop.</p><a href="#top">Back to top ↑</a></div></footer>',
    '<script src="assets/js/main.js"></script>',
    '</body></html>',
]

OUTPUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
print(f"Created {OUTPUT}")
