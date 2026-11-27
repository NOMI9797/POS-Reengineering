"""Convert a report written in Markdown into a formatted Word (.docx) file.

Mermaid code blocks are rendered to PNG images with the Mermaid CLI (mmdc).
Tables with 9+ columns are placed on their own landscape page.

Usage: python md2docx.py <input.md> <output.docx> <path to mmdc> <work dir for images>
Needs: pip install python-docx==1.1.2 ; npm install @mermaid-js/mermaid-cli@11.4.2
"""
import re
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

SRC, OUT, MMDC, WORK = map(Path, sys.argv[1:5])
WORK.mkdir(parents=True, exist_ok=True)

PORTRAIT_TEXT_WIDTH = Cm(17.0)   # A4 21 cm - 2 x 2 cm margins
LANDSCAPE_TEXT_WIDTH = Cm(25.7)  # A4 29.7 cm - 2 x 2 cm margins
CODE_FONT = "Courier New"
NAVY = RGBColor(0x1F, 0x3A, 0x5F)

doc = Document()
first = doc.sections[0]
first.page_height, first.page_width = Cm(29.7), Cm(21.0)
for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(first, side, Cm(2.0))

doc.styles["Normal"].font.name = "Calibri"
doc.styles["Normal"].font.size = Pt(10.5)
for level, size in ((1, 20), (2, 15), (3, 12)):
    style = doc.styles[f"Heading {level}"]
    style.font.name = "Calibri"
    style.font.size = Pt(size)
    style.font.color.rgb = NAVY

INLINE = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`)")


def add_runs(par, text, size=None, bold=False):
    """Add text with **bold** and `code` spans."""
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = par.add_run(part[2:-2])
            run.bold = True
        elif part.startswith("`") and part.endswith("`"):
            run = par.add_run(part[1:-1])
            run.font.name = CODE_FONT
            run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        else:
            run = par.add_run(part)
            run.bold = bold or None
        if size:
            run.font.size = size


def shade(properties, fill):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    properties.append(shd)


def new_section(landscape):
    section = doc.add_section(WD_SECTION.NEW_PAGE)
    section.orientation = WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
    long_side, short_side = Cm(29.7), Cm(21.0)
    if landscape:
        section.page_width, section.page_height = long_side, short_side
    else:
        section.page_width, section.page_height = short_side, long_side
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(section, side, Cm(2.0))


def column_weights(rows, ncols):
    """Width per column: proportional to content, never narrower than its longest word."""
    weights = []
    for c in range(ncols):
        texts = [row[c] if c < len(row) else "" for row in rows]
        longest = max(len(re.sub(r"[`*]", "", t)) for t in texts)
        word = max((len(w) * (1.35 if "`" in t else 1.1)
                    for t in texts for w in re.sub(r"[`*]", "", t).split()), default=4)
        weights.append(max(min(longest, 45), word * 1.25 + 5, 7))
    return weights


