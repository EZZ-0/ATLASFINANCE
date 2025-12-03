"""
PDF Export Module for Investment Summary
Generates professional IC-ready PDF reports
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Frame, PageTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
import pandas as pd


def generate_investment_summary_pdf(financials, generator, recommendation_data):
    """
    Generate a professional PDF report for Investment Summary
    
    Args:
        financials: Dictionary from USAFinancialExtractor
        generator: InvestmentSummaryGenerator instance
        recommendation_data: Dict from generate_recommendation()
    
    Returns:
        BytesIO buffer containing the PDF
    """
    
    # Create buffer
    buffer = io.BytesIO()
    
    # Create PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e88e5'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#3b82f6'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e88e5'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        textColor=colors.black
    )
    
    # Story (content)
    story = []
    
    # ===== HEADER =====
    story.append(Paragraph("INVESTMENT SUMMARY", title_style))
    story.append(Paragraph(f"{generator.ticker} - {generator.company_name}", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Recommendation Badge
    rec = recommendation_data['recommendation']
    conviction = recommendation_data['conviction']
    price_target = recommendation_data['price_target']
    upside_pct = recommendation_data['upside_pct']
    
    rec_color = colors.HexColor('#4caf50') if rec == 'BUY' else colors.HexColor('#f44336') if rec == 'SELL' else colors.HexColor('#ff9800')
    
    rec_table = Table([[
        Paragraph(f"<b>{rec} | PT: ${price_target:.0f} | {upside_pct:+.0f}% | {conviction} CONVICTION</b>", body_style)
    ]], colWidths=[6.5*inch])
    
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), rec_color),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 2, rec_color),
    ]))
    
    story.append(rec_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ===== BUSINESS MODEL =====
    story.append(Paragraph("Business Model", section_style))
    
    info = financials.get('info', {})
    sector = info.get('sector', 'N/A')
    industry = info.get('industry', 'N/A')
    employees = info.get('fullTimeEmployees', 'N/A')
    website = info.get('website', 'N/A')
    business_summary = info.get('longBusinessSummary', 'No business description available')
    
    # Business info table
    business_data = [
        ['Sector', sector],
        ['Industry', industry],
        ['Employees', f"{employees:,}" if isinstance(employees, int) else str(employees)],
        ['Website', website if website != 'N/A' else 'N/A']
    ]
    
    business_table = Table(business_data, colWidths=[2*inch, 4*inch])
    business_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e88e5')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
    ]))
    
    story.append(business_table)
    story.append(Spacer(1, 0.1*inch))
    
    # Business description - FULL TEXT for PDF
    if business_summary and business_summary != 'No business description available':
        # Show full text in PDF - use smaller font if very long
        if len(business_summary) > 800:
            # Long description - use smaller font style
            long_desc_style = ParagraphStyle(
                'LongDescription',
                parent=body_style,
                fontSize=8,
                leading=11,
                textColor=colors.HexColor('#424242')
            )
            story.append(Paragraph(f"<b>Business Description:</b>", body_style))
            story.append(Spacer(1, 0.05*inch))
            story.append(Paragraph(f"<i>{business_summary}</i>", long_desc_style))
        else:
            story.append(Paragraph(f"<b>Business Description:</b> <i>{business_summary}</i>", body_style))
    
    story.append(Spacer(1, 0.15*inch))
    
    # ===== INVESTMENT THESIS =====
    story.append(Paragraph("Investment Thesis", section_style))
    thesis_points = generator.generate_investment_thesis()
    for i, point in enumerate(thesis_points, 1):
        story.append(Paragraph(f"{i}. {point}", body_style))
    story.append(Spacer(1, 0.15*inch))
    
    # ===== WHY NOW =====
    story.append(Paragraph("Why Now?", section_style))
    catalysts = generator.generate_why_now_catalyst()
    for catalyst in catalysts:
        story.append(Paragraph(f"• {catalyst}", body_style))
    story.append(Spacer(1, 0.15*inch))
    
    # ===== KEY METRICS =====
    story.append(Paragraph("Key Metrics", section_style))
    
    # Helper to get ratio with fallback to info dict
    def get_ratio(key):
        if not generator.ratios.empty and key in generator.ratios.index:
            val = generator.ratios.loc[key].iloc[0]
            if val is not None:
                return val
        return None
    
    # Get metrics from info dict for fallback
    growth_rates = financials.get('growth_rates', {})
    
    # Extract metrics with fallbacks
    current_price = get_ratio('Current_Price') or info.get('currentPrice') or info.get('regularMarketPrice')
    pe_ratio = get_ratio('PE_Ratio') or info.get('trailingPE') or info.get('forwardPE')
    market_cap = get_ratio('Market_Cap') or info.get('marketCap')
    revenue = get_ratio('Revenue') or info.get('totalRevenue')
    
    # Revenue CAGR - check growth_rates dict first
    revenue_cagr = None
    if growth_rates:
        revenue_cagr = growth_rates.get('Total_Revenue_CAGR') or growth_rates.get('Revenue_CAGR')
        if revenue_cagr is not None and abs(revenue_cagr) > 1:
            revenue_cagr = revenue_cagr / 100  # Convert from percentage
    if revenue_cagr is None:
        revenue_cagr = info.get('revenueGrowth')
    
    roe = get_ratio('ROE') or info.get('returnOnEquity')
    roic = info.get('returnOnCapital') or info.get('returnOnAssets') or roe
    
    debt_equity = get_ratio('Debt_to_Equity') or info.get('debtToEquity')
    if debt_equity and debt_equity > 10:  # yfinance returns as percentage
        debt_equity = debt_equity / 100
    
    # FCF Yield calculation
    fcf = info.get('freeCashflow')
    fcf_yield = (fcf / market_cap * 100) if fcf and market_cap and market_cap > 0 else None
    
    # Metrics table with fallback values
    metrics_data = [
        ['Metric', 'Value'],
        ['Current Price', f"${current_price:.2f}" if current_price else "N/A"],
        ['P/E Ratio', f"{pe_ratio:.1f}x" if pe_ratio else "N/A"],
        ['Market Cap', f"${market_cap/1e9:.1f}B" if market_cap else "N/A"],
        ['Revenue (TTM)', f"${revenue/1e9:.1f}B" if revenue else "N/A"],
        ['Revenue CAGR', f"{revenue_cagr*100:.1f}%" if revenue_cagr else "N/A"],
        ['ROE', f"{roe*100:.1f}%" if roe else "N/A"],
        ['ROIC', f"{roic*100:.1f}%" if roic else "N/A"],
        ['FCF Yield', f"{fcf_yield:.1f}%" if fcf_yield else "N/A"],
        ['Debt/Equity', f"{debt_equity:.2f}x" if debt_equity is not None else "N/A"],
    ]
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e88e5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 0.15*inch))
    
    # ===== COMPARABLE VALUATION =====
    story.append(Paragraph("Comparable Valuation", section_style))
    peer_data = generator.generate_peer_comparison()
    
    comp_data = [
        ['', 'P/E', 'P/B', 'ROE', 'D/E'],
        [f'{generator.ticker}',
         f"{peer_data['company']['PE']:.1f}x" if peer_data['company']['PE'] else "N/A",
         f"{peer_data['company']['PB']:.1f}x" if peer_data['company']['PB'] else "N/A",
         f"{peer_data['company']['ROE']*100:.1f}%" if peer_data['company']['ROE'] else "N/A",
         f"{peer_data['company']['DE']:.2f}x" if peer_data['company']['DE'] is not None else "N/A"],
        ['Sector Median',
         f"{peer_data['sector']['PE']:.1f}x",
         f"{peer_data['sector']['PB']:.1f}x",
         f"{peer_data['sector']['ROE']*100:.1f}%",
         f"{peer_data['sector']['DE']:.2f}x"],
    ]
    
    comp_table = Table(comp_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e88e5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 2), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))
    
    story.append(comp_table)
    
    # Premium analysis
    if peer_data['premium']['PE']:
        pe_status = "premium" if peer_data['premium']['PE'] > 0 else "discount"
        story.append(Paragraph(
            f"<i>Trading at {abs(peer_data['premium']['PE']):.0f}% {pe_status} to sector P/E</i>",
            body_style
        ))
    
    story.append(Spacer(1, 0.15*inch))
    
    # ===== CATALYST TIMELINE =====
    story.append(Paragraph("Catalyst Timeline", section_style))
    timeline = generator.generate_catalyst_timeline()
    
    for cat in timeline:
        story.append(Paragraph(
            f"<b>{cat['quarter']}:</b> {cat['event']} <i>(+${cat['impact']:.0f} impact)</i>",
            body_style
        ))
    
    total_impact = sum([c['impact'] for c in timeline])
    current = get_ratio('Current_Price') or 0
    target = current + total_impact if current > 0 else 0
    
    if current > 0 and target > 0:
        story.append(Paragraph(
            f"<b>Path to Target:</b> ${current:.0f} → ${target:.0f} (+${total_impact:.0f})",
            body_style
        ))
    
    story.append(Spacer(1, 0.15*inch))
    
    # ===== RISK ASSESSMENT =====
    story.append(Paragraph("Risk Severity Matrix", section_style))
    risk_triage = generator.triage_red_flags()
    
    story.append(Paragraph("<b>🔴 Deal-Breakers:</b>", body_style))
    for flag in risk_triage['deal_breaker']:
        story.append(Paragraph(f"• {flag}", body_style))
    
    story.append(Paragraph("<b>🟡 Monitor:</b>", body_style))
    for flag in risk_triage['monitor']:
        story.append(Paragraph(f"• {flag}", body_style))
    
    story.append(Paragraph("<b>🟢 Manageable:</b>", body_style))
    for flag in risk_triage['manageable']:
        story.append(Paragraph(f"• {flag}", body_style))
    
    story.append(Spacer(1, 0.15*inch))
    
    # ===== THE ASK =====
    story.append(Paragraph("The Ask", section_style))
    
    valuation = generator.calculate_valuation_range()
    risk_reward = recommendation_data['risk_reward']
    
    if rec == "BUY":
        story.append(Paragraph(f"<b>Recommendation:</b> Initiate position at ${current:.0f}", body_style))
        story.append(Paragraph(f"<b>Price Target (12M):</b> ${price_target:.0f} ({upside_pct:+.0f}%)", body_style))
        story.append(Paragraph(f"<b>Entry Strategy:</b> Build over 2-3 weeks", body_style))
        story.append(Paragraph(f"<b>Stop-Loss:</b> ${valuation['bear_case']*1.05:.0f}", body_style))
        story.append(Paragraph(f"<b>Risk/Reward:</b> {risk_reward:.1f}:1", body_style))
    elif rec == "HOLD":
        story.append(Paragraph(f"<b>Recommendation:</b> Maintain position", body_style))
        story.append(Paragraph(f"<b>Price Target (12M):</b> ${price_target:.0f}", body_style))
        story.append(Paragraph(f"<b>Add Signal:</b> Below ${current*0.90:.0f}", body_style))
        story.append(Paragraph(f"<b>Trim Signal:</b> Above ${price_target:.0f}", body_style))
    else:  # SELL
        story.append(Paragraph(f"<b>Recommendation:</b> Exit position", body_style))
        story.append(Paragraph(f"<b>Price Target (12M):</b> ${price_target:.0f}", body_style))
    
    story.append(Spacer(1, 0.15*inch))
    
    # ===== COMPANY PROFILE =====
    story.append(Paragraph("Company Profile", section_style))
    
    profile_data = [
        ['Company', generator.company_name],
        ['Ticker', generator.ticker],
        ['Analysis Date', datetime.now().strftime('%Y-%m-%d')],
        ['Report Type', 'Investment Summary']
    ]
    
    profile_table = Table(profile_data, colWidths=[2*inch, 4*inch])
    profile_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e88e5')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f9f9f9')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(profile_table)
    
    # Footer
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        f"<i>Report generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
        ParagraphStyle('Footer', parent=body_style, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))
    story.append(Paragraph(
        "<i>This analysis is for informational purposes only and should not be considered investment advice.</i>",
        ParagraphStyle('Disclaimer', parent=body_style, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF data
    buffer.seek(0)
    return buffer


def generate_custom_dcf_pdf(ticker: str, company_name: str, custom_assumptions, 
                            custom_result: dict, preset_results: dict = None):
    """
    Generate PDF report for custom DCF scenario
    
    Args:
        ticker: Stock ticker
        company_name: Company name
        custom_assumptions: DCFAssumptions object
        custom_result: Result dict from calculate_dcf()
        preset_results: Optional dict with conservative/base/aggressive results
    
    Returns:
        BytesIO buffer containing the PDF
    """
    
    # Create buffer
    buffer = io.BytesIO()
    
    # Create PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1e88e5'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#1e88e5'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        textColor=colors.black
    )
    
    # Story
    story = []
    
    # Header
    story.append(Paragraph("CUSTOM DCF SCENARIO REPORT", title_style))
    story.append(Paragraph(f"{ticker} - {company_name}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Custom Assumptions Section
    story.append(Paragraph("Custom Assumptions", section_style))
    
    assumptions_data = [
        ['Parameter', 'Value'],
        ['Year 1 Growth', f"{custom_assumptions.revenue_growth_rates[0]*100:.1f}%"],
        ['Year 2 Growth', f"{custom_assumptions.revenue_growth_rates[1]*100:.1f}%"],
        ['Year 3 Growth', f"{custom_assumptions.revenue_growth_rates[2]*100:.1f}%"],
        ['Year 4 Growth', f"{custom_assumptions.revenue_growth_rates[3]*100:.1f}%"],
        ['Year 5 Growth', f"{custom_assumptions.revenue_growth_rates[4]*100:.1f}%"],
        ['Terminal Growth', f"{custom_assumptions.terminal_growth_rate*100:.1f}%"],
        ['Discount Rate (WACC)', f"{custom_assumptions.discount_rate*100:.1f}%"],
        ['Tax Rate', f"{custom_assumptions.tax_rate*100:.1f}%"],
        ['CapEx (% Revenue)', f"{custom_assumptions.capex_pct_revenue*100:.1f}%"],
        ['NWC Change (% Revenue)', f"{custom_assumptions.nwc_pct_revenue*100:.1f}%"],
        ['Depreciation (% Revenue)', f"{custom_assumptions.depreciation_pct_revenue*100:.1f}%"],
        ['Projection Years', str(custom_assumptions.projection_years)]
    ]
    
    assumptions_table = Table(assumptions_data, colWidths=[3.5*inch, 2.5*inch])
    assumptions_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e88e5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    
    story.append(assumptions_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Valuation Results
    story.append(Paragraph("Valuation Results", section_style))
    
    results_data = [
        ['Metric', 'Value'],
        ['Enterprise Value', f"${custom_result['enterprise_value']/1e9:.2f}B"],
        ['Equity Value', f"${custom_result['equity_value']/1e9:.2f}B"],
        ['Value Per Share', f"${custom_result['value_per_share']:.2f}"],
        ['PV of Cash Flows', f"${custom_result.get('pv_cash_flows', 0)/1e9:.2f}B"],
        ['PV of Terminal Value', f"${custom_result.get('pv_terminal_value', 0)/1e9:.2f}B"]
    ]
    
    results_table = Table(results_data, colWidths=[3.5*inch, 2.5*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4caf50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 1), (1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e8f5e9'), colors.white]),
    ]))
    
    story.append(results_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Comparison to Presets (if provided)
    if preset_results:
        story.append(Paragraph("Comparison to Presets", section_style))
        
        comparison_data = [
            ['Scenario', 'Value/Share', 'Enterprise Value', 'Equity Value'],
            ['Conservative', 
             f"${preset_results['conservative']['value_per_share']:.2f}",
             f"${preset_results['conservative']['enterprise_value']/1e9:.1f}B",
             f"${preset_results['conservative']['equity_value']/1e9:.1f}B"],
            ['Base Case',
             f"${preset_results['base']['value_per_share']:.2f}",
             f"${preset_results['base']['enterprise_value']/1e9:.1f}B",
             f"${preset_results['base']['equity_value']/1e9:.1f}B"],
            ['Aggressive',
             f"${preset_results['aggressive']['value_per_share']:.2f}",
             f"${preset_results['aggressive']['enterprise_value']/1e9:.1f}B",
             f"${preset_results['aggressive']['equity_value']/1e9:.1f}B"],
            ['Your Custom',
             f"${custom_result['value_per_share']:.2f}",
             f"${custom_result['enterprise_value']/1e9:.1f}B",
             f"${custom_result['equity_value']/1e9:.1f}B"]
        ]
        
        comparison_table = Table(comparison_data, colWidths=[1.5*inch, 1.5*inch, 2*inch, 1.5*inch])
        comparison_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e88e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fff3e0')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        
        story.append(comparison_table)
    
    # Footer
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        f"<i>Custom scenario generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
        ParagraphStyle('Footer', parent=body_style, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))
    story.append(Paragraph(
        "<i>This analysis is for informational purposes only and should not be considered investment advice.</i>",
        ParagraphStyle('Disclaimer', parent=body_style, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF data
    buffer.seek(0)
    return buffer

