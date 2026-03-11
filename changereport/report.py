"""PDF report assembly using ReportLab."""

import pandas as pd
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether, HRFlowable,
)

from changereport.constants import (
    PDF_PRIMARY_COLOR, PDF_HEADER_BG, PDF_HEADER_TEXT,
    PDF_ALT_ROW, PDF_GRID_COLOR,
)
from changereport.jargon import translate_change

# Accent colors for KPI stat cards on title page
_CARD_COLORS = ["#1565C0", "#B71C1C", "#1B5E20", "#E65100"]
# Teal for category sub-headers in change table
_TEAL_SECTION = "#00695C"
# Blue-grey for subsection banners
_SLATE = "#37474F"
# Light indigo for description rows
_ALT_ROW_INDIGO = "#E8EAF6"


def generate_report(df: pd.DataFrame, output_path: str, charts: dict,
                    analysis: dict, title: str = "ITIL 4 Change Enablement Report"):
    """Generate the full PDF report."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.70 * inch,
    )

    styles = _build_styles()
    story = []

    # 1. Title Page
    story.extend(_build_title_page(df, analysis, styles, title))
    story.append(PageBreak())

    # 2. Executive Summary
    story.extend(_build_executive_summary(df, analysis, styles))
    story.append(PageBreak())

    # 3. Charts Section
    story.extend(_build_charts_section(charts, styles))
    story.append(PageBreak())

    # 4. Change Summary Table (with inline plain-English descriptions)
    story.extend(_build_change_table(df, styles))
    story.append(PageBreak())

    # 5. Implementer Workload Summary
    story.extend(_build_implementer_section(analysis, charts, styles))

    doc.build(
        story,
        onFirstPage=_make_header_footer(title),
        onLaterPages=_make_header_footer(title),
    )


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

def _build_styles():
    """Create custom paragraph styles."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontSize=24,
        textColor=HexColor("#ffffff"),
        fontName="Helvetica-Bold",
        spaceAfter=6,
        spaceBefore=0,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        "BannerSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=HexColor("#90CAF9"),
        alignment=TA_LEFT,
        spaceAfter=0,
        spaceBefore=0,
    ))

    styles.add(ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=HexColor("#777777"),
        alignment=TA_LEFT,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontSize=12,
        textColor=HexColor("#ffffff"),
        fontName="Helvetica-Bold",
        spaceAfter=0,
        spaceBefore=0,
    ))

    styles.add(ParagraphStyle(
        "SubSection",
        parent=styles["Normal"],
        fontSize=10,
        textColor=HexColor("#ffffff"),
        fontName="Helvetica-Bold",
        spaceAfter=0,
        spaceBefore=0,
    ))

    styles.add(ParagraphStyle(
        "StatLabel",
        parent=styles["Normal"],
        fontSize=8,
        textColor=HexColor("#ffffff"),
        alignment=TA_CENTER,
        spaceAfter=0,
        spaceBefore=0,
    ))

    styles.add(ParagraphStyle(
        "StatValue",
        parent=styles["Normal"],
        fontSize=30,
        textColor=HexColor("#ffffff"),
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=0,
        spaceBefore=0,
    ))

    styles.add(ParagraphStyle(
        "KPIValue",
        parent=styles["Normal"],
        fontSize=22,
        textColor=HexColor(PDF_PRIMARY_COLOR),
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=0,
        spaceBefore=0,
    ))

    styles.add(ParagraphStyle(
        "KPILabel",
        parent=styles["Normal"],
        fontSize=8,
        textColor=HexColor("#555555"),
        alignment=TA_CENTER,
        spaceAfter=0,
        spaceBefore=0,
    ))

    styles.add(ParagraphStyle(
        "BodyText2",
        parent=styles["Normal"],
        fontSize=9,
        leading=13.5,
        textColor=HexColor("#333333"),
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        "BulletText",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=HexColor("#333333"),
        leftIndent=12,
        spaceAfter=3,
    ))

    styles.add(ParagraphStyle(
        "LaymanText",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=11,
        spaceAfter=4,
        leftIndent=8,
        textColor=HexColor("#37474F"),
    ))

    styles.add(ParagraphStyle(
        "ChartCaption",
        parent=styles["Normal"],
        fontSize=8,
        textColor=HexColor("#888888"),
        alignment=TA_CENTER,
        spaceAfter=12,
    ))

    styles.add(ParagraphStyle(
        "CellText",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
        textColor=HexColor("#212121"),
    ))

    return styles


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------

