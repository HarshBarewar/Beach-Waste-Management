"""
PDF Assessment Report Generator for BeachWaste AI.

Generates professional, printable PDF assessment reports utilizing ReportLab,
incorporating executive summaries, historical observations, multi-horizon forecasts,
waste composition shares, recycling cost calculations, and environmental recommendations.
"""
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from backend.app.core.config import settings

def generate_pdf_report(
    beach_info: Dict[str, Any],
    forecast_data: Dict[str, Any],
    composition_data: Dict[str, Any],
    cost_data: Dict[str, Any],
    output_filename: str = None
) -> Path:
    """
    Builds a comprehensive, styled PDF beach waste assessment report.
    """
    reports_dir = settings.REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    filename = output_filename or f"BeachWaste_Report_{beach_info.get('id', 'beach')}_{int(datetime.now(timezone.utc).timestamp())}.pdf"
    file_path = reports_dir / filename

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f766e')  # Deep Teal
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#64748b')
    )
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0369a1'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1e293b')
    )
    notice_style = ParagraphStyle(
        'NoticeBox',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#b45309')
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("BeachWaste AI — Coastal Waste Assessment & Forecast", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} | Deep Learning Lab Edition", subtitle_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0d9488'), spaceBefore=2, spaceAfter=8))

    # Synthetic / Data Quality Warning Banner
    banner_text = (
        "<b>DATA PROVENANCE NOTICE:</b> This assessment contains synthetic baseline demonstration data "
        "and deep learning statistical forecasts. Historical inputs and forward projections are labeled with their "
        "respective quality flags. Financial treatment figures represent calibrated models rather than fixed quotes."
    )
    elements.append(Paragraph(banner_text, notice_style))
    elements.append(Spacer(1, 10))

    # Section 1: Beach Metadata
    elements.append(Paragraph("1. Beach & Geographic Profile", h2_style))
    meta_table_data = [
        [
            Paragraph("<b>Beach Name:</b>", body_style),
            Paragraph(f"{beach_info.get('name', 'N/A')}", body_style),
            Paragraph("<b>Country / Region:</b>", body_style),
            Paragraph(f"{beach_info.get('country', 'N/A')} ({beach_info.get('region', 'N/A')})", body_style)
        ],
        [
            Paragraph("<b>Coordinates:</b>", body_style),
            Paragraph(f"{beach_info.get('latitude', 0.0):.4f}°N, {beach_info.get('longitude', 0.0):.4f}°E", body_style),
            Paragraph("<b>Coastal Type:</b>", body_style),
            Paragraph(f"{beach_info.get('coastal_type', 'Sandy Shore')}", body_style)
        ],
        [
            Paragraph("<b>Data Records:</b>", body_style),
            Paragraph(f"{beach_info.get('total_observations', 0)} Monthly Observations", body_style),
            Paragraph("<b>Data Quality Flag:</b>", body_style),
            Paragraph(f"{beach_info.get('data_source_type', 'SYNTHETIC_DEMO')}", body_style)
        ]
    ]
    t_meta = Table(meta_table_data, colWidths=[100, 170, 110, 160])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 10))

    # Section 2: Deep Learning Waste Forecast
    horizon = forecast_data.get('horizon_months', 6)
    model_name = forecast_data.get('model_type', 'LSTM').upper()
    elements.append(Paragraph(f"2. Deep Learning Forecast ({horizon}-Month Horizon | Model: {model_name})", h2_style))

    monthly_forecasts = forecast_data.get('monthly_forecasts', [])
    forecast_table_data = [
        ["Month", "Target Date", "Predicted Waste (kg)", "90% Confidence Interval (kg)", "Estimated Cost"]
    ]
    for pt in monthly_forecasts[:12]:
        forecast_table_data.append([
            f"+{pt.get('month_index')}",
            pt.get('forecast_date', ''),
            f"{pt.get('predicted_waste_kg', 0):,.1f}",
            f"[{pt.get('lower_bound_kg', 0):,.1f} - {pt.get('upper_bound_kg', 0):,.1f}]",
            f"{cost_data.get('currency', 'USD')} {pt.get('estimated_cost_total', 0):,.2f}"
        ])

    t_forecast = Table(forecast_table_data, colWidths=[45, 100, 125, 170, 100])
    t_forecast.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f766e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdfa')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_forecast)
    elements.append(Spacer(1, 10))

    # Section 3: Material & Recovery Breakdown
    elements.append(Paragraph("3. Waste Composition & Stream Allocation", h2_style))
    materials = composition_data.get('materials', [])
    comp_table_data = [
        ["Material Category", "Estimated Share (%)", f"Projected Mass (kg)", "Recovery Stream Class"]
    ]
    for m in materials:
        comp_table_data.append([
            m.get('category'),
            f"{m.get('percentage'):.1f}%",
            f"{m.get('mass_kg', 0):,.1f}",
            m.get('treatment_class')
        ])

    t_comp = Table(comp_table_data, colWidths=[130, 95, 115, 200])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (2, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    elements.append(t_comp)
    elements.append(Spacer(1, 10))

    # Section 4: Treatment & Recycling Cost Summary
    curr = cost_data.get('currency', 'USD')
    elements.append(Paragraph(f"4. Treatment & Recycling Financial Estimation ({curr})", h2_style))
    cost_rows = [
        ["Collection Operations", f"{curr} {cost_data.get('collection_cost', 0):,.2f}", "Recycling Processing", f"{curr} {cost_data.get('recycling_processing_cost', 0):,.2f}"],
        ["Haulage & Transport", f"{curr} {cost_data.get('transport_cost', 0):,.2f}", "Non-Recyclable Residual Disposal", f"{curr} {cost_data.get('non_recyclable_disposal_cost', 0):,.2f}"],
        ["Materials Recovery Sorting", f"{curr} {cost_data.get('sorting_cost', 0):,.2f}", "Organic Waste Composting", f"{curr} {cost_data.get('organic_composting_cost', 0):,.2f}"],
        ["Fixed Facilities / Admin", f"{curr} {cost_data.get('fixed_operating_cost', 0):,.2f}", "Gross Operating Cost", f"{curr} {cost_data.get('gross_total_cost', 0):,.2f}"],
        ["Material Sales Credits", f"- {curr} {cost_data.get('material_credits_or_revenue', 0):,.2f}", "<b>Net Required Budget</b>", f"<b>{curr} {cost_data.get('net_total_cost', 0):,.2f}</b>"]
    ]
    t_cost = Table(cost_rows, colWidths=[150, 120, 150, 120])
    t_cost.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BACKGROUND', (2, -1), (3, -1), colors.HexColor('#ccfbf1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    elements.append(t_cost)
    elements.append(Spacer(1, 10))

    # Section 5: Environmental Recommendations
    elements.append(Paragraph("5. Scientific & Ecological Recommendations", h2_style))
    recs = [
        "• <b>Source Reduction:</b> Implement targeted single-use plastic deposit-refund schemes at beach access kiosks.",
        "• <b>Monsoon / Storm Preparation:</b> Deploy seasonal storm-drain debris booms ahead of projected high-wind months.",
        "• <b>Community Volunteer Cleanups:</b> Target peak tourist months with scheduled weekend community stewardship drives.",
        "• <b>Material Value Recovery:</b> Partner with certified regional PET and aluminium reclaimers to offset hauling expenses."
    ]
    for r in recs:
        elements.append(Paragraph(r, body_style))
        elements.append(Spacer(1, 3))

    doc.build(elements)
    return file_path
