"""
PDF generation service for architecture packages.
Generates professional PDF documents with architecture details, service stack, deployment approach, and KPIs.
"""

from io import BytesIO
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from .models import IdeaCase, ArchitecturePackage


# Professional color palette
PRIMARY_COLOR = colors.HexColor("#1e40af")  # Deep blue
SECONDARY_COLOR = colors.HexColor("#64748b")  # Slate gray
ACCENT_COLOR = colors.HexColor("#0ea5e9")  # Sky blue
SUCCESS_COLOR = colors.HexColor("#10b981")  # Green
TEXT_COLOR = colors.HexColor("#1e293b")  # Dark slate
LIGHT_BG = colors.HexColor("#f8fafc")  # Very light gray
BORDER_COLOR = colors.HexColor("#e2e8f0")  # Light border


def _create_styles():
    """Create custom paragraph styles for the PDF."""
    styles = getSampleStyleSheet()
    
    # Title style
    styles.add(ParagraphStyle(
        name="CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=PRIMARY_COLOR,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    ))
    
    # Subtitle style
    styles.add(ParagraphStyle(
        name="CustomSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=SECONDARY_COLOR,
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName="Helvetica",
    ))
    
    # Section heading
    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=PRIMARY_COLOR,
        spaceAfter=10,
        spaceBefore=16,
        fontName="Helvetica-Bold",
        borderWidth=0,
        borderPadding=0,
    ))
    
    # Subsection heading
    styles.add(ParagraphStyle(
        name="SubsectionHeading",
        parent=styles["Heading3"],
        fontSize=13,
        textColor=ACCENT_COLOR,
        spaceAfter=8,
        spaceBefore=12,
        fontName="Helvetica-Bold",
    ))
    
    # Body text
    styles.add(ParagraphStyle(
        name="AppBody",
        parent=styles["Normal"],
        fontSize=10,
        textColor=TEXT_COLOR,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName="Helvetica",
        leading=14,
    ))
    
    # Metadata text
    styles.add(ParagraphStyle(
        name="MetaText",
        parent=styles["Normal"],
        fontSize=9,
        textColor=SECONDARY_COLOR,
        spaceAfter=6,
        fontName="Helvetica",
        leading=12,
    ))
    
    # List item
    styles.add(ParagraphStyle(
        name="ListItem",
        parent=styles["Normal"],
        fontSize=10,
        textColor=TEXT_COLOR,
        spaceAfter=4,
        leftIndent=20,
        fontName="Helvetica",
        leading=13,
    ))
    
    return styles


def _add_header_section(story, styles, idea: IdeaCase, package: ArchitecturePackage):
    """Add document header with title and metadata."""
    story.append(Paragraph(package.solution_name, styles["CustomTitle"]))
    story.append(Paragraph("Architecture Package", styles["CustomSubtitle"]))
    story.append(Spacer(1, 0.2 * inch))
    
    # Metadata table
    metadata = [
        ["Idea ID", idea.idea_id],
        ["Owner", idea.owner_display_name],
        ["Tenant", idea.tenant_id],
        ["Status", idea.status.value if hasattr(idea.status, 'value') else str(idea.status)],
        ["Stage", idea.current_stage.value if hasattr(idea.current_stage, 'value') else str(idea.current_stage)],
        ["Generated", package.generated_at.strftime("%Y-%m-%d %H:%M UTC")],
    ]
    
    table = Table(metadata, colWidths=[1.5 * inch, 4.5 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
        ("TEXTCOLOR", (0, 0), (0, -1), SECONDARY_COLOR),
        ("TEXTCOLOR", (1, 0), (1, -1), TEXT_COLOR),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3 * inch))


def _add_executive_summary(story, styles, idea: IdeaCase, package: ArchitecturePackage):
    """Add executive summary section."""
    story.append(Paragraph("Executive Summary", styles["SectionHeading"]))
    story.append(Paragraph(package.summary, styles["AppBody"]))
    story.append(Spacer(1, 0.15 * inch))
    
    # Problem and value
    story.append(Paragraph("Business Problem", styles["SubsectionHeading"]))
    story.append(Paragraph(idea.problem_statement, styles["AppBody"]))
    
    story.append(Paragraph("Expected Business Value", styles["SubsectionHeading"]))
    story.append(Paragraph(idea.expected_value, styles["AppBody"]))
    
    if idea.affected_users:
        story.append(Paragraph("Affected Users", styles["SubsectionHeading"]))
        for user in idea.affected_users:
            story.append(Paragraph(f"• {user}", styles["ListItem"]))
    
    story.append(Spacer(1, 0.2 * inch))


