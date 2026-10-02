from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import mm
from xml.sax.saxutils import escape
import re


def create_pdf_report(
    filename,
    machine_type,
    machine_id,
    manufacturer,
    final_report
):

    # =================================================
    # PDF DOCUMENT
    # =================================================

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=55,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # =================================================
    # CUSTOM STYLES
    # =================================================

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#17365D"),
        spaceBefore=12,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#222222"),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-8,
        spaceAfter=5
    )

    numbered_style = ParagraphStyle(
        "Numbered",
        parent=body_style,
        leftIndent=16,
        firstLineIndent=-12,
        spaceAfter=6
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#666666")
    )

    # =================================================
    # STORY
    # =================================================

    story = []

    # =================================================
    # HEADER / TITLE
    # =================================================

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "MechCare AI",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Machine Maintenance & Troubleshooting Report",
            subtitle_style
        )
    )

    # =================================================
    # MACHINE INFORMATION
    # =================================================

    story.append(
        Paragraph(
            "1. Machine Information",
            section_style
        )
    )

    machine_data = [
        [
            Paragraph("<b>Machine Type</b>", body_style),
            Paragraph(escape(str(machine_type)), body_style),
            Paragraph("<b>Machine ID</b>", body_style),
            Paragraph(escape(str(machine_id)), body_style)
        ],
        [
            Paragraph("<b>Manufacturer</b>", body_style),
            Paragraph(escape(str(manufacturer)), body_style),
            Paragraph("<b>Report</b>", body_style),
            Paragraph("AI-Assisted Engineering Analysis", body_style)
        ]
    ]

    machine_table = Table(
        machine_data,
        colWidths=[32 * mm, 52 * mm, 30 * mm, 52 * mm]
    )

    machine_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#EAF1F8")
            ),
            (
                "BACKGROUND",
                (2, 0),
                (2, -1),
                colors.HexColor("#EAF1F8")
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.7,
                colors.HexColor("#B8C7D9")
            ),
            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#D5DDE5")
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(machine_table)

    story.append(Spacer(1, 12))

    # =================================================
    # ENGINEERING ANALYSIS
    # =================================================

    story.append(
        Paragraph(
            "2. Engineering Analysis",
            section_style
        )
    )

    # =================================================
    # CLEAN AI REPORT
    # =================================================

    lines = final_report.split("\n")

    cause_number = 0

    for raw_line in lines:

        line = raw_line.strip()

        if not line:
            story.append(Spacer(1, 4))
            continue

        # -------------------------------------------------
        # Remove Markdown heading symbols
        # -------------------------------------------------

        if line.startswith("### "):
            heading = line[4:].strip()

            story.append(
                Paragraph(
                    escape(heading),
                    section_style
                )
            )

            continue

        if line.startswith("## "):
            heading = line[3:].strip()

            story.append(
                Paragraph(
                    escape(heading),
                    section_style
                )
            )

            continue

        # -------------------------------------------------
        # Possible Cause headings
        # -------------------------------------------------

        if line.lower().startswith("possible cause"):

            cause_number += 1

            clean_heading = re.sub(
                r"^#+\s*",
                "",
                line
            )

            clean_heading = clean_heading.replace(
                "**",
                ""
            )

            story.append(
                Paragraph(
                    escape(clean_heading),
                    ParagraphStyle(
                        "CauseHeading",
                        parent=section_style,
                        fontSize=11,
                        leading=14,
                        textColor=colors.HexColor("#244F7A"),
                        spaceBefore=7,
                        spaceAfter=4
                    )
                )
            )

            continue

        # -------------------------------------------------
        # Numbered list
        # -------------------------------------------------

        numbered_match = re.match(
            r"^(\d+)[\.\)]\s+(.*)",
            line
        )

        if numbered_match:

            number = numbered_match.group(1)
            text = numbered_match.group(2)

            text = text.replace("**", "")

            story.append(
                Paragraph(
                    f"<b>{number}.</b> {escape(text)}",
                    numbered_style
                )
            )

            continue

        # -------------------------------------------------
        # Bullet list
        # -------------------------------------------------

        if line.startswith("- ") or line.startswith("* "):

            bullet_text = line[2:].strip()

            # Remove Markdown bold
            bullet_text = bullet_text.replace("**", "")

            story.append(
                Paragraph(
                    f"• {escape(bullet_text)}",
                    bullet_style
                )
            )

            continue

        # -------------------------------------------------
        # Bold labels such as Why / How to Confirm
        # -------------------------------------------------

        clean_line = line.replace("**", "")

        # Detect labels before colon
        if ":" in clean_line:

            label, content = clean_line.split(
                ":",
                1
            )

            if len(label) < 35:

                story.append(
                    Paragraph(
                        f"<b>{escape(label.strip())}:</b> "
                        f"{escape(content.strip())}",
                        body_style
                    )
                )

                continue

        # -------------------------------------------------
        # Normal paragraph
        # -------------------------------------------------

        story.append(
            Paragraph(
                escape(clean_line),
                body_style
            )
        )

    # =================================================
    # DISCLAIMER
    # =================================================

    story.append(Spacer(1, 15))

    disclaimer_data = [[
        Paragraph(
            "<b>Important:</b> This report provides AI-assisted "
            "initial troubleshooting guidance. It does not replace "
            "qualified engineering inspection, manufacturer procedures, "
            "or site safety requirements.",
            small_style
        )
    ]]

    disclaimer_table = Table(
        disclaimer_data,
        colWidths=[164 * mm]
    )

    disclaimer_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.HexColor("#F4F6F8")
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.6,
                colors.HexColor("#C8D0D8")
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )
        ])
    )

    story.append(disclaimer_table)

    story.append(Spacer(1, 15))

    # =================================================
    # FOOTER
    # =================================================

    story.append(
        Paragraph(
            "Generated by MechCare AI",
            small_style
        )
    )

    story.append(
        Paragraph(
            "AI-Based Mechanical Maintenance & Troubleshooting Assistant",
            small_style
        )
    )

    # =================================================
    # PAGE NUMBER
    # =================================================

    def add_page_number(canvas, doc):

        canvas.saveState()

        width, height = A4

        canvas.setStrokeColor(
            colors.HexColor("#D5DDE5")
        )

        canvas.line(
            45,
            32,
            width - 45,
            32
        )

        canvas.setFont(
            "Helvetica",
            8
        )

        canvas.setFillColor(
            colors.HexColor("#666666")
        )

        canvas.drawString(
            45,
            20,
            "MechCare AI | Engineering Report"
        )

        canvas.drawRightString(
            width - 45,
            20,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    # =================================================
    # BUILD PDF
    # =================================================

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )
