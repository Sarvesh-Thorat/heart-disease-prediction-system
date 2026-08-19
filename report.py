import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)


def generate_pdf(
    patient_id,
    patient_name,
    age,
    sex,
    prediction,
    probability,
    risk_level,
    prediction_date
):

    # =====================================================
    # FILE PATH
    # =====================================================

    filename = f"heartcare_report_{patient_id}.pdf"
    file_path = os.path.join("reports", filename)

    os.makedirs("reports", exist_ok=True)

    # =====================================================
    # DOCUMENT
    # =====================================================

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    # =====================================================
    # COLORS
    # =====================================================

    teal = colors.HexColor("#0F766E")
    dark = colors.HexColor("#172554")
    text = colors.HexColor("#334155")
    muted = colors.HexColor("#64748B")
    border = colors.HexColor("#CBD5E1")
    light = colors.HexColor("#F8FAFC")

    # =====================================================
    # RISK COLORS
    # =====================================================

    risk = str(risk_level).lower()

    if "high" in risk:
        risk_color = colors.HexColor("#DC2626")
        risk_bg = colors.HexColor("#FEE2E2")
        risk_message = "High Risk Detected"

    elif "medium" in risk:
        risk_color = colors.HexColor("#D97706")
        risk_bg = colors.HexColor("#FEF3C7")
        risk_message = "Moderate Risk Detected"

    else:
        risk_color = colors.HexColor("#16A34A")
        risk_bg = colors.HexColor("#DCFCE7")
        risk_message = "Low Risk Detected"

    # =====================================================
    # STYLES
    # =====================================================

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        textColor=teal,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        alignment=TA_CENTER,
        textColor=muted,
        spaceAfter=12
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=dark,
        spaceBefore=8,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=text
    )

    center_style = ParagraphStyle(
        "CenterStyle",
        parent=normal_style,
        alignment=TA_CENTER
    )

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=normal_style,
        fontSize=8.5,
        leading=12,
        textColor=muted
    )

    # =====================================================
    # CONTENT
    # =====================================================

    elements = []

    # =====================================================
    # HEADER
    # =====================================================

    header_table = Table(
        [[
            Paragraph(
                "<b>HeartCare</b>",
                ParagraphStyle(
                    "HeaderBrand",
                    parent=normal_style,
                    fontSize=21,
                    textColor=teal,
                    fontName="Helvetica-Bold"
                )
            ),
            Paragraph(
                "Heart Disease<br/>Prediction System",
                ParagraphStyle(
                    "HeaderRight",
                    parent=normal_style,
                    fontSize=8.5,
                    leading=11,
                    alignment=TA_CENTER,
                    textColor=muted
                )
            )
        ]],
        colWidths=[350, 140]
    )

    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )

    elements.append(header_table)

    elements.append(
        HRFlowable(
            width="100%",
            thickness=1.5,
            color=teal,
            spaceBefore=3,
            spaceAfter=15
        )
    )

    # =====================================================
    # REPORT TITLE
    # =====================================================

    elements.append(
        Paragraph(
            "HEART DISEASE REPORT",
            ParagraphStyle(
                "ReportTitle",
                parent=styles["Heading1"],
                fontName="Helvetica-Bold",
                fontSize=16,
                alignment=TA_CENTER,
                textColor=dark,
                spaceAfter=5
            )
        )
    )

    elements.append(
        Paragraph(
            "Patient Risk Assessment Report",
            subtitle_style
        )
    )

    elements.append(Spacer(1, 5))

    # =====================================================
    # PATIENT INFORMATION
    # =====================================================

    elements.append(
        Paragraph(
            "Patient Information",
            section_style
        )
    )

    patient_data = [
        [
            Paragraph("<b>Patient ID</b>", normal_style),
            str(patient_id),
            Paragraph("<b>Patient Name</b>", normal_style),
            str(patient_name)
        ],
        [
            Paragraph("<b>Age</b>", normal_style),
            str(age),
            Paragraph("<b>Sex</b>", normal_style),
            str(sex)
        ],
        [
            Paragraph("<b>Prediction Date</b>", normal_style),
            str(prediction_date),
            Paragraph("<b>Report Type</b>", normal_style),
            "Heart Disease Risk Assessment"
        ]
    ]

    patient_table = Table(
        patient_data,
        colWidths=[85, 145, 100, 150]
    )

    patient_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), light),
            ("BACKGROUND", (2, 0), (2, -1), light),

            ("GRID", (0, 0), (-1, -1),
             0.6, border),

            ("VALIGN", (0, 0), (-1, -1),
             "MIDDLE"),

            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10)
        ])
    )

    elements.append(patient_table)

    elements.append(Spacer(1, 18))

    # =====================================================
    # PREDICTION RESULT
    # =====================================================

    elements.append(
        Paragraph(
            "Prediction Result",
            section_style
        )
    )

    probability_value = float(probability)

    result_data = [
        [
            Paragraph("<b>PREDICTION</b>", center_style),
            Paragraph("<b>PROBABILITY</b>", center_style),
            Paragraph("<b>RISK LEVEL</b>", center_style)
        ],
        [
            Paragraph(
                f"<b>{prediction}</b>",
                ParagraphStyle(
                    "PredictionValue",
                    parent=center_style,
                    fontSize=12,
                    textColor=risk_color
                )
            ),
            Paragraph(
                f"<b>{probability_value:.2f}%</b>",
                ParagraphStyle(
                    "ProbabilityValue",
                    parent=center_style,
                    fontSize=13,
                    textColor=teal
                )
            ),
            Paragraph(
                f"<b>{risk_level}</b>",
                ParagraphStyle(
                    "RiskValue",
                    parent=center_style,
                    fontSize=12,
                    textColor=risk_color
                )
            )
        ]
    ]

    result_table = Table(
        result_data,
        colWidths=[175, 175, 150]
    )

    result_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), teal),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("BACKGROUND", (0, 1), (-1, 1), risk_bg),

            ("GRID", (0, 0), (-1, -1),
             0.6, border),

            ("VALIGN", (0, 0), (-1, -1),
             "MIDDLE"),

            ("ALIGN", (0, 0), (-1, -1),
             "CENTER"),

            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12)
        ])
    )

    elements.append(result_table)

    elements.append(Spacer(1, 18))

    # =====================================================
    # PROBABILITY BAR
    # =====================================================

    

    # =====================================================
    # FOOTER
    # =====================================================

    elements.append(
        HRFlowable(
            width="100%",
            thickness=0.8,
            color=border,
            spaceBefore=5,
            spaceAfter=8
        )
    )

    
    # =====================================================
    # BUILD PDF
    # =====================================================

    doc.build(elements)

    return file_path