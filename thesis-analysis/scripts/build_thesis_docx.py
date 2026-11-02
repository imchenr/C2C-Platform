from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor

import sys

SKILL_ROOT = Path("/Users/eddy/.codex/plugins/cache/openai-primary-runtime/documents/26.805.11740/skills/documents")
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
from table_geometry import apply_table_geometry, audit_docx_tables, column_widths_from_weights


ROOT = Path("/Users/eddy/Codes/design-platform/thesis-analysis")
SOURCE = ROOT / "校园二手交易平台-毕业论文正文.md"
OUTPUT = ROOT / "基于FastAPI与Vue的校园二手商品交易平台设计与实现-论文正文.docx"

BODY_CN = "Arial Unicode MS"
LATIN = "Times New Roman"
BLACK = RGBColor(0, 0, 0)
MUTED = RGBColor(90, 90, 90)
TABLE_HEAD = "E8EEE9"
TABLE_ALT = "F7F9F7"


def set_fonts(run, *, cn=BODY_CN, latin=LATIN, size=12, bold=False, color=BLACK, italic=False):
    run.font.name = latin
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr, name in (("ascii", latin), ("hAnsi", latin), ("eastAsia", cn), ("cs", latin)):
        rfonts.set(qn(f"w:{attr}"), name)


def style_font(style, *, size, bold=False, before=0, after=0, line=1.5, first_line=None, align=None, keep_next=False):
    style.font.name = LATIN
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = BLACK
    rpr = style._element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    rfonts.set(qn("w:ascii"), LATIN)
    rfonts.set(qn("w:hAnsi"), LATIN)
    rfonts.set(qn("w:eastAsia"), BODY_CN)
    pf = style.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if first_line is not None:
        pf.first_line_indent = Cm(first_line)
    if align is not None:
        pf.alignment = align
    pf.keep_with_next = keep_next
    pf.widow_control = True


def add_field(paragraph, code, placeholder=""):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar"); begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = code
    sep = OxmlElement("w:fldChar"); sep.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t"); text.text = placeholder
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, sep, text, end])


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def set_cell_margins(cell, top=90, bottom=90, start=110, end=110):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for side, value in (("top", top), ("bottom", bottom), ("start", start), ("end", end)):
        node = tc_mar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_settings(doc):
    settings = doc.settings._element
    update = settings.find(qn("w:updateFields"))
    if update is None:
        update = OxmlElement("w:updateFields")
        settings.append(update)
    update.set(qn("w:val"), "true")