def _section_banner(text, styles, page_width, color=None):
    """Full-width colored section header banner."""
    color = color or PDF_PRIMARY_COLOR
    data = [[Paragraph(text, styles["SectionHeader"])]]
    t = Table(data, colWidths=[page_width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor(color)),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


def _subsection_banner(text, styles, page_width, color=None):
    """Lighter subsection header banner."""
    color = color or _SLATE
    data = [[Paragraph(text, styles["SubSection"])]]
    t = Table(data, colWidths=[page_width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor(color)),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


# ---------------------------------------------------------------------------
# Page builders
# ---------------------------------------------------------------------------

def _build_title_page(df, analysis, styles, title):
    """Title page: navy banner + 4 KPI cards."""
    elements = []
    page_width = A4[0] - 1.2 * inch

    elements.append(Spacer(1, 0.55 * inch))

    # Full-width dark navy title banner
    date_from, date_to = analysis["date_range"]
    banner_rows = [[Paragraph(title, styles["ReportTitle"])]]
    if date_from and date_to:
        period = (f"Reporting Period:  "
                  f"{date_from.strftime('%d %B %Y')}  —  {date_to.strftime('%d %B %Y')}")
        banner_rows.append([Paragraph(period, styles["BannerSubtitle"])])

    banner = Table(banner_rows, colWidths=[page_width])
    banner_style = [
        ("BACKGROUND", (0, 0), (-1, -1), HexColor(PDF_PRIMARY_COLOR)),
        ("LEFTPADDING", (0, 0), (-1, -1), 22),
        ("RIGHTPADDING", (0, 0), (-1, -1), 22),
        ("TOPPADDING", (0, 0), (-1, 0), 28),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 24),
    ]
    if len(banner_rows) > 1:
        banner_style += [
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 1), (-1, 1), 0),
        ]
    banner.setStyle(TableStyle(banner_style))
    elements.append(banner)

    elements.append(Spacer(1, 0.25 * inch))

    # 4 coloured KPI cards (1 row × 4 columns, value above label)
    total = analysis["total_changes"]
    high_impact = len(analysis["high_impact"])
    stats = [
        (str(total),                            "TOTAL CHANGES",       _CARD_COLORS[0]),
        (str(high_impact),                      "HIGH-IMPACT CHANGES", _CARD_COLORS[1]),
        (str(len(analysis["by_category"])),     "CATEGORIES COVERED",  _CARD_COLORS[2]),
        (str(len(analysis["implementer_workload"])), "CHANGE IMPLEMENTERS", _CARD_COLORS[3]),
    ]

    card_w = page_width / 4
    val_row = [Paragraph(v, styles["StatValue"]) for v, _, _ in stats]
    lbl_row = [Paragraph(l, styles["StatLabel"]) for _, l, _ in stats]

    card_style = [
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, 0),  20),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  6),
        ("TOPPADDING",    (0, 1), (-1, 1),  4),
        ("BOTTOMPADDING", (0, 1), (-1, 1),  20),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
    ]
    for i, (*_, color) in enumerate(stats):
        card_style.append(("BACKGROUND", (i, 0), (i, 1), HexColor(color)))

    card_table = Table([val_row, lbl_row], colWidths=[card_w] * 4)
    card_table.setStyle(TableStyle(card_style))
    elements.append(card_table)

    elements.append(Spacer(1, 1.1 * inch))
    gen_date = datetime.now().strftime("%d %B %Y at %H:%M")
    elements.append(Paragraph(f"Report generated on {gen_date}", styles["ReportSubtitle"]))

    return elements


