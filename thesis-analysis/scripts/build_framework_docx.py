from pathlib import Path
import re

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor, Twips

import sys
SKILL_ROOT = Path('/Users/eddy/.codex/plugins/cache/openai-primary-runtime/documents/26.805.11740/skills/documents')
sys.path.insert(0, str(SKILL_ROOT / 'scripts'))
from table_geometry import apply_table_geometry, column_widths_from_weights


ROOT = Path('/Users/eddy/Codes/design-platform')
SOURCE = ROOT / 'thesis-analysis/校园二手交易平台-毕业论文详细框架.md'
OUTPUT = ROOT / 'thesis-analysis/基于FastAPI与Vue的校园二手交易平台-毕业论文详细框架.docx'

ACCENT = RGBColor(31, 78, 121)
DARK = RGBColor(31, 31, 31)
MUTED = RGBColor(89, 89, 89)
TABLE_FILL = 'E8EEF5'
ALT_FILL = 'F6F8FA'
BODY_CN = 'Arial Unicode MS'
HEADING_CN = 'Arial Unicode MS'
LATIN = 'Times New Roman'


def set_east_asia_font(run, cn=BODY_CN, latin=LATIN, size=None, bold=None, color=None):
    run.font.name = latin
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.insert(0, rfonts)
    rfonts.set(qn('w:ascii'), latin)
    rfonts.set(qn('w:hAnsi'), latin)
    rfonts.set(qn('w:eastAsia'), cn)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def configure_style(style, cn, latin, size, color=DARK, bold=False, before=0, after=6, line=1.25):
    style.font.name = latin
    style._element.rPr.rFonts.set(qn('w:ascii'), latin)
    style._element.rPr.rFonts.set(qn('w:hAnsi'), latin)
    style._element.rPr.rFonts.set(qn('w:eastAsia'), cn)
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = color
    pf = style.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn('w:shd'))
    if shd is None:
        shd = OxmlElement('w:shd')
        tc_pr.append(shd)
    shd.set(qn('w:fill'), fill)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tag = OxmlElement('w:tblHeader')
    tag.set(qn('w:val'), 'true')
    tr_pr.append(tag)


def add_field(paragraph, field_code):
    run = paragraph.add_run()
    fld_begin = OxmlElement('w:fldChar')
    fld_begin.set(qn('w:fldCharType'), 'begin')
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = field_code
    fld_sep = OxmlElement('w:fldChar')
    fld_sep.set(qn('w:fldCharType'), 'separate')
    text = OxmlElement('w:t')
    text.text = '1'
    fld_end = OxmlElement('w:fldChar')
    fld_end.set(qn('w:fldCharType'), 'end')
    run._r.extend([fld_begin, instr, fld_sep, text, fld_end])


