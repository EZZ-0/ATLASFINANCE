"""
ENHANCED PDF EXPORT MODULE
===========================

Professional IC-Ready PDF Reports with Alpha Signals

Features:
- Investment Summary (existing)
- Score Dashboard with visual gauges
- Alpha Signals: Earnings Revisions, Insider Activity, Ownership
- DCF Model details
- Executive Summary (1-page)
- Chart exports

Author: ATLAS Financial Intelligence
Created: 2025-12-08 (MILESTONE-005)
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    PageBreak, Image, Flowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Wedge
from reportlab.graphics import renderPDF
from datetime import datetime
import io
import pandas as pd
import logging

logger = logging.getLogger(__name__)


# ==========================================
# CUSTOM FLOWABLES
# ==========================================

class ScoreGauge(Flowable):
    """
    Custom flowable for drawing score gauges in PDF.
    Creates a semi-circular gauge with colored segments.
    """
    
    def __init__(self, score: float, label: str, width: float = 100, height: float = 60):
        Flowable.__init__(self)
        self.score = max(0, min(100, score))  # Clamp 0-100
        self.label = label
        self.width = width
        self.height = height
    
    def draw(self):
        # Background arc (gray)
        self.canv.setStrokeColor(colors.HexColor('#e0e0e0'))
        self.canv.setLineWidth(8)
        self.canv.arc(10, 10, self.width - 10, self.height + 30, 180, 180)
        
        # Score arc (colored based on value)
        if self.score < 40:
            color = colors.HexColor('#ef4444')  # Red
        elif self.score < 70:
            color = colors.HexColor('#f59e0b')  # Orange
        else:
            color = colors.HexColor('#10b981')  # Green
        
        self.canv.setStrokeColor(color)
        angle = (self.score / 100) * 180
        self.canv.arc(10, 10, self.width - 10, self.height + 30, 180, -angle)
        
        # Score text
        self.canv.setFillColor(colors.black)
        self.canv.setFont('Helvetica-Bold', 14)
        self.canv.drawCentredString(self.width / 2, 25, f"{self.score:.0f}")
        
        # Label
        self.canv.setFont('Helvetica', 8)
        self.canv.drawCentredString(self.width / 2, 10, self.label)


class SentimentBar(Flowable):
    """
    Horizontal sentiment bar from -100 to +100.
    Used for insider sentiment, revision momentum, etc.
    """
    
    def __init__(self, value: float, label: str, width: float = 200, height: float = 30):
        Flowable.__init__(self)
        self.value = max(-100, min(100, value))  # Clamp -100 to +100
        self.label = label
        self.width = width
        self.height = height
    
    def draw(self):
        # Background bar
        self.canv.setFillColor(colors.HexColor('#f0f0f0'))
        self.canv.rect(0, 10, self.width, 15, fill=1, stroke=0)
        
        # Colored portion
        mid = self.width / 2
        if self.value >= 0:
            color = colors.HexColor('#10b981')  # Green for positive
            bar_width = (self.value / 100) * mid
            self.canv.setFillColor(color)
            self.canv.rect(mid, 10, bar_width, 15, fill=1, stroke=0)
        else:
            color = colors.HexColor('#ef4444')  # Red for negative
            bar_width = (abs(self.value) / 100) * mid
            self.canv.setFillColor(color)
            self.canv.rect(mid - bar_width, 10, bar_width, 15, fill=1, stroke=0)
        
        # Center line
        self.canv.setStrokeColor(colors.black)
        self.canv.setLineWidth(1)
        self.canv.line(mid, 8, mid, 27)
        
        # Value text
        self.canv.setFillColor(colors.black)
        self.canv.setFont('Helvetica-Bold', 10)
        self.canv.drawCentredString(self.width / 2, 30, f"{self.value:+.0f}")
        
        # Label
        self.canv.setFont('Helvetica', 8)
        self.canv.drawCentredString(self.width / 2, 0, self.label)


# ==========================================
# STYLE DEFINITIONS
# ==========================================

def get_pdf_styles():
    """Get all custom PDF styles."""
    styles = getSampleStyleSheet()
    
    custom_styles = {
        'title': ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e88e5'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ),
        'subtitle': ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=6,
            alignment=TA_CENTER
        ),
        'section': ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e88e5'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ),
        'subsection': ParagraphStyle(
            'SubSection',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#374151'),
            spaceAfter=6,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ),
        'body': ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.black
        ),
        'small': ParagraphStyle(
            'SmallText',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=4
        ),
        'footer': ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
    }
    
    return custom_styles


def get_score_color(score: float) -> colors.Color:
    """Get color based on score value (0-100)."""
    if score < 40:
        return colors.HexColor('#ef4444')  # Red
    elif score < 70:
        return colors.HexColor('#f59e0b')  # Orange
    else:
        return colors.HexColor('#10b981')  # Green


def get_sentiment_color(value: float) -> colors.Color:
    """Get color based on sentiment value (-100 to +100)."""
    if value < -20:
        return colors.HexColor('#ef4444')  # Red (bearish)
    elif value > 20:
        return colors.HexColor('#10b981')  # Green (bullish)
    else:
        return colors.HexColor('#6b7280')  # Gray (neutral)


# ==========================================
# SECTION GENERATORS
# ==========================================

def create_header_section(story: list, styles: dict, ticker: str, company_name: str, 
                          recommendation: str, price_target: float, upside_pct: float, 
                          conviction: str):
    """Create the header section with recommendation badge."""
    
    story.append(Paragraph("INVESTMENT SUMMARY", styles['title']))
    story.append(Paragraph(f"{ticker} - {company_name}", styles['subtitle']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Recommendation badge
    rec_color = (
        colors.HexColor('#10b981') if recommendation == 'BUY' else
        colors.HexColor('#ef4444') if recommendation == 'SELL' else
        colors.HexColor('#f59e0b')
    )
    
    rec_table = Table([[
        Paragraph(
            f"<b>{recommendation} | PT: ${price_target:.0f} | {upside_pct:+.0f}% | {conviction} CONVICTION</b>",
            styles['body']
        )
    ]], colWidths=[6.5 * inch])
    
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
    story.append(Spacer(1, 0.2 * inch))


def create_score_dashboard(story: list, styles: dict, scores: dict):
    """
    Create the score dashboard section.
    
    Args:
        scores: dict with keys 'conviction', 'health', 'risk_reward', 'earnings_momentum', 
                'insider_sentiment', 'institutional_accumulation'
    """
    story.append(Paragraph("Score Dashboard", styles['section']))
    
    # Primary scores (3 columns)
    primary_data = [
        ['Conviction', 'Financial Health', 'Risk/Reward'],
        [
            f"{scores.get('conviction', 50):.0f}/100",
            f"{scores.get('health', 50):.0f}/100",
            f"{scores.get('risk_reward', 50):.0f}/100"
        ],
    ]
    
    primary_table = Table(primary_data, colWidths=[2.17 * inch] * 3)
    primary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1f26')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (0, 1), get_score_color(scores.get('conviction', 50))),
        ('BACKGROUND', (1, 1), (1, 1), get_score_color(scores.get('health', 50))),
        ('BACKGROUND', (2, 1), (2, 1), get_score_color(scores.get('risk_reward', 50))),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 18),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 15),
        ('TOPPADDING', (0, 1), (-1, 1), 15),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
    ]))
    
    story.append(primary_table)
    story.append(Spacer(1, 0.15 * inch))
    
    # Alpha signals (if available)
    if any(k in scores for k in ['earnings_momentum', 'insider_sentiment', 'institutional_accumulation']):
        story.append(Paragraph("Alpha Signals", styles['subsection']))
        
        alpha_data = [
            ['Earnings Momentum', 'Insider Sentiment', 'Inst. Accumulation'],
            [
                f"{scores.get('earnings_momentum', 0):+.0f}" if scores.get('earnings_momentum') is not None else 'N/A',
                f"{scores.get('insider_sentiment', 0):+.0f}" if scores.get('insider_sentiment') is not None else 'N/A',
                f"{scores.get('institutional_accumulation', 0):+.0f}" if scores.get('institutional_accumulation') is not None else 'N/A'
            ],
        ]
        
        alpha_table = Table(alpha_data, colWidths=[2.17 * inch] * 3)
        alpha_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (0, 1), get_sentiment_color(scores.get('earnings_momentum', 0) or 0)),
            ('BACKGROUND', (1, 1), (1, 1), get_sentiment_color(scores.get('insider_sentiment', 0) or 0)),
            ('BACKGROUND', (2, 1), (2, 1), get_sentiment_color(scores.get('institutional_accumulation', 0) or 0)),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 14),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
            ('TOPPADDING', (0, 1), (-1, 1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ]))
        
        story.append(alpha_table)
    
    story.append(Spacer(1, 0.2 * inch))


def create_alpha_signals_section(story: list, styles: dict, alpha_data: dict):
    """
    Create the Alpha Signals section with earnings, insider, and ownership data.
    
    Args:
        alpha_data: dict with 'earnings', 'insider', 'ownership' sub-dicts
    """
    story.append(Paragraph("Alpha Signals", styles['section']))
    story.append(Paragraph(
        "<i>Key signals that historically predict stock outperformance</i>",
        styles['small']
    ))
    story.append(Spacer(1, 0.1 * inch))
    
    # Earnings Revisions
    if 'earnings' in alpha_data and alpha_data['earnings']:
        story.append(Paragraph("Earnings Revisions", styles['subsection']))
        earnings = alpha_data['earnings']
        
        earnings_data = [
            ['Metric', 'Value', 'Signal'],
            [
                'Momentum Score',
                f"{earnings.get('momentum_score', 0):+.0f}",
                earnings.get('trend', 'N/A')
            ],
            [
                '30-Day Revision',
                f"{earnings.get('revision_30d', 0):+.1f}%",
                '📈 Up' if earnings.get('revision_30d', 0) > 0 else '📉 Down' if earnings.get('revision_30d', 0) < 0 else '➡️ Flat'
            ],
            [
                'Analyst Count',
                str(earnings.get('analyst_count', 'N/A')),
                'High Coverage' if earnings.get('analyst_count', 0) > 20 else 'Moderate'
            ],
            [
                'Beat Rate (4Q)',
                f"{earnings.get('beat_rate', 0):.0f}%",
                '✅ Strong' if earnings.get('beat_rate', 0) > 75 else 'Average'
            ],
        ]
        
        earnings_table = Table(earnings_data, colWidths=[2 * inch, 2 * inch, 2.5 * inch])
        earnings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        story.append(earnings_table)
        story.append(Spacer(1, 0.1 * inch))
    
    # Insider Activity
    if 'insider' in alpha_data and alpha_data['insider']:
        story.append(Paragraph("Insider Transactions", styles['subsection']))
        insider = alpha_data['insider']
        
        insider_data = [
            ['Metric', 'Value', 'Signal'],
            [
                'Sentiment Score',
                f"{insider.get('sentiment_score', 0):+.0f}",
                insider.get('sentiment_label', 'N/A')
            ],
            [
                'Net Activity (90d)',
                f"${insider.get('net_value', 0)/1_000_000:.1f}M",
                '🟢 Net Buy' if insider.get('net_value', 0) > 0 else '🔴 Net Sell'
            ],
            [
                'Buy Transactions',
                str(insider.get('buy_count', 0)),
                ''
            ],
            [
                'Sell Transactions',
                str(insider.get('sell_count', 0)),
                ''
            ],
            [
                'Cluster Buying',
                'Yes' if insider.get('is_cluster', False) else 'No',
                '⭐ Bullish Signal' if insider.get('is_cluster', False) else ''
            ],
        ]
        
        insider_table = Table(insider_data, colWidths=[2 * inch, 2 * inch, 2.5 * inch])
        insider_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f3ff')]),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        story.append(insider_table)
        story.append(Spacer(1, 0.1 * inch))
    
    # Institutional Ownership
    if 'ownership' in alpha_data and alpha_data['ownership']:
        story.append(Paragraph("Institutional Ownership", styles['subsection']))
        ownership = alpha_data['ownership']
        
        ownership_data = [
            ['Metric', 'Value', 'Signal'],
            [
                'Institutional %',
                f"{ownership.get('institutional_pct', 0):.1f}%",
                'High' if ownership.get('institutional_pct', 0) > 70 else 'Moderate'
            ],
            [
                'Insider %',
                f"{ownership.get('insider_pct', 0):.1f}%",
                ''
            ],
            [
                'Top 10 Concentration',
                f"{ownership.get('top10_pct', 0):.1f}%",
                'Concentrated' if ownership.get('top10_pct', 0) > 50 else 'Diversified'
            ],
            [
                'Accumulation Score',
                f"{ownership.get('accumulation_score', 0):+.0f}",
                ownership.get('sentiment_label', 'N/A')
            ],
        ]
        
        ownership_table = Table(ownership_data, colWidths=[2 * inch, 2 * inch, 2.5 * inch])
        ownership_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        story.append(ownership_table)
    
    story.append(Spacer(1, 0.2 * inch))


def create_dcf_summary_section(story: list, styles: dict, dcf_data: dict):
    """
    Create DCF valuation summary section.
    
    Args:
        dcf_data: dict with 'conservative', 'base', 'aggressive', 'current_price', 'assumptions'
    """
    story.append(Paragraph("DCF Valuation Summary", styles['section']))
    
    # Scenario comparison table
    scenario_data = [
        ['Scenario', 'Value/Share', 'Upside/Downside'],
        [
            'Conservative',
            f"${dcf_data.get('conservative', 0):.2f}",
            f"{((dcf_data.get('conservative', 0) / dcf_data.get('current_price', 1)) - 1) * 100:+.1f}%"
        ],
        [
            'Base Case',
            f"${dcf_data.get('base', 0):.2f}",
            f"{((dcf_data.get('base', 0) / dcf_data.get('current_price', 1)) - 1) * 100:+.1f}%"
        ],
        [
            'Aggressive',
            f"${dcf_data.get('aggressive', 0):.2f}",
            f"{((dcf_data.get('aggressive', 0) / dcf_data.get('current_price', 1)) - 1) * 100:+.1f}%"
        ],
    ]
    
    scenario_table = Table(scenario_data, colWidths=[2.5 * inch, 2 * inch, 2 * inch])
    scenario_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e88e5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffebee'), colors.HexColor('#e3f2fd'), colors.HexColor('#e8f5e9')]),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(scenario_table)
    
    # Key assumptions
    if 'assumptions' in dcf_data:
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("Key Assumptions (Base Case)", styles['subsection']))
        
        assumptions = dcf_data['assumptions']
        assumptions_data = [
            ['WACC', f"{assumptions.get('wacc', 0)*100:.1f}%"],
            ['Terminal Growth', f"{assumptions.get('terminal_growth', 0)*100:.1f}%"],
            ['Revenue CAGR (5Y)', f"{assumptions.get('revenue_cagr', 0)*100:.1f}%"],
            ['EBIT Margin (Terminal)', f"{assumptions.get('ebit_margin', 0)*100:.1f}%"],
        ]
        
        assumptions_table = Table(assumptions_data, colWidths=[3.25 * inch, 3.25 * inch])
        assumptions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        story.append(assumptions_table)
    
    story.append(Spacer(1, 0.2 * inch))


def create_footer(story: list, styles: dict):
    """Add footer with timestamp and disclaimer."""
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        f"<i>Report generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
        styles['footer']
    ))
    story.append(Paragraph(
        "<i>This analysis is for informational purposes only and should not be considered investment advice.</i>",
        styles['footer']
    ))


# ==========================================
# MAIN EXPORT FUNCTIONS
# ==========================================

def generate_enhanced_ic_memo(
    ticker: str,
    company_name: str,
    recommendation_data: dict,
    scores: dict,
    alpha_data: dict = None,
    dcf_data: dict = None,
    key_metrics: dict = None,
    investment_thesis: list = None,
    catalysts: list = None,
    risks: dict = None,
    comparables: dict = None
) -> io.BytesIO:
    """
    Generate enhanced IC Memo PDF with all available data.
    
    Args:
        ticker: Stock ticker
        company_name: Company name
        recommendation_data: dict with 'recommendation', 'price_target', 'upside_pct', 'conviction'
        scores: dict with score values (0-100 or -100 to +100)
        alpha_data: Optional dict with 'earnings', 'insider', 'ownership' data
        dcf_data: Optional dict with DCF scenario values
        key_metrics: Optional dict with P/E, ROE, etc.
        investment_thesis: Optional list of thesis points
        catalysts: Optional list of catalyst dicts
        risks: Optional dict with 'deal_breaker', 'monitor', 'manageable' lists
        comparables: Optional dict with peer comparison data
    
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )
    
    styles = get_pdf_styles()
    story = []
    
    # Header with recommendation
    create_header_section(
        story, styles, ticker, company_name,
        recommendation_data.get('recommendation', 'HOLD'),
        recommendation_data.get('price_target', 0),
        recommendation_data.get('upside_pct', 0),
        recommendation_data.get('conviction', 'MEDIUM')
    )
    
    # Score Dashboard
    create_score_dashboard(story, styles, scores)
    
    # Alpha Signals (if available)
    if alpha_data:
        create_alpha_signals_section(story, styles, alpha_data)
    
    # DCF Summary (if available)
    if dcf_data:
        create_dcf_summary_section(story, styles, dcf_data)
    
    # Investment Thesis
    if investment_thesis:
        story.append(Paragraph("Investment Thesis", styles['section']))
        for i, point in enumerate(investment_thesis, 1):
            story.append(Paragraph(f"{i}. {point}", styles['body']))
        story.append(Spacer(1, 0.15 * inch))
    
    # Key Metrics
    if key_metrics:
        story.append(Paragraph("Key Metrics", styles['section']))
        
        metrics_data = [['Metric', 'Value']]
        for metric, value in key_metrics.items():
            metrics_data.append([metric, str(value)])
        
        metrics_table = Table(metrics_data, colWidths=[3.25 * inch, 3.25 * inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e88e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 0.15 * inch))
    
    # Catalysts
    if catalysts:
        story.append(Paragraph("Catalyst Timeline", styles['section']))
        for cat in catalysts:
            if isinstance(cat, dict):
                story.append(Paragraph(
                    f"<b>{cat.get('quarter', '')}:</b> {cat.get('event', '')} "
                    f"<i>(+${cat.get('impact', 0):.0f} impact)</i>",
                    styles['body']
                ))
            else:
                story.append(Paragraph(f"• {cat}", styles['body']))
        story.append(Spacer(1, 0.15 * inch))
    
    # Risk Assessment
    if risks:
        story.append(Paragraph("Risk Severity Matrix", styles['section']))
        
        if risks.get('deal_breaker'):
            story.append(Paragraph("<b>🔴 Deal-Breakers:</b>", styles['body']))
            for flag in risks['deal_breaker']:
                story.append(Paragraph(f"• {flag}", styles['body']))
        
        if risks.get('monitor'):
            story.append(Paragraph("<b>🟡 Monitor:</b>", styles['body']))
            for flag in risks['monitor']:
                story.append(Paragraph(f"• {flag}", styles['body']))
        
        if risks.get('manageable'):
            story.append(Paragraph("<b>🟢 Manageable:</b>", styles['body']))
            for flag in risks['manageable']:
                story.append(Paragraph(f"• {flag}", styles['body']))
        
        story.append(Spacer(1, 0.15 * inch))
    
    # Comparables
    if comparables:
        story.append(Paragraph("Comparable Valuation", styles['section']))
        
        comp_data = [
            ['', 'P/E', 'P/B', 'ROE', 'D/E'],
            [
                ticker,
                f"{comparables.get('company', {}).get('PE', 'N/A')}x" if comparables.get('company', {}).get('PE') else 'N/A',
                f"{comparables.get('company', {}).get('PB', 'N/A')}x" if comparables.get('company', {}).get('PB') else 'N/A',
                f"{comparables.get('company', {}).get('ROE', 0)*100:.1f}%" if comparables.get('company', {}).get('ROE') else 'N/A',
                f"{comparables.get('company', {}).get('DE', 'N/A')}x" if comparables.get('company', {}).get('DE') is not None else 'N/A',
            ],
            [
                'Sector',
                f"{comparables.get('sector', {}).get('PE', 'N/A')}x",
                f"{comparables.get('sector', {}).get('PB', 'N/A')}x",
                f"{comparables.get('sector', {}).get('ROE', 0)*100:.1f}%",
                f"{comparables.get('sector', {}).get('DE', 'N/A')}x",
            ],
        ]
        
        comp_table = Table(comp_data, colWidths=[1.5 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e88e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#e3f2fd')),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        story.append(comp_table)
        story.append(Spacer(1, 0.15 * inch))
    
    # Footer
    create_footer(story, styles)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer


def generate_executive_summary(
    ticker: str,
    company_name: str,
    recommendation: str,
    price_target: float,
    upside_pct: float,
    key_points: list,
    current_price: float
) -> io.BytesIO:
    """
    Generate a 1-page executive summary PDF.
    
    Perfect for quick sharing with busy stakeholders.
    """
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=1 * inch,
        leftMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch
    )
    
    styles = get_pdf_styles()
    story = []
    
    # Title
    story.append(Paragraph("EXECUTIVE SUMMARY", styles['title']))
    story.append(Paragraph(f"{ticker} - {company_name}", styles['subtitle']))
    story.append(Spacer(1, 0.3 * inch))
    
    # Quick recommendation box
    rec_color = (
        colors.HexColor('#10b981') if recommendation == 'BUY' else
        colors.HexColor('#ef4444') if recommendation == 'SELL' else
        colors.HexColor('#f59e0b')
    )
    
    quick_data = [
        ['RECOMMENDATION', 'PRICE TARGET', 'CURRENT', 'UPSIDE'],
        [recommendation, f"${price_target:.0f}", f"${current_price:.0f}", f"{upside_pct:+.0f}%"]
    ]
    
    quick_table = Table(quick_data, colWidths=[1.5 * inch] * 4)
    quick_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1f26')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (0, 1), rec_color),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
    ]))
    
    story.append(quick_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Key points
    story.append(Paragraph("Key Points", styles['section']))
    for point in key_points[:5]:  # Limit to 5 for 1-pager
        story.append(Paragraph(f"• {point}", styles['body']))
    
    # Footer
    create_footer(story, styles)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer


# ==========================================
# INTEGRATION HELPER
# ==========================================

def get_alpha_data_for_pdf(ticker: str) -> dict:
    """
    Fetch all alpha signals data for PDF export.
    
    Returns dict with 'earnings', 'insider', 'ownership' data.
    """
    alpha_data = {}
    
    # Try earnings revisions
    try:
        from earnings_revisions import get_earnings_revisions
        revision_summary = get_earnings_revisions(ticker)
        if revision_summary and revision_summary.status == 'success':
            alpha_data['earnings'] = {
                'momentum_score': revision_summary.momentum_score,
                'trend': revision_summary.trend.value if revision_summary.trend else 'N/A',
                'revision_30d': getattr(revision_summary, 'revision_30d_pct', 0) or 0,
                'analyst_count': revision_summary.analyst_count or 0,
                'beat_rate': (revision_summary.beat_rate or 0) * 100,
            }
    except Exception as e:
        logger.debug(f"Earnings revisions not available: {e}")
    
    # Try insider transactions
    try:
        from insider_transactions import get_insider_summary
        insider_summary = get_insider_summary(ticker)
        if insider_summary:
            alpha_data['insider'] = {
                'sentiment_score': insider_summary.sentiment_score,
                'sentiment_label': insider_summary.sentiment_label,
                'net_value': insider_summary.net_value,
                'buy_count': insider_summary.buy_transactions,
                'sell_count': insider_summary.sell_transactions,
                'is_cluster': insider_summary.is_cluster_buying,
            }
    except Exception as e:
        logger.debug(f"Insider data not available: {e}")
    
    # Try institutional ownership
    try:
        from institutional_ownership import get_ownership_summary
        ownership_summary = get_ownership_summary(ticker)
        if ownership_summary:
            alpha_data['ownership'] = {
                'institutional_pct': ownership_summary.institutional_pct,
                'insider_pct': ownership_summary.insider_pct,
                'top10_pct': ownership_summary.top10_concentration,
                'accumulation_score': ownership_summary.accumulation_score,
                'sentiment_label': ownership_summary.sentiment_label,
            }
    except Exception as e:
        logger.debug(f"Ownership data not available: {e}")
    
    return alpha_data


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCED PDF EXPORT TEST")
    print("=" * 60)
    
    # Test data
    test_recommendation = {
        'recommendation': 'BUY',
        'price_target': 250,
        'upside_pct': 35,
        'conviction': 'HIGH'
    }
    
    test_scores = {
        'conviction': 85,
        'health': 72,
        'risk_reward': 68,
        'earnings_momentum': 45,
        'insider_sentiment': -25,
        'institutional_accumulation': 15
    }
    
    test_alpha = {
        'earnings': {
            'momentum_score': 45,
            'trend': 'UP',
            'revision_30d': 3.5,
            'analyst_count': 42,
            'beat_rate': 87.5
        },
        'insider': {
            'sentiment_score': -25,
            'sentiment_label': 'Bearish',
            'net_value': -5000000,
            'buy_count': 2,
            'sell_count': 15,
            'is_cluster': False
        },
        'ownership': {
            'institutional_pct': 64.4,
            'insider_pct': 1.7,
            'top10_pct': 45.2,
            'accumulation_score': 15,
            'sentiment_label': 'Accumulating'
        }
    }
    
    # Generate test PDF
    pdf_buffer = generate_enhanced_ic_memo(
        ticker='AAPL',
        company_name='Apple Inc.',
        recommendation_data=test_recommendation,
        scores=test_scores,
        alpha_data=test_alpha,
        investment_thesis=['Strong ecosystem lock-in', 'Services growth accelerating', 'Capital return program'],
        key_metrics={'P/E': '28.5x', 'ROE': '28.5%', 'Market Cap': '$3.5T'}
    )
    
    # Save test PDF
    with open('test_enhanced_ic_memo.pdf', 'wb') as f:
        f.write(pdf_buffer.read())
    
    print("\n[OK] Test PDF generated: test_enhanced_ic_memo.pdf")
    print("=" * 60)

