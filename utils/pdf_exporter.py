import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from config import LOGO_PATH, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BG

def generate_executive_pdf(title, subtitle, kpi_dict, narrative_summary, table_data=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor(COLOR_PRIMARY), leading=18
    )
    sub_style = ParagraphStyle(
        'DocSub', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor("#64748B"), leading=11
    )
    body_style = ParagraphStyle(
        'DocBody', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor(COLOR_PRIMARY), leading=13
    )
    section_style = ParagraphStyle(
        'SectionHeading', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor(COLOR_SECONDARY), leading=14
    )
    
    header_text = [
        Paragraph(f"<b>{title.upper()}</b>", title_style),
        Spacer(1, 3),
        Paragraph(f"{subtitle} | Generated: {datetime.now().strftime('%B %d, %Y')}", sub_style)
    ]
    
    # Proportional logo handler prevents aspect ratio crushing
    if os.path.exists(LOGO_PATH):
        try:
            logo_img = Image(LOGO_PATH)
            # Constrain width while maintaining native aspect ratio dynamically
            aspect = logo_img.imageHeight / float(logo_img.imageWidth)
            logo_img.drawWidth = 80
            logo_img.drawHeight = 80 * aspect
            
            header_table = Table([[logo_img, header_text]], colWidths=[90, 430])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(header_table)
        except Exception:
            story.extend(header_text)
    else:
        story.extend(header_text)
        
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor(COLOR_SECONDARY), spaceBefore=0, spaceAfter=10))
    
    # Narrative Section
    story.append(Paragraph("<b>EXECUTIVE NARRATIVE BRIEF</b>", section_style))
    story.append(Spacer(1, 4))
    
    narrative_table = Table([[Paragraph(narrative_summary, body_style)]], colWidths=[520])
    narrative_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(COLOR_BG)),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(narrative_table)
    story.append(Spacer(1, 10))
    
    # KPI Grid
    story.append(Paragraph("<b>KEY OPERATIONAL METRICS SUMMARY</b>", section_style))
    story.append(Spacer(1, 5))
    
    kpi_table_data = []
    kpi_keys = list(kpi_dict.keys())
    
    for i in range(0, len(kpi_keys), 2):
        k1 = kpi_keys[i]
        v1 = str(kpi_dict[k1])
        if i + 1 < len(kpi_keys):
            k2 = kpi_keys[i+1]
            v2 = str(kpi_dict[k2])
            kpi_table_data.append([
                Paragraph(f"<b>{k1}:</b> {v1}", body_style),
                Paragraph(f"<b>{k2}:</b> {v2}", body_style)
            ])
        else:
            kpi_table_data.append([Paragraph(f"<b>{k1}:</b> {v1}", body_style), ""])
            
    if kpi_table_data:
        kpi_table = Table(kpi_table_data, colWidths=[260, 260])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(kpi_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()