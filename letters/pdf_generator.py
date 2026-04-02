"""
PDF generation for Boenix SMS.
Produces: Report Cards, Fee Statements, Parent Notification Letters.
"""
import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Boenix brand colours ─────────────────────────────────────────────────────
NAVY   = colors.HexColor('#1B3A6B')
GOLD   = colors.HexColor('#C9A227')
LIGHT  = colors.HexColor('#EEF2FB')
WHITE  = colors.white
BLACK  = colors.black
GREEN  = colors.HexColor('#198754')
RED    = colors.HexColor('#DC3545')
GREY   = colors.HexColor('#6C757D')


def _base_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('SchoolName',  fontName='Helvetica-Bold',  fontSize=14, textColor=NAVY,  alignment=TA_CENTER, spaceAfter=2))
    styles.add(ParagraphStyle('SubTitle',    fontName='Helvetica',       fontSize=9,  textColor=GREY,  alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle('DocTitle',    fontName='Helvetica-Bold',  fontSize=11, textColor=WHITE, alignment=TA_CENTER))
    styles.add(ParagraphStyle('BodySmall',   fontName='Helvetica',       fontSize=8,  textColor=BLACK, leading=12))
    styles.add(ParagraphStyle('BodyNormal',  fontName='Helvetica',       fontSize=9,  textColor=BLACK, leading=13))
    styles.add(ParagraphStyle('Label',       fontName='Helvetica-Bold',  fontSize=8,  textColor=NAVY))
    styles.add(ParagraphStyle('Value',       fontName='Helvetica',       fontSize=8,  textColor=BLACK))
    styles.add(ParagraphStyle('SectionHdr',  fontName='Helvetica-Bold',  fontSize=9,  textColor=WHITE))
    styles.add(ParagraphStyle('Footer',      fontName='Helvetica-Oblique',fontSize=7, textColor=GREY,  alignment=TA_CENTER))
    return styles


def _school_header(styles, school_name, school_motto):
    """Returns a list of flowables for the school letterhead."""
    return [
        Paragraph(school_name.upper(), styles['SchoolName']),
        Paragraph(school_motto, styles['SubTitle']),
        HRFlowable(width='100%', thickness=2, color=GOLD, spaceAfter=4),
    ]


def _section_banner(title, styles):
    data = [[Paragraph(title, styles['SectionHdr'])]]
    t = Table(data, colWidths=['100%'])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
    ]))
    return t


def _grade_colour(grade):
    high = {'A', 'A-', 'B+', 'B'}
    mid  = {'B-', 'C+', 'C'}
    if grade in high:
        return GREEN
    if grade in mid:
        return colors.HexColor('#FD7E14')
    return RED


# ─────────────────────────────────────────────────────────────────────────────
#  REPORT CARD
# ─────────────────────────────────────────────────────────────────────────────

