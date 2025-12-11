"""
INSTITUTIONAL OWNERSHIP MODULE
==============================

Tracks institutional investor ownership - a key signal for "smart money" activity.

Why Institutional Ownership Matters:
- Institutions do deep research before buying
- Rising institutional ownership = accumulation
- Falling ownership = distribution
- Top holder changes signal major shifts

Data Sources:
- Primary: yfinance (institutional_holders, major_holders)
- Backup: SEC 13F filings (quarterly)
- Tertiary: WhaleWisdom, Fintel

Key Metrics:
- Total institutional ownership %
- Change in ownership (QoQ)
- Top 10 holders
- New positions / exits
- Concentrated vs distributed ownership

Author: ATLAS Financial Intelligence
Created: 2025-12-08 (MILESTONE-004, TASK-A015)
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import yfinance as yf

# Import centralized cache to prevent Yahoo rate limiting
from utils.ticker_cache import get_ticker_info, get_ticker

logger = logging.getLogger(__name__)


class HolderType(Enum):
    """Type of institutional holder."""
    MUTUAL_FUND = "Mutual Fund"
    HEDGE_FUND = "Hedge Fund"
    PENSION = "Pension Fund"
    INSURANCE = "Insurance Company"
    BANK = "Bank"
    INVESTMENT_ADVISOR = "Investment Advisor"
    SOVEREIGN = "Sovereign Wealth Fund"
    ETF = "ETF"
    OTHER = "Other"


@dataclass
class InstitutionalHolder:
    """Single institutional holder record."""
    name: str
    shares: int
    value: float
    percent_held: float
    date_reported: Optional[datetime] = None
    change_shares: Optional[int] = None  # Change from previous quarter
    change_percent: Optional[float] = None
    holder_type: HolderType = HolderType.OTHER
    
    @property
    def is_new_position(self) -> bool:
        """True if this is a new position (no prior holding)."""
        return self.change_shares is not None and self.change_shares == self.shares
    
    @property
    def is_increased(self) -> bool:
        """True if position was increased."""
        return self.change_shares is not None and self.change_shares > 0
    
    @property
    def is_decreased(self) -> bool:
        """True if position was decreased."""
        return self.change_shares is not None and self.change_shares < 0
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'shares': self.shares,
            'value': self.value,
            'percent': self.percent_held,
            'change_shares': self.change_shares,
            'change_pct': self.change_percent,
            'type': self.holder_type.value
        }


@dataclass
class OwnershipSummary:
    """Aggregated institutional ownership summary."""
    ticker: str
    timestamp: str
    
    # Ownership percentages
    institutional_pct: float = 0.0
    insider_pct: float = 0.0
    retail_pct: float = 0.0  # Calculated as 100 - inst - insider
    
    # Share counts
    shares_outstanding: int = 0
    institutional_shares: int = 0
    insider_shares: int = 0
    
    # Holder counts
    total_institutions: int = 0
    
    # Top holders
    top_holders: List[InstitutionalHolder] = field(default_factory=list)
    
    # Change metrics (vs previous quarter)
    ownership_change_pct: Optional[float] = None
    new_positions: int = 0
    increased_positions: int = 0
    decreased_positions: int = 0
    exited_positions: int = 0
    
    # Concentration metrics
    top10_concentration: float = 0.0  # % held by top 10
    is_concentrated: bool = False  # Top 10 > 50%
    
    # Sentiment
    accumulation_score: float = 0.0  # -100 to +100
    sentiment_label: str = "Neutral"
    
    def to_dict(self) -> Dict:
        return {
            'ticker': self.ticker,
            'timestamp': self.timestamp,
            'ownership': {
                'institutional': self.institutional_pct,
                'insider': self.insider_pct,
                'retail': self.retail_pct
            },
            'shares': {
                'outstanding': self.shares_outstanding,
                'institutional': self.institutional_shares,
                'insider': self.insider_shares
            },
            'institutions': {
                'total': self.total_institutions,
                'new': self.new_positions,
                'increased': self.increased_positions,
                'decreased': self.decreased_positions,
                'exited': self.exited_positions
            },
            'concentration': {
                'top10_pct': self.top10_concentration,
                'is_concentrated': self.is_concentrated
            },
            'sentiment': {
                'score': self.accumulation_score,
                'label': self.sentiment_label
            },
            'top_holders': [h.to_dict() for h in self.top_holders[:10]]
        }


class InstitutionalOwnershipTracker:
    """
    Tracks institutional ownership and accumulation/distribution.
    
    Usage:
        tracker = InstitutionalOwnershipTracker()
        summary = tracker.get_ownership_summary("AAPL")
        
        # Check accumulation
        if summary.accumulation_score > 30:
            print("Institutions are accumulating!")
        
        # Check concentration
        if summary.is_concentrated:
            print("Ownership is highly concentrated in top 10")
    """
    
    def __init__(self):
        """Initialize the tracker."""
        pass
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_ownership_summary(_self, ticker: str) -> Optional[OwnershipSummary]:
        """
        Get institutional ownership summary for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            OwnershipSummary with all metrics
        """
        try:
            # Use centralized cache to prevent Yahoo rate limiting
            info = get_ticker_info(ticker)
            stock = get_ticker(ticker)
            
            # Get holder data (requires Ticker object)
            inst_holders = stock.institutional_holders
            major_holders = stock.major_holders
            
            summary = OwnershipSummary(
                ticker=ticker,
                timestamp=datetime.now().isoformat()
            )
            
            # Parse major holders (ownership percentages)
            if major_holders is not None and not major_holders.empty:
                summary = _self._parse_major_holders(summary, major_holders)
            else:
                # Fallback to info dict
                summary.institutional_pct = info.get('heldPercentInstitutions', 0) * 100
                summary.insider_pct = info.get('heldPercentInsiders', 0) * 100
            
            # Calculate retail (remainder)
            summary.retail_pct = max(0, 100 - summary.institutional_pct - summary.insider_pct)
            
            # Get share counts
            summary.shares_outstanding = info.get('sharesOutstanding', 0)
            summary.institutional_shares = int(summary.shares_outstanding * summary.institutional_pct / 100)
            summary.insider_shares = int(summary.shares_outstanding * summary.insider_pct / 100)
            
            # Parse institutional holders
            if inst_holders is not None and not inst_holders.empty:
                summary = _self._parse_institutional_holders(summary, inst_holders)
            
            # Calculate concentration
            summary = _self._calculate_concentration(summary)
            
            # Calculate accumulation score
            summary = _self._calculate_accumulation_score(summary)
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get ownership summary for {ticker}: {e}")
            return None
    
    def _parse_major_holders(
        self, 
        summary: OwnershipSummary, 
        major_holders: pd.DataFrame
    ) -> OwnershipSummary:
        """
        Parse major holders DataFrame.
        
        yfinance returns DataFrame with index like:
        - 'insidersPercentHeld'
        - 'institutionsPercentHeld'
        - 'institutionsFloatPercentHeld'
        - 'institutionsCount'
        
        Fixed: 2025-12-08 (TASK-A018 - Bug fix from E018 validation)
        """
        try:
            # New format: yfinance returns DataFrame with metric names as index
            if hasattr(major_holders, 'index'):
                # Check for new yfinance format (index-based)
                if 'institutionsPercentHeld' in major_holders.index:
                    # Index-based access (new yfinance format)
                    if 'Value' in major_holders.columns:
                        inst_val = major_holders.loc['institutionsPercentHeld', 'Value']
                        if inst_val is not None:
                            summary.institutional_pct = float(inst_val) * 100
                    
                    if 'insidersPercentHeld' in major_holders.index:
                        ins_val = major_holders.loc['insidersPercentHeld', 'Value']
                        if ins_val is not None:
                            summary.insider_pct = float(ins_val) * 100
                    
                    if 'institutionsCount' in major_holders.index:
                        count_val = major_holders.loc['institutionsCount', 'Value']
                        if count_val is not None:
                            summary.total_institutions = int(count_val)
                
                else:
                    # Fallback: Old format with [value, description] rows
                    for _, row in major_holders.iterrows():
                        if len(row) >= 2:
                            value = row.iloc[0]
                            desc = str(row.iloc[1]).lower()
                            
                            # Parse percentage (could be string like "5.50%")
                            if isinstance(value, str):
                                value = float(value.replace('%', ''))
                            else:
                                value = float(value) * 100 if value < 1 else float(value)
                            
                            if 'institution' in desc:
                                summary.institutional_pct = value
                            elif 'insider' in desc:
                                summary.insider_pct = value
                    
        except Exception as e:
            logger.debug(f"Error parsing major holders: {e}")
        
        return summary
    
    def _parse_institutional_holders(
        self, 
        summary: OwnershipSummary, 
        inst_holders: pd.DataFrame
    ) -> OwnershipSummary:
        """
        Parse institutional holders DataFrame.
        
        Updated: 2025-12-08 (TASK-A018 - Added pctChange extraction per E021)
        Fixed: 2025-12-08 - Fixed percent_held extraction to handle multiple column names
        """
        try:
            holders = []
            total_pct_change = 0
            change_count = 0
            
            # Debug: Log available columns
            logger.debug(f"Institutional holders columns: {inst_holders.columns.tolist()}")
            
            for _, row in inst_holders.iterrows():
                # Extract pctChange if available (key insight from E020/E021)
                pct_change = None
                if 'pctChange' in row and row['pctChange'] is not None:
                    try:
                        pct_change = float(row['pctChange']) * 100  # Convert to percentage
                        total_pct_change += pct_change
                        change_count += 1
                    except:
                        pass
                
                # Try multiple column names for percentage held
                pct_held = 0.0
                for col_name in ['% Out', 'pctHeld', 'Percent Out', 'percentOut', 'pct_out']:
                    if col_name in row and row[col_name] is not None:
                        try:
                            pct_val = float(row[col_name])
                            # Convert decimal to percentage if needed
                            if pct_val > 0 and pct_val < 1:
                                pct_held = pct_val * 100
                            else:
                                pct_held = pct_val
                            break
                        except (ValueError, TypeError):
                            continue
                
                # If still 0 and we have shares and outstanding, calculate manually
                if pct_held == 0 and summary.shares_outstanding > 0:
                    shares = int(row.get('Shares', 0) or 0)
                    if shares > 0:
                        pct_held = (shares / summary.shares_outstanding) * 100
                
                holder = InstitutionalHolder(
                    name=str(row.get('Holder', 'Unknown')),
                    shares=int(row.get('Shares', 0) or 0),
                    value=float(row.get('Value', 0) or 0),
                    percent_held=pct_held,
                    date_reported=pd.to_datetime(row.get('Date Reported')) if 'Date Reported' in row else None,
                    holder_type=self._classify_holder(str(row.get('Holder', ''))),
                    change_percent=pct_change
                )
                holders.append(holder)
            
            summary.top_holders = holders
            summary.total_institutions = len(holders) if not summary.total_institutions else summary.total_institutions
            
            # Store average pct change for accumulation calculation
            if change_count > 0:
                summary._avg_holder_change = total_pct_change / change_count
            
        except Exception as e:
            logger.debug(f"Error parsing institutional holders: {e}")
        
        return summary
    
    def _classify_holder(self, name: str) -> HolderType:
        """Classify holder type based on name."""
        name_upper = name.upper()
        
        if 'VANGUARD' in name_upper or 'BLACKROCK' in name_upper or 'STATE STREET' in name_upper:
            return HolderType.ETF  # These are primarily ETF providers
        elif 'FIDELITY' in name_upper or 'T. ROWE' in name_upper or 'CAPITAL' in name_upper:
            return HolderType.MUTUAL_FUND
        elif 'HEDGE' in name_upper or 'CITADEL' in name_upper or 'RENAISSANCE' in name_upper:
            return HolderType.HEDGE_FUND
        elif 'PENSION' in name_upper or 'RETIREMENT' in name_upper:
            return HolderType.PENSION
        elif 'BANK' in name_upper or 'MORGAN' in name_upper or 'GOLDMAN' in name_upper:
            return HolderType.BANK
        elif 'INSURANCE' in name_upper or 'LIFE' in name_upper:
            return HolderType.INSURANCE
        else:
            return HolderType.INVESTMENT_ADVISOR
    
    def _calculate_concentration(self, summary: OwnershipSummary) -> OwnershipSummary:
        """Calculate ownership concentration metrics."""
        if not summary.top_holders:
            return summary
        
        # Top 10 concentration
        top10 = summary.top_holders[:10]
        summary.top10_concentration = sum(h.percent_held for h in top10)
        summary.is_concentrated = summary.top10_concentration > 50
        
        return summary
    
    def _calculate_accumulation_score(self, summary: OwnershipSummary) -> OwnershipSummary:
        """
        Calculate accumulation/distribution score (-100 to +100).
        
        Positive = accumulation (institutions buying)
        Negative = distribution (institutions selling)
        """
        score = 0.0
        
        # High institutional ownership is a positive sign
        if summary.institutional_pct > 80:
            score += 20
        elif summary.institutional_pct > 60:
            score += 10
        elif summary.institutional_pct < 20:
            score -= 20
        
        # Position changes
        if summary.new_positions > summary.exited_positions:
            score += 20
        elif summary.exited_positions > summary.new_positions:
            score -= 20
        
        if summary.increased_positions > summary.decreased_positions:
            score += 15
        elif summary.decreased_positions > summary.increased_positions:
            score -= 15
        
        # Cap at -100 to +100
        score = max(-100, min(100, score))
        
        summary.accumulation_score = round(score, 1)
        
        # Set label
        if score >= 40:
            summary.sentiment_label = "Strong Accumulation"
        elif score >= 15:
            summary.sentiment_label = "Accumulation"
        elif score >= -15:
            summary.sentiment_label = "Neutral"
        elif score >= -40:
            summary.sentiment_label = "Distribution"
        else:
            summary.sentiment_label = "Strong Distribution"
        
        return summary


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

def get_ownership_summary(ticker: str) -> Optional[OwnershipSummary]:
    """
    Get institutional ownership summary for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        OwnershipSummary or None
    """
    tracker = InstitutionalOwnershipTracker()
    return tracker.get_ownership_summary(ticker)


def get_institutional_pct(ticker: str) -> float:
    """Get institutional ownership percentage."""
    summary = get_ownership_summary(ticker)
    return summary.institutional_pct if summary else 0.0


def get_top_holders(ticker: str, limit: int = 10) -> List[InstitutionalHolder]:
    """Get top institutional holders."""
    summary = get_ownership_summary(ticker)
    return summary.top_holders[:limit] if summary else []


def is_heavily_institutional(ticker: str, threshold: float = 70.0) -> bool:
    """Check if stock is heavily owned by institutions."""
    return get_institutional_pct(ticker) > threshold


# ==========================================
# VISUALIZATION FUNCTIONS
# ==========================================

def create_ownership_pie(summary: OwnershipSummary) -> "go.Figure":
    """Create a pie chart showing ownership breakdown."""
    import plotly.graph_objects as go
    
    labels = ['Institutional', 'Insider', 'Retail/Other']
    values = [summary.institutional_pct, summary.insider_pct, summary.retail_pct]
    colors = ['#3b82f6', '#10b981', '#6b7280']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='percent+label',
        textposition='outside'
    )])
    
    fig.update_layout(
        title="Ownership Breakdown",
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        showlegend=False
    )
    
    return fig


def create_top_holders_chart(holders: List[InstitutionalHolder], limit: int = 10) -> "go.Figure":
    """Create a horizontal bar chart of top holders."""
    import plotly.graph_objects as go
    
    if not holders:
        return None
    
    holders = holders[:limit]
    
    names = [h.name[:30] + '...' if len(h.name) > 30 else h.name for h in reversed(holders)]
    values = [h.percent_held for h in reversed(holders)]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=names,
        orientation='h',
        marker_color='#3b82f6',
        text=[f"{v:.1f}%" for v in values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Top Institutional Holders",
        xaxis_title="% Ownership",
        height=max(300, len(holders) * 35),
        margin=dict(l=200, r=50, t=50, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return fig


def create_accumulation_gauge(score: float) -> "go.Figure":
    """Create a gauge showing accumulation/distribution."""
    import plotly.graph_objects as go
    
    if score > 30:
        color = "green"
    elif score > 0:
        color = "lightgreen"
    elif score > -30:
        color = "orange"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Accumulation Score", 'font': {'size': 16}},
        gauge={
            'axis': {'range': [-100, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [-100, -30], 'color': 'rgba(255, 0, 0, 0.2)'},
                {'range': [-30, 0], 'color': 'rgba(255, 165, 0, 0.2)'},
                {'range': [0, 30], 'color': 'rgba(144, 238, 144, 0.2)'},
                {'range': [30, 100], 'color': 'rgba(0, 128, 0, 0.2)'},
            ]
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return fig


# ==========================================
# STREAMLIT UI COMPONENT
# ==========================================

def render_ownership_card(ticker: str, compact: bool = True):
    """
    Render institutional ownership card in Streamlit.
    
    Args:
        ticker: Stock ticker symbol
        compact: If True, show condensed view
    """
    summary = get_ownership_summary(ticker)
    
    if not summary:
        st.warning(f"No ownership data available for {ticker}")
        return
    
    if compact:
        # Compact view - single row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Institutional",
                f"{summary.institutional_pct:.1f}%",
                help="Percentage owned by institutions"
            )
        
        with col2:
            st.metric(
                "Insider",
                f"{summary.insider_pct:.1f}%",
                help="Percentage owned by insiders"
            )
        
        with col3:
            st.metric(
                "Concentration",
                f"{summary.top10_concentration:.1f}%",
                help="Percentage held by top 10 institutions"
            )
        
        with col4:
            st.metric(
                "Signal",
                summary.sentiment_label,
                help=f"Accumulation score: {summary.accumulation_score}"
            )
    else:
        # Full view
        st.markdown("### Institutional Ownership")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Institutional", f"{summary.institutional_pct:.1f}%")
        with col2:
            st.metric("Insider", f"{summary.insider_pct:.1f}%")
        with col3:
            st.metric("Retail/Other", f"{summary.retail_pct:.1f}%")
        with col4:
            st.metric("# Institutions", summary.total_institutions)
        
        # Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.plotly_chart(create_ownership_pie(summary), use_container_width=True)
        
        with chart_col2:
            st.plotly_chart(create_accumulation_gauge(summary.accumulation_score), use_container_width=True)
        
        # Top holders table
        if summary.top_holders:
            st.markdown("#### Top Institutional Holders")
            
            holders_data = [{
                'Holder': h.name,
                'Shares': f"{h.shares:,}",
                'Value': f"${h.value/1_000_000:.1f}M" if h.value >= 1_000_000 else f"${h.value:,.0f}",
                '% Owned': f"{h.percent_held:.2f}%",
                'Type': h.holder_type.value
            } for h in summary.top_holders[:10]]
            
            st.dataframe(pd.DataFrame(holders_data), hide_index=True, use_container_width=True)


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("INSTITUTIONAL OWNERSHIP TRACKER TEST")
    print("=" * 60)
    
    tracker = InstitutionalOwnershipTracker()
    
    for ticker in ['AAPL', 'MSFT', 'TSLA']:
        print(f"\n[TEST] {ticker}")
        summary = tracker.get_ownership_summary(ticker)
        
        if summary:
            data = summary.to_dict()
            print(f"  Institutional: {data['ownership']['institutional']:.1f}%")
            print(f"  Insider: {data['ownership']['insider']:.1f}%")
            print(f"  Retail: {data['ownership']['retail']:.1f}%")
            print(f"  Top 10 Concentration: {data['concentration']['top10_pct']:.1f}%")
            print(f"  Accumulation: {data['sentiment']['score']} ({data['sentiment']['label']})")
            print(f"  # Institutions: {data['institutions']['total']}")
        else:
            print("  No data available")
    
    print("\n[OK] Module ready for integration")