def _build_executive_summary(df, analysis, styles):
    """Executive summary: narrative + mini KPI row + three subsections."""
    elements = []
    page_width = A4[0] - 1.2 * inch

    elements.append(_section_banner("Executive Summary", styles, page_width))
    elements.append(Spacer(1, 0.15 * inch))

    total = analysis["total_changes"]
    date_from, date_to = analysis["date_range"]
    date_str = ""
    if date_from and date_to:
        date_str = (f" between {date_from.strftime('%d %b %Y')}"
                    f" and {date_to.strftime('%d %b %Y')}")

    overview = (
        f"A total of <b>{total} change requests</b> were processed{date_str}. "
        f"The busiest category was <b>{analysis['busiest_category']}</b>. "
        f"The busiest day was <b>{analysis['busiest_day']}</b>."
    )
    elements.append(Paragraph(overview, styles["BodyText2"]))
    elements.append(Spacer(1, 0.18 * inch))

    # Mini KPI row (light indigo card strip)
    high_impact = len(analysis["high_impact"])
    kpi_stats = [
        (str(total),                                "Total Changes"),
        (str(high_impact),                          "High-Impact"),
        (str(len(analysis["by_category"])),         "Categories"),
        (str(len(analysis["implementer_workload"])), "Implementers"),
    ]
    kpi_w = page_width / 4
    kpi_vals = [Paragraph(v, styles["KPIValue"]) for v, _ in kpi_stats]
    kpi_lbls = [Paragraph(l, styles["KPILabel"]) for _, l in kpi_stats]

    kpi_table = Table([kpi_vals, kpi_lbls], colWidths=[kpi_w] * 4)
    kpi_table.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, 0),  12),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  4),
        ("TOPPADDING",    (0, 1), (-1, 1),  2),
        ("BOTTOMPADDING", (0, 1), (-1, 1),  12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1),
         [HexColor("#EEF2FF"), HexColor("#EEF2FF")]),
        ("BOX",       (0, 0), (-1, -1), 0.5,  HexColor("#C5CAE9")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5,  HexColor("#C5CAE9")),
        ("LINEABOVE", (0, 0), (-1, 0),  3,    HexColor(PDF_PRIMARY_COLOR)),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 0.2 * inch))

    # Change Type Breakdown
    elements.append(_subsection_banner("Change Type Breakdown", styles, page_width))
    elements.append(Spacer(1, 0.08 * inch))
    by_type = analysis["by_type"]
    for ctype, count in by_type.items():
        pct = count / total * 100 if total > 0 else 0
        elements.append(Paragraph(
            f"\u2022 <b>{ctype}</b>: {count} ({pct:.0f}%)",
            styles["BulletText"]
        ))
    elements.append(Spacer(1, 0.15 * inch))

    # Impact Summary
    elements.append(_subsection_banner("Impact Summary", styles, page_width))
    elements.append(Spacer(1, 0.08 * inch))
    elements.append(Paragraph(
        f"Out of {total} changes, <b>{high_impact}</b> had potential service "
        f"impact (site down, user disconnections, or service degradation). "
        f"The remaining <b>{total - high_impact}</b> changes were classified as "
        f"having no customer impact.",
        styles["BodyText2"]
    ))
    elements.append(Spacer(1, 0.15 * inch))

    # Changes by Category
    elements.append(_subsection_banner("Changes by Category", styles, page_width))
    elements.append(Spacer(1, 0.08 * inch))
    by_cat = analysis["by_category"]
    for cat, count in by_cat.items():
        pct = count / total * 100 if total > 0 else 0
        elements.append(Paragraph(
            f"\u2022 <b>{cat}</b>: {count} ({pct:.0f}%)",
            styles["BulletText"]
        ))

    return elements


def _build_charts_section(charts, styles):
    """Visual analysis: charts with titled subsection banners."""
    elements = []
    page_width = A4[0] - 1.2 * inch

    elements.append(_section_banner("Visual Analysis", styles, page_width))
    elements.append(Spacer(1, 0.15 * inch))

    chart_info = [
        ("by_category", "Changes by Network Category",
         "Distribution of changes across different network and system categories."),
        ("by_impact", "Impact Distribution",
         "Expected customer impact level for each change."),
        ("timeline", "Change Activity Timeline",
         "Daily distribution of changes showing activity patterns over the reporting period."),
        ("implementer", "Top Change Implementers",
         "Workload distribution across change implementers."),
    ]

    for key, title_text, caption in chart_info:
        if key not in charts:
            continue
        elements.append(_subsection_banner(title_text, styles, page_width))
        elements.append(Spacer(1, 0.08 * inch))
        buf = charts[key]
        buf.seek(0)
        img = Image(buf, width=page_width, height=page_width * 0.45)
        elements.append(img)
        elements.append(Paragraph(caption, styles["ChartCaption"]))
        elements.append(Spacer(1, 0.1 * inch))

    return elements