def generate_report_card(student, exam, marks_data, position, total_students,
                         school_name, school_motto, class_teacher_name='',
                         principal_remarks='', teacher_remarks=''):
    """
    marks_data: list of dicts:
      [{'subject': <Subject>, 'score': 72.5, 'grade': 'B+', 'points': 10}, ...]
    Returns bytes (PDF).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = _base_styles()
    story  = []

    # ── Header ──────────────────────────────────────────────────────────────
    story += _school_header(styles, school_name, school_motto)

    # ── Doc title banner ────────────────────────────────────────────────────
    story.append(_section_banner(f'STUDENT REPORT CARD — {exam.name.upper()}', styles))
    story.append(Spacer(1, 0.3*cm))

    # ── Student info block ──────────────────────────────────────────────────
    info_data = [
        [Paragraph('Name:', styles['Label']),
         Paragraph(student.full_name, styles['Value']),
         Paragraph('Adm. No.:', styles['Label']),
         Paragraph(student.admission_number, styles['Value'])],
        [Paragraph('Class:', styles['Label']),
         Paragraph(str(student.class_section), styles['Value']),
         Paragraph('Term / Year:', styles['Label']),
         Paragraph(f'Term {exam.term}, {exam.year}', styles['Value'])],
        [Paragraph('Position:', styles['Label']),
         Paragraph(f'{position} out of {total_students}', styles['Value']),
         Paragraph('Boarding:', styles['Label']),
         Paragraph(student.get_boarding_type_display(), styles['Value'])],
    ]
    info_table = Table(info_data, colWidths=[2.5*cm, 6*cm, 2.5*cm, 6*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
        ('GRID',       (0, 0), (-1, -1), 0.3, colors.HexColor('#D5DCE8')),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.4*cm))

    # ── Marks table ─────────────────────────────────────────────────────────
    story.append(_section_banner('ACADEMIC PERFORMANCE', styles))
    story.append(Spacer(1, 0.2*cm))

    header = [
        Paragraph('Subject',  styles['SectionHdr']),
        Paragraph('Score',    styles['SectionHdr']),
        Paragraph('Grade',    styles['SectionHdr']),
        Paragraph('Points',   styles['SectionHdr']),
        Paragraph('Remarks',  styles['SectionHdr']),
    ]
    marks_rows = [header]

    total_pts  = 0
    scored_n   = 0
    for item in marks_data:
        score  = item.get('score')
        grade  = item.get('grade', '—')
        points = item.get('points', 0)
        if score is not None and grade != 'ABS':
            total_pts += points
            scored_n  += 1

        score_str = 'ABSENT' if grade == 'ABS' else (f'{float(score):.1f}' if score is not None else '—')
        remark = _remark_for_grade(grade)
        g_color = _grade_colour(grade)

        row = [
            Paragraph(item['subject'].name, styles['BodySmall']),
            Paragraph(score_str, ParagraphStyle('sc', fontName='Helvetica', fontSize=8,
                                                 alignment=TA_CENTER)),
            Paragraph(grade, ParagraphStyle('gr', fontName='Helvetica-Bold', fontSize=8,
                                             textColor=g_color, alignment=TA_CENTER)),
            Paragraph(str(points) if grade != 'ABS' else '—',
                      ParagraphStyle('pt', fontName='Helvetica', fontSize=8, alignment=TA_CENTER)),
            Paragraph(remark, styles['BodySmall']),
        ]
        marks_rows.append(row)

    mean_pts   = round(total_pts / scored_n, 3) if scored_n else 0
    from exams.models import get_kcse_grade
    mean_grade, _ = get_kcse_grade(mean_pts * (100 / 12))

    # Totals row
    marks_rows.append([
        Paragraph('MEAN GRADE', ParagraphStyle('tot', fontName='Helvetica-Bold', fontSize=8, textColor=NAVY)),
        Paragraph('', styles['BodySmall']),
        Paragraph(mean_grade, ParagraphStyle('mg', fontName='Helvetica-Bold', fontSize=10,
                                              textColor=_grade_colour(mean_grade), alignment=TA_CENTER)),
        Paragraph(str(mean_pts), ParagraphStyle('mp', fontName='Helvetica-Bold', fontSize=8,
                                                 textColor=NAVY, alignment=TA_CENTER)),
        Paragraph(f'Position: {position}/{total_students}',
                  ParagraphStyle('pos', fontName='Helvetica-Bold', fontSize=8, textColor=NAVY)),
    ])

    col_w = [5.5*cm, 2*cm, 2*cm, 2*cm, 6*cm]
    mt = Table(marks_rows, colWidths=col_w, repeatRows=1)
    mt.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  NAVY),
        ('BACKGROUND',    (0, -1), (-1, -1), LIGHT),
        ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor('#D5DCE8')),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [WHITE, LIGHT]),
        ('LINEBELOW',     (0, -2), (-1, -2), 1, GOLD),
    ]))
    story.append(mt)
    story.append(Spacer(1, 0.5*cm))

    # ── Remarks ─────────────────────────────────────────────────────────────
    if teacher_remarks or principal_remarks:
        story.append(_section_banner('REMARKS', styles))
        story.append(Spacer(1, 0.2*cm))
        rem_data = []
        if teacher_remarks:
            rem_data.append([
                Paragraph('Class Teacher:', styles['Label']),
                Paragraph(teacher_remarks, styles['BodyNormal']),
            ])
        if principal_remarks:
            rem_data.append([
                Paragraph('Principal:', styles['Label']),
                Paragraph(principal_remarks, styles['BodyNormal']),
            ])
        rt = Table(rem_data, colWidths=[3*cm, 14.5*cm])
        rt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
            ('GRID',       (0, 0), (-1, -1), 0.3, colors.HexColor('#D5DCE8')),
            ('TOPPADDING',    (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
            ('VALIGN',     (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(rt)
        story.append(Spacer(1, 0.4*cm))

    # ── Signatures ──────────────────────────────────────────────────────────
    sig_data = [[
        Paragraph('Class Teacher: ________________________', styles['BodySmall']),
        Paragraph(f'Date: {date.today().strftime("%d/%m/%Y")}', styles['BodySmall']),
        Paragraph('Principal: ________________________', styles['BodySmall']),
    ]]
    st = Table(sig_data, colWidths=[6*cm, 4*cm, 7.5*cm])
    story.append(st)
    story.append(Spacer(1, 0.3*cm))

    # ── Footer ──────────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=1, color=GOLD))
    story.append(Paragraph(
        f'{school_name} | Generated: {date.today().strftime("%d %B %Y")} | CONFIDENTIAL',
        styles['Footer']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
#  FEE STATEMENT
# ─────────────────────────────────────────────────────────────────────────────

def generate_fee_statement(student, payments, balances, school_name, school_motto):
    """Returns bytes (PDF fee statement)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = _base_styles()
    story  = []

    story += _school_header(styles, school_name, school_motto)
    story.append(_section_banner('FEE STATEMENT', styles))
    story.append(Spacer(1, 0.3*cm))

    # Student info
    info_data = [
        [Paragraph('Student:', styles['Label']),
         Paragraph(student.full_name, styles['Value']),
         Paragraph('Adm. No.:', styles['Label']),
         Paragraph(student.admission_number, styles['Value'])],
        [Paragraph('Class:', styles['Label']),
         Paragraph(str(student.class_section), styles['Value']),
         Paragraph('Statement Date:', styles['Label']),
         Paragraph(date.today().strftime('%d %B %Y'), styles['Value'])],
    ]
    it = Table(info_data, colWidths=[2.5*cm, 6*cm, 3*cm, 6*cm])
    it.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
        ('GRID',       (0, 0), (-1, -1), 0.3, colors.HexColor('#D5DCE8')),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
    ]))
    story.append(it)
    story.append(Spacer(1, 0.5*cm))

    # Balance summary per term
    story.append(_section_banner('BALANCE SUMMARY', styles))
    story.append(Spacer(1, 0.2*cm))

    bal_header = [
        Paragraph('Term', styles['SectionHdr']),
        Paragraph('Year', styles['SectionHdr']),
        Paragraph('Expected (KSh)', styles['SectionHdr']),
        Paragraph('Paid (KSh)', styles['SectionHdr']),
        Paragraph('Balance (KSh)', styles['SectionHdr']),
        Paragraph('Status', styles['SectionHdr']),
    ]
    bal_rows = [bal_header]
    for b in balances:
        bal_color = GREEN if b.is_cleared else RED
        bal_rows.append([
            Paragraph(f'Term {b.term}', styles['BodySmall']),
            Paragraph(str(b.year), styles['BodySmall']),
            Paragraph(f'{b.expected:,.0f}', ParagraphStyle('r', fontName='Helvetica', fontSize=8, alignment=TA_RIGHT)),
            Paragraph(f'{b.paid:,.0f}', ParagraphStyle('r', fontName='Helvetica', fontSize=8, alignment=TA_RIGHT, textColor=GREEN)),
            Paragraph(f'{b.balance:,.0f}', ParagraphStyle('r', fontName='Helvetica-Bold', fontSize=8,
                                                            alignment=TA_RIGHT, textColor=bal_color)),
            Paragraph('CLEARED' if b.is_cleared else 'OWING',
                      ParagraphStyle('s', fontName='Helvetica-Bold', fontSize=7, textColor=bal_color, alignment=TA_CENTER)),
        ])

    bt = Table(bal_rows, colWidths=[2*cm, 2*cm, 3.5*cm, 3.5*cm, 3.5*cm, 3*cm], repeatRows=1)
    bt.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  NAVY),
        ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor('#D5DCE8')),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT]),
    ]))
    story.append(bt)
    story.append(Spacer(1, 0.5*cm))

    # Payment history
    story.append(_section_banner('PAYMENT HISTORY', styles))
    story.append(Spacer(1, 0.2*cm))

    pay_header = [
        Paragraph('Date', styles['SectionHdr']),
        Paragraph('Term/Year', styles['SectionHdr']),
        Paragraph('Amount (KSh)', styles['SectionHdr']),
        Paragraph('Method', styles['SectionHdr']),
        Paragraph('Reference', styles['SectionHdr']),
    ]
    pay_rows = [pay_header]
    for p in payments:
        pay_rows.append([
            Paragraph(p.date_paid.strftime('%d/%m/%Y'), styles['BodySmall']),
            Paragraph(f'T{p.term}/{p.year}', styles['BodySmall']),
            Paragraph(f'{p.amount:,.0f}', ParagraphStyle('pr', fontName='Helvetica-Bold', fontSize=8,
                                                          alignment=TA_RIGHT, textColor=GREEN)),
            Paragraph(p.get_method_display(), styles['BodySmall']),
            Paragraph(p.reference or '—', styles['BodySmall']),
        ])

    pt = Table(pay_rows, colWidths=[2.5*cm, 2.5*cm, 3.5*cm, 3*cm, 6*cm], repeatRows=1)
    pt.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  NAVY),
        ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor('#D5DCE8')),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT]),
    ]))
    story.append(pt)
    story.append(Spacer(1, 0.5*cm))

    story.append(HRFlowable(width='100%', thickness=1, color=GOLD))
    story.append(Paragraph(
        f'{school_name} | Fee Statement generated: {date.today().strftime("%d %B %Y")}',
        styles['Footer']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def _remark_for_grade(grade):
    remarks = {
        'A':  'Excellent performance. Keep it up!',
        'A-': 'Very good. Aim higher.',
        'B+': 'Good work. Push for A.',
        'B':  'Good. Work harder.',
        'B-': 'Above average. More effort needed.',
        'C+': 'Average. Significant improvement required.',
        'C':  'Fair. Must work much harder.',
        'C-': 'Below average. Urgent improvement needed.',
        'D+': 'Poor. Seek teacher support immediately.',
        'D':  'Very poor. Remediation required.',
        'D-': 'Unsatisfactory. Immediate intervention needed.',
        'E':  'Fail. Comprehensive support required.',
        'ABS':'Absent during examination.',
    }
    return remarks.get(grade, '—')
