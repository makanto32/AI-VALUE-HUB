from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable, ListItem, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Drawing, String, Rect, Line, PolyLine

output_path = "docs/AI_Opportunity_Hub_Architecture_Reference.pdf"

styles = getSampleStyleSheet()
if 'ClientTitle' not in styles.byName:
    styles.add(ParagraphStyle(name='ClientTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=20, leading=24, spaceAfter=12, textColor=colors.HexColor('#0f4c81')))
if 'ClientHeading' not in styles.byName:
    styles.add(ParagraphStyle(name='ClientHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, leading=16, spaceAfter=8, textColor=colors.HexColor('#0f4c81')))
if 'ClientBody' not in styles.byName:
    styles.add(ParagraphStyle(name='ClientBody', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=13, spaceAfter=6, textColor=colors.HexColor('#1f2937')))
if 'ClientBullet' not in styles.byName:
    styles.add(ParagraphStyle(name='ClientBullet', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=13, leftIndent=12, spaceAfter=4, textColor=colors.HexColor('#1f2937')))
if 'ClientCaption' not in styles.byName:
    styles.add(ParagraphStyle(name='ClientCaption', parent=styles['BodyText'], fontName='Helvetica-Oblique', fontSize=9, leading=11, textColor=colors.HexColor('#4b5563')))

story = []
story.append(Paragraph("AI Opportunity Hub\nReference Architecture", styles['ClientTitle']))
story.append(Paragraph("Client-ready architecture overview for solution evaluation, implementation planning, and reuse.", styles['ClientBody']))
story.append(Spacer(1, 0.3 * cm))

story.append(Paragraph("1. Solution Overview", styles['ClientHeading']))
story.append(Paragraph("AI Opportunity Hub is a reference solution that helps organizations capture ideas, evaluate technical feasibility, generate architecture packages, and prepare implementation guidance for AI initiatives.", styles['ClientBody']))
story.append(Spacer(1, 0.2 * cm))

story.append(Paragraph("2. Logical Layers", styles['ClientHeading']))
logical_items = [
    "Presentation Layer: React + Vite experience for idea intake and review",
    "Application Layer: FastAPI endpoints for validation, orchestration, and package generation",
    "Intelligence Layer: context evaluation and architecture decision logic",
    "Data Layer: local persistence, document storage, and artifact management",
    "Integration Layer: deployment readiness for Azure services, authentication, and future enterprise connectors"
]
story.append(ListFlowable([ListItem(Paragraph(item, styles['ClientBullet'])) for item in logical_items], bulletType='bullet'))
story.append(Spacer(1, 0.3 * cm))

story.append(Paragraph("3. Core Runtime Flow", styles['ClientHeading']))
flow_data = [
    ["User", "Frontend", "Idea capture"],
    ["API", "FastAPI", "Validation + orchestration"],
    ["Context Engine", "Domain Logic", "Business/technical assessment"],
    ["Architecture Package", "Output", "Components, risks, deployment steps"]
]
flow_table = Table(flow_data, colWidths=[3.2 * cm, 3.2 * cm, 6.4 * cm], repeatRows=1)
flow_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f4c81')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 9),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f9fafb'), colors.white]),
]))
story.append(flow_table)
story.append(Spacer(1, 0.3 * cm))

story.append(Paragraph("4. Reference Deployment Model", styles['ClientHeading']))
story.append(Paragraph("The architecture supports a local MVP deployment and a cloud-aligned Azure deployment path. The current implementation is optimized for rapid demonstration, while the structure is prepared for enterprise evolution.", styles['ClientBody']))
story.append(Spacer(1, 0.2 * cm))

story.append(Paragraph("5. Recommended Reuse Scenarios", styles['ClientHeading']))
reuse_items = [
    "Use the frontend and API layout as a foundation for a custom innovation portal",
    "Reuse the validation workflow for internal AI opportunity review programs",
    "Adapt the storage abstraction to enterprise databases and document services",
    "Replace demo authentication with Microsoft Entra ID for production rollout"
]
story.append(ListFlowable([ListItem(Paragraph(item, styles['ClientBullet'])) for item in reuse_items], bulletType='bullet'))
story.append(Spacer(1, 0.3 * cm))

story.append(Paragraph("6. Architecture Diagram", styles['ClientHeading']))
story.append(Paragraph("A visual summary of the solution follows.", styles['ClientCaption']))

# simple vector diagram
drawing = Drawing(16 * cm, 6 * cm)
# background
drawing.add(Rect(0.2 * cm, 0.2 * cm, 15.6 * cm, 5.6 * cm, fillColor=colors.HexColor('#f8fbff'), strokeColor=colors.HexColor('#d7e7f7'), strokeWidth=1))
# boxes
box_style = dict(fillColor=colors.HexColor('#e8f2ff'), strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.2)
drawing.add(Rect(1.0 * cm, 3.5 * cm, 3.0 * cm, 1.2 * cm, **box_style))
drawing.add(String(1.4 * cm, 3.95 * cm, 'Users / Clients'))
drawing.add(Rect(5.0 * cm, 3.5 * cm, 3.0 * cm, 1.2 * cm, **box_style))
drawing.add(String(5.45 * cm, 3.95 * cm, 'Frontend'))
drawing.add(Rect(9.0 * cm, 3.5 * cm, 3.0 * cm, 1.2 * cm, **box_style))
drawing.add(String(9.35 * cm, 3.95 * cm, 'API / Orchestrator'))
drawing.add(Rect(5.0 * cm, 1.0 * cm, 3.0 * cm, 1.2 * cm, **box_style))
drawing.add(String(5.25 * cm, 1.45 * cm, 'Data / Storage'))
# arrows
for x1, y1, x2, y2 in [(4.0, 4.1, 5.0, 4.1), (8.0, 4.1, 9.0, 4.1), (6.5, 3.5, 6.5, 2.2)]:
    drawing.add(Line(x1 * cm, y1 * cm, x2 * cm, y2 * cm, strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.2))
drawing.add(PolyLine([(3.5*cm, 4.1*cm),(3.8*cm, 4.1*cm)], strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.2))
drawing.add(PolyLine([(8.2*cm, 4.1*cm),(8.8*cm, 4.1*cm)], strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.2))
drawing.add(PolyLine([(6.5*cm, 3.5*cm),(6.5*cm, 2.2*cm)], strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.2))
story.append(drawing)
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph("This document is intended as a client-facing reference for architecture understanding, reuse, and implementation planning.", styles['ClientCaption']))

# Build pdf
pdf = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=2.2 * cm, leftMargin=2.2 * cm, topMargin=2.0 * cm, bottomMargin=2.0 * cm)
pdf.build(story)
print(output_path)