def add_table(rows):
    header, body = rows[0], rows[1:]
    ncols = len(header)
    wide = ncols >= 9
    width = LANDSCAPE_TEXT_WIDTH if wide else PORTRAIT_TEXT_WIDTH
    if wide:
        new_section(landscape=True)
    font = Pt(8) if ncols >= 7 else Pt(9)

    table = doc.add_table(rows=1, cols=ncols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, text in enumerate(header):
        cell = table.rows[0].cells[i]
        add_runs(cell.paragraphs[0], text, size=font, bold=True)
        shade(cell._tc.get_or_add_tcPr(), "DCE6F1")
    repeat = OxmlElement("w:tblHeader")       # header row repeats on every page
    repeat.set(qn("w:val"), "true")
    table.rows[0]._tr.get_or_add_trPr().append(repeat)
    for row in body:
        cells = table.add_row().cells
        for i in range(ncols):
            add_runs(cells[i].paragraphs[0], row[i] if i < len(row) else "", size=font)

    weights = column_weights(rows, ncols)
    widths = [int(width * w / sum(weights)) for w in weights]
    table.autofit = False
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    table._tbl.tblPr.append(layout)
    for c, grid_col in enumerate(table._tbl.tblGrid.findall(qn("w:gridCol"))):
        grid_col.set(qn("w:w"), str(int(widths[c] / 635)))   # EMU -> twentieths of a point
    for row in table.rows:
        for c, cell in enumerate(row.cells):
            cell.width = widths[c]

    if wide:
        new_section(landscape=False)
    else:
        doc.add_paragraph()


def add_code(lines):
    for line in lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Cm(0.3)
        shade(p._p.get_or_add_pPr(), "F3F4F6")
        run = p.add_run(line if line else " ")
        run.font.name = CODE_FONT
        run.font.size = Pt(8)
    doc.add_paragraph()


figure_no = 0


def add_mermaid(lines):
    global figure_no
    figure_no += 1
    source = WORK / f"diagram{figure_no}.mmd"
    image = WORK / f"diagram{figure_no}.png"
    source.write_text("\n".join(lines), encoding="utf-8")
    subprocess.run([str(MMDC), "-i", str(source), "-o", str(image),
                    "-b", "white", "-s", "3", "-q"], check=True)
    picture = doc.add_picture(str(image), width=PORTRAIT_TEXT_WIDTH)
    max_height = Cm(21.0)                      # keep tall diagrams on one page
    if picture.height > max_height:
        picture.width = int(picture.width * max_height / picture.height)
        picture.height = max_height
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption = doc.add_paragraph()
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = caption.add_run(f"Figure {figure_no}")
    run.italic = True
    run.font.size = Pt(9)


def add_title_page(title, extra_lines):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(120)
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(26)
    run.font.color.rgb = NAVY
    for k, text in enumerate(extra_lines):
        q = doc.add_paragraph()
        q.alignment = WD_ALIGN_PARAGRAPH.CENTER
        q.add_run(text).font.size = Pt(14 if k == 0 else 12)
    doc.add_page_break()
    doc.add_heading("Contents", level=1)
    toc = doc.add_paragraph()
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), 'TOC \\o "1-2" \\h \\z \\u')
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = "Right-click here and choose Update Field to build the table of contents."
    r.append(t)
    field.append(r)
    toc._p.append(field)
    doc.add_page_break()


def add_page_numbers():
    footer = doc.sections[0].footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run()
    for kind, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if kind:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        run._r.append(el)


lines = SRC.read_text(encoding="utf-8").splitlines()
i = 0
title_done = False
while i < len(lines):
    line = lines[i]

    if line.startswith("```"):
        language = line[3:].strip()
        block = []
        i += 1
        while not lines[i].startswith("```"):
            block.append(lines[i])
            i += 1
        i += 1
        if language == "mermaid":
            add_mermaid(block)
        else:
            add_code(block)
        continue

    if line.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            if not re.match(r"^\|\s*-", lines[i]):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
            i += 1
        add_table(rows)
        continue

    heading = re.match(r"^(#{1,3}) (.*)", line)
    if heading:
        level, text = len(heading.group(1)), heading.group(2)
        if level == 1 and not title_done:
            # title page: the title plus the next two non-empty lines (subtitle, byline)
            j, extra = i + 1, []
            while len(extra) < 2 and j < len(lines):
                if lines[j].strip():
                    extra.append(lines[j].strip())
                j += 1
            add_title_page(text, extra)
            title_done = True
            i = j
            continue
        if level == 2 and not text.startswith("1."):
            doc.add_page_break()       # each main section starts on a new page
        doc.add_heading(text.replace("`", ""), level=level)
        i += 1
        continue

    numbered = re.match(r"^(\d+)\. (.*)", line)
    if numbered:
        add_runs(doc.add_paragraph(style="List Number"), numbered.group(2))
    elif line.startswith("- "):
        add_runs(doc.add_paragraph(style="List Bullet"), line[2:])
    elif line.strip():
        add_runs(doc.add_paragraph(), line)
    i += 1

add_page_numbers()
doc.save(OUT)
print(f"saved {OUT} with {figure_no} diagrams")