def _build_change_table(df, styles):
    """Change summary table: category groups with teal sub-banners."""
    elements = []
    page_width = A4[0] - 1.2 * inch

    elements.append(_section_banner("Change Summary", styles, page_width))
    elements.append(Spacer(1, 0.06 * inch))
    elements.append(Paragraph(
        "All changes processed during the reporting period, grouped by category "
        "and ordered by date. Each change includes a plain-English description.",
        styles["BodyText2"]
    ))
    elements.append(Spacer(1, 0.1 * inch))

    categories = sorted(
        [c for c in df["category"].unique() if pd.notna(c) and str(c).strip()]
    )

    col_widths = [
        page_width * 0.07,   # ID
        page_width * 0.28,   # Subject
        page_width * 0.10,   # Type
        page_width * 0.14,   # Start
        page_width * 0.13,   # Impact
        page_width * 0.15,   # Implementer
        page_width * 0.13,   # Duration
    ]

    for category in categories:
        cat_df = df[df["category"] == category].copy()
        cat_df = cat_df.sort_values("start_datetime", ascending=True, na_position="last")

        # Teal category sub-banner
        elements.append(_subsection_banner(
            f"{category}  \u2014  {len(cat_df)} changes",
            styles, page_width, color=_TEAL_SECTION
        ))
        elements.append(Spacer(1, 0.04 * inch))

        # Table header row
        headers = ["ID", "Subject", "Type", "Start", "Impact", "Implementer", "Duration"]
        header_row = [
            Paragraph(f"<b>{h}</b>", ParagraphStyle(
                f"TH_{h}", parent=styles["CellText"],
                textColor=HexColor("#ffffff"), fontName="Helvetica-Bold",
            ))
            for h in headers
        ]

        table_data = [header_row]
        style_commands = [
            ("BACKGROUND", (0, 0), (-1, 0), HexColor(PDF_HEADER_BG)),
            ("TEXTCOLOR",  (0, 0), (-1, 0), HexColor(PDF_HEADER_TEXT)),
            ("FONTSIZE",   (0, 0), (-1, -1), 7),
            ("GRID",       (0, 0), (-1, -1), 0.4, HexColor(PDF_GRID_COLOR)),
            ("VALIGN",     (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 5),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ]

        for change_idx, (_, row) in enumerate(cat_df.iterrows()):
            subject = str(row.get("subject", ""))
            if len(subject) > 80:
                subject = subject[:77] + "..."

            start_str = ""
            if pd.notna(row.get("start_datetime")):
                start_str = row["start_datetime"].strftime("%d %b %Y %H:%M")

            dur_str = ""
            duration = row.get("duration_hours")
            if pd.notna(duration):
                try:
                    dur = float(duration)
                    dur_str = f"{int(dur * 60)} min" if dur < 1 else f"{dur:.1f} hrs"
                except (ValueError, TypeError):
                    pass

            # Data row
            data_row_idx = len(table_data)
            table_data.append([
                Paragraph(str(row.get("id", "")), styles["CellText"]),
                Paragraph(f"<b>{subject}</b>", styles["CellText"]),
                Paragraph(str(row.get("type_of_change", "")), styles["CellText"]),
                Paragraph(start_str, styles["CellText"]),
                Paragraph(str(row.get("impact_description", "")), styles["CellText"]),
                Paragraph(str(row.get("customer_name", "")), styles["CellText"]),
                Paragraph(dur_str, styles["CellText"]),
            ])

            # Description row spanning all columns
            desc_row_idx = len(table_data)
            translation = translate_change(row)
            table_data.append([
                Paragraph(f"<i>{translation}</i>", styles["LaymanText"]),
                "", "", "", "", "", "",
            ])

            style_commands.append(("SPAN", (0, desc_row_idx), (-1, desc_row_idx)))

            bg = HexColor("#ffffff") if change_idx % 2 == 0 else HexColor(PDF_ALT_ROW)
            style_commands.append(("BACKGROUND", (0, data_row_idx), (-1, data_row_idx), bg))
            style_commands.append(
                ("BACKGROUND", (0, desc_row_idx), (-1, desc_row_idx), HexColor(_ALT_ROW_INDIGO))
            )
            style_commands.append(
                ("LINEBEFORE", (0, desc_row_idx), (0, desc_row_idx), 3,
                 HexColor(PDF_PRIMARY_COLOR))
            )
            style_commands.append(
                ("LINEBELOW", (0, desc_row_idx), (-1, desc_row_idx), 0.75,
                 HexColor("#cccccc"))
            )

        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle(style_commands))
        elements.append(t)
        elements.append(Spacer(1, 0.22 * inch))

    return elements