def configure(doc):
    section = doc.sections[0]
    # The title page must not carry the running header or visible page number.
    section.different_first_page_header_footer = True
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(25.4)
    section.bottom_margin = Mm(25.4)
    section.left_margin = Mm(30)
    section.right_margin = Mm(25)
    section.header_distance = Mm(15)
    section.footer_distance = Mm(15)

    styles = doc.styles
    style_font(styles["Normal"], size=12, after=0, line=1.5, first_line=0.74, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    style_font(styles["Heading 1"], size=16, bold=True, before=16, after=12, line=1.25, align=WD_ALIGN_PARAGRAPH.CENTER, keep_next=True)
    style_font(styles["Heading 2"], size=14, bold=True, before=12, after=6, line=1.25, keep_next=True)
    style_font(styles["Heading 3"], size=12, bold=True, before=8, after=4, line=1.25, keep_next=True)
    style_font(styles["Caption"], size=10.5, before=4, after=8, line=1.1, align=WD_ALIGN_PARAGRAPH.CENTER, keep_next=False)

    set_repeat_settings(doc)


def add_header_footer(section):
    hp = section.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hp.paragraph_format.space_after = Pt(0)
    run = hp.add_run("基于 FastAPI 与 Vue 的校园二手商品交易平台设计与实现")
    set_fonts(run, size=9, color=MUTED)
    fp = section.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.space_before = Pt(0)
    add_field(fp, "PAGE", "1")


def cover(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(52)
    run = p.add_run("本科毕业论文")
    set_fonts(run, size=22, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(76)
    p.paragraph_format.space_after = Pt(20)
    run = p.add_run("基于 FastAPI 与 Vue 的校园二手商品\n交易平台设计与实现")
    set_fonts(run, size=24, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Design and Implementation of a Campus Second-hand Goods\nTrading Platform Based on FastAPI and Vue")
    set_fonts(run, size=13)

    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(48)
    spacer.paragraph_format.line_spacing = 1.0
    rows = [
        ("学生姓名", "________________"),
        ("学号", "________________"),
        ("专业", "________________"),
        ("指导教师", "________________"),
        ("学院", "________________"),
        ("完成日期", "2026 年 8 月"),
    ]
    table = doc.add_table(rows=0, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for label, value in rows:
        cells = table.add_row().cells
        cells[0].text = label
        cells[1].text = value
        for i, cell in enumerate(cells):
            set_cell_margins(cell, 70, 70, 140, 140)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(0)
            for run in p.runs:
                set_fonts(run, size=12, bold=(i == 0))
    repeat_header(table.rows[0])
    apply_table_geometry(table, [2300, 4200], table_width_dxa=6500, indent_dxa=140, cell_margins_dxa={"top":70,"bottom":70,"start":140,"end":140})
    # Remove borders for the cover information grid.
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        edge = OxmlElement(f"w:{side}")
        edge.set(qn("w:val"), "nil")
        borders.append(edge)

    doc.add_page_break()


def add_toc_pages(doc):
    p = doc.add_paragraph("目录", style="Heading 1")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    toc = doc.add_paragraph()
    add_field(toc, 'TOC \\o "1-3" \\h \\z \\u', "打开 Word 后按 Ctrl+A，再按 F9 更新目录和页码。")
    doc.add_page_break()
    p = doc.add_paragraph("图目录", style="Heading 1")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(doc.add_paragraph(), 'TOC \\h \\z \\c "图"', "打开 Word 后更新域生成图目录。")
    doc.add_page_break()
    p = doc.add_paragraph("表目录", style="Heading 1")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(doc.add_paragraph(), 'TOC \\h \\z \\c "表"', "打开 Word 后更新域生成表目录。")
    doc.add_page_break()


def inline_runs(paragraph, text, size=12, bold=False, italic=False, color=BLACK):
    parts = re.split(r"(`[^`]+`|\*\*[^*]+\*\*)", text)
    for part in parts:
        if not part:
            continue
        mono = part.startswith("`") and part.endswith("`")
        strong = part.startswith("**") and part.endswith("**")
        content = part[1:-1] if mono else part[2:-2] if strong else part
        run = paragraph.add_run(content)
        set_fonts(run, cn=BODY_CN, latin="Menlo" if mono else LATIN, size=10.5 if mono else size, bold=bold or strong, italic=italic, color=color)


def parse_table(lines, index):
    rows = []
    while index < len(lines) and lines[index].strip().startswith("|"):
        raw = lines[index].strip().strip("|")
        cells = [item.strip() for item in raw.split("|")]
        if not all(re.fullmatch(r":?-{3,}:?", item.replace(" ", "")) for item in cells):
            rows.append(cells)
        index += 1
    return rows, index


def weights_for(rows):
    cols = len(rows[0])
    if cols == 3:
        return [1.35, 2.35, 4.3]
    if cols == 4:
        return [0.8, 1.75, 4.1, 1.0]
    if cols == 6:
        return [2.7, 0.8, 0.8, 1.3, 1.3, 1.3]
    if cols == 2:
        return [1.8, 6.2]
    lengths = []
    for col in range(cols):
        lengths.append(max(max(len(row[col]) if col < len(row) else 0 for row in rows), 4))
    return lengths


def add_table(doc, rows, caption):
    if caption:
        p = doc.add_paragraph(caption, style="Caption")
        p.paragraph_format.keep_with_next = True
    cols = max(len(row) for row in rows)
    normalized = [row + [""] * (cols - len(row)) for row in rows]
    table = doc.add_table(rows=0, cols=cols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for ri, values in enumerate(normalized):
        cells = table.add_row().cells
        for ci, value in enumerate(values):
            cell = cells[ci]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            if ri == 0:
                set_cell_shading(cell, TABLE_HEAD)
            elif ri % 2 == 0:
                set_cell_shading(cell, TABLE_ALT)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            if ci == 0 and cols in (4, 6):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            inline_runs(p, value, size=9.2, bold=(ri == 0))
        if ri == 0:
            repeat_header(table.rows[-1])
    widths = column_widths_from_weights(weights_for(normalized), total_width_dxa=8000)
    apply_table_geometry(table, widths, table_width_dxa=8000, indent_dxa=110, cell_margins_dxa={"top":90,"bottom":90,"start":110,"end":110})
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_figure(doc, marker):
    match = re.fullmatch(r"\[\[FIG:([^|]+)\|([^|]+)\|([0-9.]+)\]\]", marker)
    if not match:
        return False
    rel, caption, width_cm = match.groups()
    path = ROOT / rel
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    picture = run.add_picture(str(path), width=Cm(float(width_cm)))
    doc_pr = picture._inline.docPr
    doc_pr.set("name", caption)
    doc_pr.set("title", caption)
    doc_pr.set("descr", caption)
    cp = doc.add_paragraph(caption, style="Caption")
    return True


def build():
    doc = Document()
    configure(doc)
    cover(doc)
    add_toc_pages(doc)
    for section in doc.sections:
        add_header_footer(section)

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    idx = 1  # skip Markdown title; the title is already on the cover
    pending_table_caption = ""
    first_major = True
    in_references = False
    suppress_next_major_break = False
    while idx < len(lines):
        text = lines[idx].strip()
        if not text or text == "---":
            idx += 1
            continue
        table_marker = re.fullmatch(r"\[\[TABLE:(.+)\]\]", text)
        if table_marker:
            pending_table_caption = table_marker.group(1)
            idx += 1
            continue
        if text.startswith("|"):
            rows, idx = parse_table(lines, idx)
            add_table(doc, rows, pending_table_caption)
            pending_table_caption = ""
            continue
        if add_figure(doc, text):
            idx += 1
            continue
        heading = re.match(r"^(#{2,4})\s+(.+)$", text)
        if heading:
            hashes, label = heading.groups()
            level = len(hashes) - 1
            if level == 1 and (label.startswith("第 ") or label in {"参考文献", "致谢"} or label.startswith("附录")):
                if not first_major and not suppress_next_major_break:
                    doc.add_page_break()
                first_major = False
                suppress_next_major_break = False
            if label == "参考文献":
                in_references = True
            elif level == 1 and label != "参考文献":
                in_references = False
            p = doc.add_paragraph(style=f"Heading {min(level, 3)}")
            inline_runs(p, label, size={1: 16, 2: 14, 3: 12}[min(level, 3)], bold=True)
            idx += 1
            continue
        p = doc.add_paragraph()
        p.paragraph_format.keep_together = False
        if in_references or re.match(r"^\[\d+\]", text):
            p.paragraph_format.first_line_indent = Cm(-0.74)
            p.paragraph_format.left_indent = Cm(0.74)
            p.paragraph_format.line_spacing = 1.25
            p.paragraph_format.space_after = Pt(4)
            inline_runs(p, text, size=10.5)
        elif text.startswith("关键词：") or text.startswith("Keywords:"):
            p.paragraph_format.first_line_indent = Cm(0)
            inline_runs(p, text, size=11.5, bold=False)
        else:
            inline_runs(p, text, size=12)
        if text.startswith("本章") and idx + 1 < len(lines):
            # A short chapter summary occasionally consumes only a few lines.
            # When it already ends on a nearly empty page, avoid inserting a
            # second explicit page break before the next major heading.
            lookahead = idx + 1
            while lookahead < len(lines) and not lines[lookahead].strip():
                lookahead += 1
            if lookahead < len(lines) and re.match(r"^##\s+(第 |参考文献|致谢|附录)", lines[lookahead].strip()):
                suppress_next_major_break = True
        idx += 1

    doc.core_properties.title = "基于 FastAPI 与 Vue 的校园二手商品交易平台设计与实现"
    doc.core_properties.subject = "本科毕业论文正文"
    doc.core_properties.author = ""
    doc.core_properties.keywords = "校园二手交易, FastAPI, Vue 3, 前后端分离"
    doc.save(OUTPUT)

    if audit_docx_tables(OUTPUT):
        raise RuntimeError("table geometry audit failed")
    print(OUTPUT)


if __name__ == "__main__":
    build()
