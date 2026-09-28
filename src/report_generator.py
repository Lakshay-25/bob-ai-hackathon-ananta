"""
report_generator.py — Drishti SHO Intelligence Brief Generator
Generates a downloadable one-page PDF report for the Station House Officer.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime, timedelta


def _get_styles():
    """Create custom paragraph styles for the report."""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='ReportTitle',
        parent=styles['Title'],
        fontSize=20,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='ReportSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#16213e'),
        spaceBefore=14,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='BodyText2',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4,
        fontName='Helvetica',
        leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='Disclaimer',
        parent=styles['Normal'],
        fontSize=7,
        textColor=colors.HexColor('#999999'),
        spaceBefore=16,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        leading=9
    ))
    
    styles.add(ParagraphStyle(
        name='ZoneTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#0f3460'),
        spaceBefore=6,
        spaceAfter=2,
        fontName='Helvetica-Bold'
    ))
    
    return styles


def generate_sho_report(top5_data, explanations, patrol_suggestions, 
                         summary_stats, event_scenario=None):
    """
    Generate a complete SHO Intelligence Brief as a PDF.
    
    Args:
        top5_data: DataFrame of top 5 zones with risk scores
        explanations: list of 5 explain_zone() dicts
        patrol_suggestions: list of 5 suggest_patrol() dicts
        summary_stats: dict from get_summary_stats()
        event_scenario: optional simulate_event() dict
    
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )
    
    styles = _get_styles()
    elements = []
    
    # --- HEADER ---
    elements.append(Paragraph("DRISHTI", styles['ReportTitle']))
    elements.append(Paragraph("Weekly Crime Intelligence Brief", styles['ReportSubtitle']))
    
    next_week_start = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
    next_week_end = next_week_start + timedelta(days=6)
    date_str = f"Forecast Period: {next_week_start.strftime('%d %b %Y')} – {next_week_end.strftime('%d %b %Y')}"
    elements.append(Paragraph(date_str, styles['ReportSubtitle']))
    
    elements.append(Paragraph(
        "SYNTHETIC DATA — DEMONSTRATION ONLY",
        ParagraphStyle('Warning', parent=styles['Normal'], fontSize=9,
                       textColor=colors.HexColor('#e74c3c'), alignment=TA_CENTER,
                       fontName='Helvetica-Bold', spaceAfter=8)
    ))
    
    elements.append(HRFlowable(
        width="100%", thickness=1.5,
        color=colors.HexColor('#16213e'), spaceAfter=10
    ))
    
    # --- SECTION 1: SUMMARY STATS ---
    elements.append(Paragraph("1. Data Summary", styles['SectionHeader']))
    
    summary_data = [
        ['Total Incidents', 'Areas Analyzed', 'Date Range', 'Most Common Crime', 'High-Risk Zones'],
        [
            str(summary_stats['total_incidents']),
            str(summary_stats['total_areas']),
            summary_stats['date_range'],
            summary_stats['most_common_crime'],
            str(summary_stats['high_risk_zones'])
        ]
    ]
    
    summary_table = Table(summary_data, colWidths=[90, 80, 130, 100, 80])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, 1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f5f6fa')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 22),
    ]))
    elements.append(summary_table)
    
    # --- SECTION 2: TOP 5 ZONES ---
    elements.append(Paragraph("2. Top 5 At-Risk Micro-Zones", styles['SectionHeader']))
    
    zone_header = ['Rank', 'Zone', 'Risk Score', 'Incidents', 'Primary Crime', 'Trend']
    zone_rows = [zone_header]
    
    for i, (_, row) in enumerate(top5_data.iterrows()):
        exp = explanations[i] if i < len(explanations) else {}
        zone_rows.append([
            str(i + 1),
            row['area'],
            f"{row['risk_score']:.1f}",
            str(row['total_incidents']),
            exp.get('most_common_crime', 'N/A'),
            row['trend_direction']
        ])
    
    zone_table = Table(zone_rows, colWidths=[35, 65, 70, 65, 100, 65])
    zone_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 20),
        # Alternate row colors
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fff3f3')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#fff8f3')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#fffff3')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#f3fff3')),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#f3f8ff')),
    ]))
    elements.append(zone_table)
    
    # --- SECTION 3: ZONE DETAILS & PATROL ---
    elements.append(Paragraph("3. Zone Analysis & Patrol Recommendations", styles['SectionHeader']))
    
    for i in range(min(5, len(explanations))):
        exp = explanations[i]
        patrol = patrol_suggestions[i] if i < len(patrol_suggestions) else {}
        
        zone_block = []
        zone_block.append(Paragraph(
            f"Zone {i+1}: {exp['area']}",
            styles['ZoneTitle']
        ))
        zone_block.append(Paragraph(
            f"<b>Analysis:</b> {exp.get('explanation', 'No data.')}",
            styles['BodyText2']
        ))
        zone_block.append(Paragraph(
            f"<b>Patrol:</b> {patrol.get('recommendation', 'Standard coverage.')}",
            styles['BodyText2']
        ))
        zone_block.append(Spacer(1, 4))
        
        elements.append(KeepTogether(zone_block))
    
    # --- SECTION 4: EVENT SCENARIO (if provided) ---
    if event_scenario:
        elements.append(Paragraph("4. Event Impact Scenario", styles['SectionHeader']))
        elements.append(Paragraph(
            f"<b>Scenario:</b> {event_scenario.get('event', 'N/A')} near {event_scenario.get('area', 'N/A')}",
            styles['BodyText2']
        ))
        elements.append(Paragraph(
            f"<b>Impact:</b> Risk score {event_scenario.get('original_score', 0)} → "
            f"{event_scenario.get('adjusted_score', 0)} ({event_scenario.get('change_percent', '0%')})",
            styles['BodyText2']
        ))
        elements.append(Paragraph(
            f"<b>Note:</b> {event_scenario.get('label', '')}",
            styles['BodyText2']
        ))
    
    # --- FOOTER ---
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(
        width="100%", thickness=0.5,
        color=colors.HexColor('#cccccc'), spaceAfter=6
    ))
    elements.append(Paragraph(
        "This report uses synthetic data for demonstration purposes only. "
        "All recommendations are decision support for human review — the Station House Officer "
        "retains full authority over patrol deployment decisions. "
        "Drishti does not profile individuals. All analysis is place-based and aggregate.",
        styles['Disclaimer']
    ))
    elements.append(Paragraph(
        f"Generated by Drishti v1.0 | Team Ananta | {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        styles['Disclaimer']
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
