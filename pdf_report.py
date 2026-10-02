from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from xml.sax.saxutils import escape
import re
import os


# =================================================
# UNICODE FONT
# =================================================

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

if os.path.exists(FONT_PATH) and os.path.exists(FONT_BOLD_PATH):

    pdfmetrics.registerFont(
        TTFont("DejaVuSans", FONT_PATH)
    )

    pdfmetrics.registerFont(
        TTFont("DejaVuSans-Bold", FONT_BOLD_PATH)
    )

    NORMAL_FONT = "DejaVuSans"
    BOLD_FONT = "DejaVuSans-Bold"

else:

    NORMAL_FONT = "Helvetica"
    BOLD_FONT = "Helvetica-Bold"


def clean_text(text):

    text = str(text)

    # Replace common Unicode punctuation
    replacements = {
        "\u2013": "-",   # en dash
        "\u2014": "-",   # em dash
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2022": "-",   # bullet
        "\u00a0": " ",   # non-breaking space
        "\u2026": "...", # ellipsis
        "\u2192": "->",  # arrow
        "\u00d7": "x",   # multiplication sign
        "\u00b0": " deg", # degree symbol
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove zero-width and invisible characters
    invisible_chars = [
        "\u200b",
        "\u200c",
        "\u200d",
        "\u2060",
        "\ufeff",
        "\u00ad"
    ]

    for char in invisible_chars:
        text = text.replace(char, "")

    # Keep only safe printable ASCII characters
    cleaned = ""

    for char in text:

        if 32 <= ord(char) <= 126:
            cleaned += char

        elif char in "\n\r\t":
            cleaned += char

        else:
            # Replace any remaining unsupported Unicode character
            cleaned += ""

    return cleaned.strip()

    """
    Clean hidden/control characters that can sometimes
    appear in user or AI-generated text.
    """

    text = str(text)

    # Remove zero-width characters
    text = text.replace("\u200b", "")
    text = text.replace("\u200c", "")
    text = text.replace("\u200d", "")
    text = text.replace("\ufeff", "")

    # Replace unusual line characters
    text = text.replace("\r", "")
    text = text.replace("\t", " ")

    return text.strip()


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
        fontName=BOLD_FONT,
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName=NORMAL_FONT,
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName=BOLD_FONT,
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#17365D"),
        spaceBefore=12,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName=NORMAL_FONT,
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

    cause_style = ParagraphStyle(
        "CauseHeading",
        parent=section_style,
        fontName=BOLD_FONT,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#244F7A"),
        spaceBefore=7,
        spaceAfter=4
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontName=NORMAL_FONT,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#666666")
    )

    # =================================================
    # STORY
    # =================================================

    story = []

    # =================================================
    # TITLE
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

    machine_type = clean_text(machine_type)
    machine_id = clean_text(machine_id)
    manufacturer = clean_text(manufacturer)

    machine_data = [
        [
            Paragraph("<b>Machine Type</b>", body_style),
            Paragraph(escape(machine_type), body_style),
            Paragraph("<b>Machine ID</b>", body_style),
            Paragraph(escape(machine_id), body_style)
        ],
        [
            Paragraph("<b>Manufacturer</b>", body_style),
            Paragraph(escape(manufacturer), body_style),
            Paragraph("<b>Report</b>", body_style),
            Paragraph(
                "AI-Assisted Engineering Analysis",
                body_style
            )
        ]
    ]

    machine_table = Table(
        machine_data,
        colWidths=[
            32 * mm,
            52 * mm,
            30 * mm,
            52 * mm
        ]
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

    final_report = clean_text(final_report)

    # =================================================
    # PROCESS AI REPORT
    # =================================================

    for raw_line in final_report.split("\n"):

        line = clean_text(raw_line)

        if not line:
            story.append(Spacer(1, 4))
            continue

        # -------------------------------------------------
        # Markdown headings
        # -------------------------------------------------

        if line.startswith("### "):

            heading = line[4:].strip()

            story.append(
                Paragraph(
                    escape(
                        heading.replace("**", "")
                    ),
                    section_style
                )
            )

            continue

        if line.startswith("## "):

            heading = line[3:].strip()

            story.append(
                Paragraph(
                    escape(
                        heading.replace("**", "")
                    ),
                    section_style
                )
            )

            continue

        # -------------------------------------------------
        # Possible Cause headings
        # -------------------------------------------------

        if line.lower().startswith("possible cause"):

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
                    cause_style
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
                    f"<b>{number}.</b> "
                    f"{escape(text)}",
                    numbered_style
                )
            )

            continue

        # -------------------------------------------------
        # Bullet list
        # -------------------------------------------------

        if line.startswith("- ") or line.startswith("* "):

            bullet_text = line[2:].strip()

            bullet_text = bullet_text.replace(
                "**",
                ""
            )

            story.append(
                Paragraph(
                    f"• {escape(bullet_text)}",
                    bullet_style
                )
            )

            continue

        # -------------------------------------------------
        # Bold labels
        # -------------------------------------------------

        clean_line = line.replace(
            "**",
            ""
        )

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
    # FOOTER / PAGE NUMBER
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
            NORMAL_FONT,
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