def _add_architecture_components(story, styles, package: ArchitecturePackage):
    """Add architecture components section."""
    story.append(Paragraph("Architecture Components", styles["SectionHeading"]))
    
    if package.components:
        component_data = [["Component", "Purpose"]]
        for comp in package.components:
            component_data.append([comp.name, comp.purpose])
        
        table = Table(component_data, colWidths=[2.2 * inch, 3.8 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("TEXTCOLOR", (0, 1), (-1, -1), TEXT_COLOR),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No components defined.", styles["MetaText"]))
    
    story.append(Spacer(1, 0.2 * inch))


def _add_service_stack(story, styles, package: ArchitecturePackage):
    """Add recommended service stack section."""
    story.append(Paragraph("Recommended Service Stack", styles["SectionHeading"]))
    
    if package.suggested_component_catalog:
        stack_data = [["Service", "Description"]]
        for comp in package.suggested_component_catalog:
            stack_data.append([comp.name, comp.purpose])
        
        table = Table(stack_data, colWidths=[2.2 * inch, 3.8 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("TEXTCOLOR", (0, 1), (-1, -1), TEXT_COLOR),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No service stack defined.", styles["MetaText"]))
    
    story.append(Spacer(1, 0.2 * inch))


def _add_deployment_approach(story, styles, package: ArchitecturePackage):
    """Add deployment approach section."""
    story.append(Paragraph("Deployment Approach", styles["SectionHeading"]))
    
    if package.deployment_steps:
        for idx, step in enumerate(package.deployment_steps, 1):
            story.append(Paragraph(f"{idx}. {step}", styles["ListItem"]))
    else:
        story.append(Paragraph("No deployment steps defined.", styles["MetaText"]))
    
    story.append(Spacer(1, 0.15 * inch))
    
    if package.integration_points:
        story.append(Paragraph("Integration Points", styles["SubsectionHeading"]))
        for point in package.integration_points:
            story.append(Paragraph(f"• {point}", styles["ListItem"]))
    
    story.append(Spacer(1, 0.2 * inch))


def _add_consumption_estimate(story, styles, package: ArchitecturePackage):
    """Add consumption and cost estimate section."""
    if package.monthly_production_consumption is None:
        return
    
    story.append(Paragraph("Consumption & Cost Estimate", styles["SectionHeading"]))
    
    consumption = package.monthly_production_consumption
    consumption_data = [
        ["Metric", "Value"],
        ["Monthly Executions", f"{consumption.monthly_executions:,}"],
        ["Prompt Tokens per Execution", f"{consumption.prompt_tokens_per_execution:,}"],
        ["Completion Tokens per Execution", f"{consumption.completion_tokens_per_execution:,}"],
        ["Monthly Prompt Tokens", f"{consumption.monthly_prompt_tokens:,}"],
        ["Monthly Completion Tokens", f"{consumption.monthly_completion_tokens:,}"],
        ["Estimated Monthly Cost", f"${consumption.estimated_monthly_cost_usd:,.2f}"],
    ]
    
    table = Table(consumption_data, colWidths=[3 * inch, 3 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SUCCESS_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("TEXTCOLOR", (0, 1), (-1, -1), TEXT_COLOR),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    
    if consumption.assumptions:
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("Assumptions", styles["SubsectionHeading"]))
        for assumption in consumption.assumptions:
            story.append(Paragraph(f"• {assumption}", styles["ListItem"]))
    
    story.append(Spacer(1, 0.2 * inch))


def _add_kpis_section(story, styles, idea: IdeaCase):
    """Add KPIs section based on business validation."""
    story.append(Paragraph("Key Performance Indicators", styles["SectionHeading"]))
    
    kpis = []
    
    if idea.business_validation:
        bv = idea.business_validation
        if hasattr(bv, 'value_score') and bv.value_score:
            kpis.append(("Business Value Score", f"{bv.value_score}/10"))
        if hasattr(bv, 'risk_score') and bv.risk_score:
            kpis.append(("Risk Assessment Score", f"{bv.risk_score}/10"))
        if hasattr(bv, 'assumptions') and bv.assumptions:
            kpis.append(("Key Assumptions", f"{len(bv.assumptions)} identified"))
    
    if idea.technical_validation:
        tv = idea.technical_validation
        if hasattr(tv, 'recommendation') and tv.recommendation:
            kpis.append(("Technical Recommendation", tv.recommendation.upper()))
    
    if kpis:
        kpi_data = [["KPI", "Value"]]
        kpi_data.extend(kpis)
        
        table = Table(kpi_data, colWidths=[3 * inch, 3 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("TEXTCOLOR", (0, 1), (-1, -1), TEXT_COLOR),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No KPIs available.", styles["MetaText"]))
    
    story.append(Spacer(1, 0.2 * inch))


def _add_risks_section(story, styles, package: ArchitecturePackage):
    """Add risks section."""
    if not package.risks:
        return
    
    story.append(Paragraph("Identified Risks", styles["SectionHeading"]))
    for risk in package.risks:
        story.append(Paragraph(f"• {risk}", styles["ListItem"]))
    story.append(Spacer(1, 0.2 * inch))


def _add_footer(story, styles):
    """Add document footer."""
    story.append(Spacer(1, 0.3 * inch))
    footer_text = (
        f"Document generated on {datetime.utcnow().strftime('%Y-%m-%d at %H:%M UTC')} | "
        "AI Value Hub Platform"
    )
    story.append(Paragraph(footer_text, styles["MetaText"]))


def generate_architecture_pdf(idea: IdeaCase) -> BytesIO:
    """
    Generate a professional PDF document for an architecture package.
    
    Args:
        idea: IdeaCase with architecture_package populated
        
    Returns:
        BytesIO buffer containing the PDF
        
    Raises:
        ValueError: If idea has no architecture_package
    """
    if idea.architecture_package is None:
        raise ValueError("Idea has no architecture package")
    
    package = idea.architecture_package
    buffer = BytesIO()
    styles = _create_styles()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=f"{package.solution_name} - Architecture Package",
        author="AI Value Hub",
    )
    
    story = []
    
    # Build document sections
    _add_header_section(story, styles, idea, package)
    _add_executive_summary(story, styles, idea, package)
    _add_architecture_components(story, styles, package)
    _add_service_stack(story, styles, package)
    _add_deployment_approach(story, styles, package)
    _add_consumption_estimate(story, styles, package)
    _add_kpis_section(story, styles, idea)
    _add_risks_section(story, styles, package)
    _add_footer(story, styles)
    
    doc.build(story)
    buffer.seek(0)
    
    return buffer