def add_toc(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement('w:fldChar'); begin.set(qn('w:fldCharType'), 'begin')
    instr = OxmlElement('w:instrText'); instr.set(qn('xml:space'), 'preserve'); instr.text = 'TOC \\o "1-3" \\h \\z \\u'
    sep = OxmlElement('w:fldChar'); sep.set(qn('w:fldCharType'), 'separate')
    txt = OxmlElement('w:t'); txt.text = '打开 Word 后右键此目录并选择“更新域”，即可生成完整目录。'
    end = OxmlElement('w:fldChar'); end.set(qn('w:fldCharType'), 'end')
    run._r.extend([begin, instr, sep, txt, end])


def add_inline_runs(paragraph, text, size=11, color=DARK, bold=False):
    parts = re.split(r'(`[^`]+`|\*\*[^*]+\*\*)', text)
    for part in parts:
        if not part:
            continue
        mono = part.startswith('`') and part.endswith('`')
        strong = part.startswith('**') and part.endswith('**')
        content = part[1:-1] if mono else part[2:-2] if strong else part
        run = paragraph.add_run(content)
        set_east_asia_font(run, cn='Menlo' if mono else BODY_CN, latin='Menlo' if mono else LATIN, size=10 if mono else size, bold=bold or strong, color=color)


def add_numbered_paragraph(doc, text):
    p = doc.add_paragraph(style='List Number')
    add_inline_runs(p, text)
    return p


def add_bullet_paragraph(doc, text):
    p = doc.add_paragraph(style='List Bullet')
    add_inline_runs(p, text)
    return p


def parse_table(lines, idx):
    rows = []
    while idx < len(lines) and lines[idx].strip().startswith('|'):
        raw = lines[idx].strip().strip('|')
        cells = [c.strip() for c in raw.split('|')]
        if not all(re.fullmatch(r':?-{3,}:?', c.replace(' ', '')) for c in cells):
            rows.append(cells)
        idx += 1
    return rows, idx


def table_weights(rows):
    cols = len(rows[0])
    maxlens = []
    for c in range(cols):
        vals = [len(r[c]) if c < len(r) else 0 for r in rows]
        maxlens.append(max(max(vals), 5))
    if cols == 2:
        return [1.35, 3.65]
    if cols == 3:
        return [1.2, 2.2, 2.8]
    if cols == 4:
        return [0.9, 1.6, 1.6, 2.4]
    return maxlens


def add_table(doc, rows):
    if not rows:
        return
    cols = max(len(r) for r in rows)
    rows = [r + [''] * (cols - len(r)) for r in rows]
    table = doc.add_table(rows=0, cols=cols)
    table.style = 'Table Grid'
    for ri, values in enumerate(rows):
        cells = table.add_row().cells
        for ci, value in enumerate(values):
            cell = cells[ci]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if ri == 0:
                set_cell_shading(cell, TABLE_FILL)
            elif ri % 2 == 0:
                set_cell_shading(cell, ALT_FILL)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            add_inline_runs(p, value, size=9.5, bold=(ri == 0), color=DARK)
        if ri == 0:
            set_repeat_table_header(table.rows[-1])
    widths = column_widths_from_weights(table_weights(rows), total_width_dxa=9120)
    apply_table_geometry(table, widths, table_width_dxa=9120, indent_dxa=120, cell_margins_dxa={'top':100,'bottom':100,'start':120,'end':120})
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def configure_document(doc):
    sec = doc.sections[0]
    sec.page_width = Mm(210)
    sec.page_height = Mm(297)
    sec.top_margin = Mm(25.4)
    sec.bottom_margin = Mm(25.4)
    sec.left_margin = Mm(25.4)
    sec.right_margin = Mm(25.4)
    sec.header_distance = Mm(12.5)
    sec.footer_distance = Mm(12.5)

    styles = doc.styles
    configure_style(styles['Normal'], BODY_CN, LATIN, 11, DARK, False, 0, 6, 1.25)
    styles['Normal'].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    configure_style(styles['Heading 1'], HEADING_CN, LATIN, 16, ACCENT, True, 16, 8, 1.15)
    configure_style(styles['Heading 2'], HEADING_CN, LATIN, 13, ACCENT, True, 12, 6, 1.15)
    configure_style(styles['Heading 3'], HEADING_CN, LATIN, 11.5, RGBColor(47, 84, 111), True, 9, 4, 1.15)
    configure_style(styles['List Bullet'], BODY_CN, LATIN, 11, DARK, False, 0, 4, 1.25)
    styles['List Bullet'].paragraph_format.left_indent = Cm(0.75)
    styles['List Bullet'].paragraph_format.first_line_indent = Cm(-0.35)
    configure_style(styles['List Number'], BODY_CN, LATIN, 11, DARK, False, 0, 4, 1.25)
    styles['List Number'].paragraph_format.left_indent = Cm(0.75)
    styles['List Number'].paragraph_format.first_line_indent = Cm(-0.35)

    for section in doc.sections:
        hp = section.header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_inline_runs(hp, '校园二手商品交易平台毕业论文详细框架', size=9, color=MUTED)
        fp = section.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_field(fp, 'PAGE')

    settings = doc.settings._element
    update = OxmlElement('w:updateFields')
    update.set(qn('w:val'), 'true')
    settings.append(update)


def add_cover(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(95)
    p.paragraph_format.space_after = Pt(16)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('毕业论文详细框架')
    set_east_asia_font(r, cn=HEADING_CN, size=18, bold=True, color=ACCENT)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run('基于 FastAPI 与 Vue 的校园二手商品交易平台设计与实现')
    set_east_asia_font(r, cn=HEADING_CN, size=25, bold=True, color=DARK)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(60)
    r = p.add_run('参考样稿研究 · 三级目录 · 逐节写作任务 · 图表与代码证据映射')
    set_east_asia_font(r, size=12, color=MUTED)

    rows = [
        ['项目名称', '校园集市'],
        ['系统类型', 'Python + Vue 校园二手商品交易平台'],
        ['前端技术', 'Vue 3、Vite、Vue Router、Pinia、Axios、Element Plus、ECharts'],
        ['后端技术', 'FastAPI、SQLAlchemy、SQLite、PBKDF2、HMAC 令牌'],
        ['项目规模', 'C 端 + 管理后台；14 个主要数据实体；49 个 API 接口'],
        ['生成日期', '2026 年 8 月 12 日'],
    ]
    add_table(doc, rows)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(28)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('用途：论文开题、目录确认、正文写作与系统证据准备')
    set_east_asia_font(r, size=10.5, color=MUTED)
    doc.add_page_break()

    p = doc.add_paragraph('目录', style='Heading 1')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    toc = doc.add_paragraph()
    add_toc(toc)
    doc.add_page_break()


def build():
    doc = Document()
    configure_document(doc)
    add_cover(doc)
    lines = SOURCE.read_text(encoding='utf-8').splitlines()
    idx = 0
    first_title_skipped = False
    while idx < len(lines):
        raw = lines[idx].rstrip()
        stripped = raw.strip()
        if not stripped or stripped == '---':
            idx += 1
            continue
        if stripped.startswith('|'):
            rows, idx = parse_table(lines, idx)
            add_table(doc, rows)
            continue
        m = re.match(r'^(#{1,6})\s+(.*)$', stripped)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            if not first_title_skipped:
                first_title_skipped = True
                idx += 1
                continue
            # Markdown is one level deeper because the file has a document title.
            word_level = max(1, min(3, level - 1))
            p = doc.add_paragraph(style=f'Heading {word_level}')
            add_inline_runs(p, title, size={1:16,2:13,3:11.5}[word_level], color=ACCENT if word_level < 3 else RGBColor(47,84,111), bold=True)
            idx += 1
            continue
        if stripped.startswith('- '):
            add_bullet_paragraph(doc, stripped[2:].strip())
            idx += 1
            continue
        if re.match(r'^\d+\.\s+', stripped):
            add_numbered_paragraph(doc, re.sub(r'^\d+\.\s+', '', stripped))
            idx += 1
            continue
        p = doc.add_paragraph()
        p.paragraph_format.keep_together = False
        add_inline_runs(p, stripped)
        idx += 1

    doc.core_properties.title = '基于FastAPI与Vue的校园二手交易平台毕业论文详细框架'
    doc.core_properties.subject = '毕业论文结构与逐节写作说明'
    doc.core_properties.author = 'Codex'
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == '__main__':
    build()