def _build_implementer_section(analysis, charts, styles):
    """Implementer workload table."""
    elements = []
    page_width = A4[0] - 1.2 * inch

    elements.append(_section_banner("Implementer Workload Summary", styles, page_width))
    elements.append(Spacer(1, 0.1 * inch))

    impl = analysis["implementer_workload"]
    if impl.empty:
        elements.append(Paragraph("No implementer data available.", styles["BodyText2"]))
        return elements

    elements.append(Paragraph(
        f"A total of <b>{len(impl)} individuals</b> implemented changes during "
        f"this period. Below is a summary of their workload.",
        styles["BodyText2"]
    ))
    elements.append(Spacer(1, 0.1 * inch))

    headers = ["Implementer", "Changes", "Total Hours", "Categories"]
    header_row = [
        Paragraph(f"<b>{h}</b>", ParagraphStyle(
            f"TH3_{h}", parent=styles["CellText"],
            textColor=HexColor("#ffffff"), fontName="Helvetica-Bold",
        ))
        for h in headers
    ]

    col_widths = [
        page_width * 0.25,
        page_width * 0.10,
        page_width * 0.12,
        page_width * 0.53,
    ]

    table_data = [header_row]
    for name, row in impl.iterrows():
        hours_str = f"{row['total_hours']:.1f}" if pd.notna(row['total_hours']) else "N/A"
        table_data.append([
            Paragraph(str(name), styles["CellText"]),
            Paragraph(str(row["change_count"]), styles["CellText"]),
            Paragraph(hours_str, styles["CellText"]),
            Paragraph(str(row["categories"]), styles["CellText"]),
        ])

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), HexColor(PDF_HEADER_BG)),
        ("TEXTCOLOR",     (0, 0), (-1, 0), HexColor(PDF_HEADER_TEXT)),
        ("FONTSIZE",      (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [HexColor("#ffffff"), HexColor(PDF_ALT_ROW)]),
        ("GRID",          (0, 0), (-1, -1), 0.4, HexColor(PDF_GRID_COLOR)),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
    ]))
    elements.append(t)
    return elements


# ---------------------------------------------------------------------------
# Header / footer
# ---------------------------------------------------------------------------

def _make_header_footer(title):
    """Return a canvas callback that draws a solid header bar and footer line."""
    def _draw(canvas, doc):
        canvas.saveState()
        width, height = A4
        margin = 0.6 * inch

        # Solid navy header bar
        bar_h = 0.36 * inch
        canvas.setFillColor(HexColor(PDF_PRIMARY_COLOR))
        canvas.rect(0, height - bar_h, width, bar_h, fill=1, stroke=0)

        # Header text (white): title left, page number right
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(HexColor("#ffffff"))
        text_y = height - 0.235 * inch
        canvas.drawString(margin, text_y, title)
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(width - margin, text_y, f"Page {doc.page}")

        # Footer line
        canvas.setStrokeColor(HexColor("#dddddd"))
        canvas.setLineWidth(0.75)
        canvas.line(margin, 0.52 * inch, width - margin, 0.52 * inch)

        # Footer text
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(HexColor("#999999"))
        canvas.drawString(margin, 0.36 * inch,
                          f"Generated {datetime.now().strftime('%d %b %Y')}")
        canvas.drawRightString(width - margin, 0.36 * inch,
                               "ITIL 4 Change Enablement — Confidential")

        canvas.restoreState()

    return _draw
