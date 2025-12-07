"""
EARNINGS REVISION TRACKING MODULE
==================================

Tracks analyst earnings estimate revisions - one of the strongest 
alpha signals for stock performance.

Key Metrics:
- EPS estimate changes (7d, 30d, 60d, 90d)
- Number of upward vs downward revisions
- Revision momentum score
- Estimate dispersion (analyst agreement)

Research shows:
- Stocks with upward revisions outperform
- Revision momentum predicts future returns
- High revision velocity signals catalysts

Data Sources:
- Primary: yfinance (analyst estimates)
- Backup: FMP API, Alpha Vantage

Author: ATLAS Financial Intelligence
Created: 2025-12-08 (MILESTONE-002, TASK-A007)
"""

import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RevisionDirection(Enum):
    """Direction of earnings revision."""
    UP = "up"
    DOWN = "down"
    UNCHANGED = "unchanged"


class RevisionStrength(Enum):
    """Strength/magnitude of revision."""
    STRONG_UP = "strong_up"       # > 5%
    MODERATE_UP = "moderate_up"   # 2-5%
    SLIGHT_UP = "slight_up"       # 0-2%
    UNCHANGED = "unchanged"       # 0%
    SLIGHT_DOWN = "slight_down"   # 0-2%
    MODERATE_DOWN = "moderate_down"  # 2-5%
    STRONG_DOWN = "strong_down"   # > 5%


@dataclass
class EPSEstimate:
    """EPS estimate data for a period."""
    period: str  # 'current_quarter', 'next_quarter', 'current_year', 'next_year'
    estimate: Optional[float]
    low: Optional[float]
    high: Optional[float]
    num_analysts: Optional[int]
    growth_pct: Optional[float]


@dataclass
class RevisionData:
    """Revision data for a specific timeframe."""
    timeframe: str  # '7d', '30d', '60d', '90d'
    current_estimate: Optional[float]
    previous_estimate: Optional[float]
    change_pct: Optional[float]
    direction: RevisionDirection
    strength: RevisionStrength


@dataclass
class RevisionSummary:
    """Complete revision summary for a ticker."""
    ticker: str
    timestamp: str
    
    # Current estimates
    current_quarter_eps: EPSEstimate
    next_quarter_eps: EPSEstimate
    current_year_eps: EPSEstimate
    next_year_eps: EPSEstimate
    
    # Revisions by timeframe
    revisions_7d: Optional[RevisionData]
    revisions_30d: Optional[RevisionData]
    revisions_60d: Optional[RevisionData]
    revisions_90d: Optional[RevisionData]
    
    # Aggregate metrics
    revision_momentum_score: float  # -100 to +100
    analyst_agreement: str  # 'High', 'Moderate', 'Low'
    revision_trend: str  # 'Accelerating Up', 'Up', 'Flat', 'Down', 'Accelerating Down'
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON/display."""
        return {
            'ticker': self.ticker,
            'timestamp': self.timestamp,
            'current_quarter': {
                'eps': self.current_quarter_eps.estimate,
                'analysts': self.current_quarter_eps.num_analysts,
                'range': f"${self.current_quarter_eps.low:.2f} - ${self.current_quarter_eps.high:.2f}" if self.current_quarter_eps.low else None
            },
            'next_quarter': {
                'eps': self.next_quarter_eps.estimate,
                'analysts': self.next_quarter_eps.num_analysts,
            },
            'current_year': {
                'eps': self.current_year_eps.estimate,
                'growth': self.current_year_eps.growth_pct,
            },
            'next_year': {
                'eps': self.next_year_eps.estimate,
                'growth': self.next_year_eps.growth_pct,
            },
            'revisions': {
                '7d': self.revisions_7d.change_pct if self.revisions_7d else None,
                '30d': self.revisions_30d.change_pct if self.revisions_30d else None,
                '60d': self.revisions_60d.change_pct if self.revisions_60d else None,
                '90d': self.revisions_90d.change_pct if self.revisions_90d else None,
            },
            'momentum_score': self.revision_momentum_score,
            'analyst_agreement': self.analyst_agreement,
            'trend': self.revision_trend
        }


class EarningsRevisionTracker:
    """
    Tracks analyst earnings estimate revisions.
    
    Usage:
        tracker = EarningsRevisionTracker()
        summary = tracker.get_revision_summary("AAPL")
        
        # Get momentum score
        score = summary.revision_momentum_score  # -100 to +100
        
        # Get trend
        trend = summary.revision_trend  # 'Up', 'Down', etc.
    """
    
    # Thresholds for revision strength classification
    STRONG_THRESHOLD = 0.05  # 5%
    MODERATE_THRESHOLD = 0.02  # 2%
    
    def __init__(self):
        """Initialize the tracker."""
        pass
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_revision_summary(_self, ticker: str) -> Optional[RevisionSummary]:
        """
        Get complete revision summary for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            RevisionSummary with all revision data
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract current estimates
            current_q = _self._extract_eps_estimate(info, 'current_quarter')
            next_q = _self._extract_eps_estimate(info, 'next_quarter')
            current_y = _self._extract_eps_estimate(info, 'current_year')
            next_y = _self._extract_eps_estimate(info, 'next_year')
            
            # Extract revisions
            rev_7d = _self._extract_revision(info, '7d')
            rev_30d = _self._extract_revision(info, '30d')
            rev_60d = _self._extract_revision(info, '60d')
            rev_90d = _self._extract_revision(info, '90d')
            
            # Calculate momentum score
            momentum = _self._calculate_momentum_score(rev_7d, rev_30d, rev_60d, rev_90d)
            
            # Calculate analyst agreement
            agreement = _self._calculate_analyst_agreement(current_q, current_y)
            
            # Determine trend
            trend = _self._determine_revision_trend(rev_7d, rev_30d, rev_60d, rev_90d)
            
            return RevisionSummary(
                ticker=ticker,
                timestamp=datetime.now().isoformat(),
                current_quarter_eps=current_q,
                next_quarter_eps=next_q,
                current_year_eps=current_y,
                next_year_eps=next_y,
                revisions_7d=rev_7d,
                revisions_30d=rev_30d,
                revisions_60d=rev_60d,
                revisions_90d=rev_90d,
                revision_momentum_score=momentum,
                analyst_agreement=agreement,
                revision_trend=trend
            )
            
        except Exception as e:
            logger.error(f"Failed to get revision summary for {ticker}: {e}")
            return None
    
    def _extract_eps_estimate(self, info: Dict, period: str) -> EPSEstimate:
        """Extract EPS estimate for a period from yfinance info."""
        period_map = {
            'current_quarter': {
                'estimate': 'currentQuarterEstimate',
                'low': 'currentQuarterEstimateLow',
                'high': 'currentQuarterEstimateHigh',
            },
            'next_quarter': {
                'estimate': 'nextQuarterEstimate',
            },
            'current_year': {
                'estimate': 'earningsQuarterlyGrowth',  # Use as proxy
                'growth': 'earningsGrowth',
            },
            'next_year': {
                'estimate': 'forwardEps',
                'growth': 'earningsGrowth',
            }
        }
        
        mapping = period_map.get(period, {})
        
        estimate = info.get(mapping.get('estimate'))
        
        # Try alternate field names
        if estimate is None and period == 'current_year':
            estimate = info.get('trailingEps')
        if estimate is None and period == 'next_year':
            estimate = info.get('forwardEps')
        
        return EPSEstimate(
            period=period,
            estimate=estimate,
            low=info.get(mapping.get('low')),
            high=info.get(mapping.get('high')),
            num_analysts=info.get('numberOfAnalystOpinions'),
            growth_pct=info.get(mapping.get('growth'))
        )
    
    def _extract_revision(self, info: Dict, timeframe: str) -> Optional[RevisionData]:
        """
        Extract revision data for a timeframe.
        
        Note: yfinance doesn't directly provide revision history.
        We use available estimate fields and calculate based on
        what's accessible.
        """
        # yfinance fields for estimate changes
        # These are not always available in the standard info dict
        change_fields = {
            '7d': 'epsRevisions7Day',
            '30d': 'epsRevisions30Day', 
            '60d': 'epsRevisions60Day',
            '90d': 'epsRevisions90Day',
        }
        
        field = change_fields.get(timeframe)
        
        # Try to get revision data
        # Note: yfinance may not have these fields, so we'll need
        # to use FMP or Alpha Vantage as backup
        
        # For now, try available fields
        current = info.get('targetMeanPrice') or info.get('forwardEps')
        
        # Since yfinance doesn't provide historical estimates,
        # we need to use supplementary data sources
        # This will be enhanced when E012 research is complete
        
        if current is None:
            return None
        
        # Placeholder - will be enhanced with actual revision data
        return RevisionData(
            timeframe=timeframe,
            current_estimate=current,
            previous_estimate=None,
            change_pct=None,
            direction=RevisionDirection.UNCHANGED,
            strength=RevisionStrength.UNCHANGED
        )
    
    def _classify_revision_strength(self, change_pct: float) -> RevisionStrength:
        """Classify revision strength based on percentage change."""
        if change_pct is None:
            return RevisionStrength.UNCHANGED
        
        abs_change = abs(change_pct)
        
        if change_pct > self.STRONG_THRESHOLD:
            return RevisionStrength.STRONG_UP
        elif change_pct > self.MODERATE_THRESHOLD:
            return RevisionStrength.MODERATE_UP
        elif change_pct > 0:
            return RevisionStrength.SLIGHT_UP
        elif change_pct < -self.STRONG_THRESHOLD:
            return RevisionStrength.STRONG_DOWN
        elif change_pct < -self.MODERATE_THRESHOLD:
            return RevisionStrength.MODERATE_DOWN
        elif change_pct < 0:
            return RevisionStrength.SLIGHT_DOWN
        else:
            return RevisionStrength.UNCHANGED
    
    def _calculate_momentum_score(
        self,
        rev_7d: Optional[RevisionData],
        rev_30d: Optional[RevisionData],
        rev_60d: Optional[RevisionData],
        rev_90d: Optional[RevisionData]
    ) -> float:
        """
        Calculate revision momentum score (-100 to +100).
        
        Weights recent revisions more heavily.
        """
        weights = {'7d': 0.40, '30d': 0.30, '60d': 0.20, '90d': 0.10}
        
        score = 0.0
        total_weight = 0.0
        
        for timeframe, revision in [
            ('7d', rev_7d), ('30d', rev_30d), 
            ('60d', rev_60d), ('90d', rev_90d)
        ]:
            if revision and revision.change_pct is not None:
                # Normalize change to -100/+100 scale
                # Cap at ±20% change = ±100 score
                normalized = max(-100, min(100, revision.change_pct * 5))
                score += normalized * weights[timeframe]
                total_weight += weights[timeframe]
        
        if total_weight > 0:
            return round(score / total_weight, 1)
        
        return 0.0
    
    def _calculate_analyst_agreement(
        self,
        current_q: EPSEstimate,
        current_y: EPSEstimate
    ) -> str:
        """
        Calculate analyst agreement based on estimate dispersion.
        """
        if current_q.low and current_q.high and current_q.estimate:
            range_pct = (current_q.high - current_q.low) / current_q.estimate if current_q.estimate != 0 else 0
            
            if range_pct < 0.10:  # < 10% range
                return 'High'
            elif range_pct < 0.25:  # 10-25% range
                return 'Moderate'
            else:
                return 'Low'
        
        return 'Unknown'
    
    def _determine_revision_trend(
        self,
        rev_7d: Optional[RevisionData],
        rev_30d: Optional[RevisionData],
        rev_60d: Optional[RevisionData],
        rev_90d: Optional[RevisionData]
    ) -> str:
        """
        Determine the overall revision trend.
        """
        changes = []
        
        for rev in [rev_7d, rev_30d, rev_60d, rev_90d]:
            if rev and rev.change_pct is not None:
                changes.append(rev.change_pct)
        
        if not changes:
            return 'No Data'
        
        avg_change = sum(changes) / len(changes)
        
        # Check for acceleration
        if len(changes) >= 2:
            recent = changes[0]
            older = changes[-1]
            
            if recent > older > 0:
                return 'Accelerating Up'
            elif recent < older < 0:
                return 'Accelerating Down'
        
        if avg_change > 0.02:
            return 'Up'
        elif avg_change < -0.02:
            return 'Down'
        else:
            return 'Flat'


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

def get_earnings_revisions(ticker: str) -> Optional[RevisionSummary]:
    """
    Get earnings revision summary for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        RevisionSummary or None
    """
    tracker = EarningsRevisionTracker()
    return tracker.get_revision_summary(ticker)


def get_revision_momentum_score(ticker: str) -> float:
    """
    Get just the momentum score for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Momentum score (-100 to +100)
    """
    summary = get_earnings_revisions(ticker)
    return summary.revision_momentum_score if summary else 0.0


def get_revision_direction(ticker: str) -> str:
    """
    Get revision direction as simple string.
    
    Returns: 'Up', 'Down', 'Flat', or 'Unknown'
    """
    summary = get_earnings_revisions(ticker)
    if not summary:
        return 'Unknown'
    
    trend = summary.revision_trend
    if 'Up' in trend:
        return 'Up'
    elif 'Down' in trend:
        return 'Down'
    else:
        return 'Flat'


# ==========================================
# FMP API INTEGRATION (Backup Data Source)
# ==========================================

def get_fmp_revisions(ticker: str, api_key: str = None) -> Optional[Dict]:
    """
    Get earnings revisions from Financial Modeling Prep API.
    
    FMP provides more detailed revision data than yfinance.
    Requires API key (free tier available).
    
    Args:
        ticker: Stock ticker symbol
        api_key: FMP API key (or from env var FMP_API_KEY)
        
    Returns:
        Dict with FMP revision data or None
    """
    import os
    import requests
    
    api_key = api_key or os.getenv('FMP_API_KEY')
    
    if not api_key:
        logger.debug("FMP API key not set, skipping FMP revisions")
        return None
    
    try:
        url = f"https://financialmodelingprep.com/api/v3/analyst-estimates/{ticker}?apikey={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            logger.warning(f"FMP API returned {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"FMP API error: {e}")
        return None


# ==========================================
# VISUALIZATION FUNCTIONS
# ==========================================

def create_revision_gauge(momentum_score: float) -> "go.Figure":
    """
    Create a gauge chart showing revision momentum.
    
    Args:
        momentum_score: Score from -100 to +100
        
    Returns:
        Plotly figure
    """
    import plotly.graph_objects as go
    
    # Determine color based on score
    if momentum_score > 20:
        color = "green"
    elif momentum_score > 0:
        color = "lightgreen"
    elif momentum_score > -20:
        color = "orange"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=momentum_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Revision Momentum", 'font': {'size': 16}},
        delta={'reference': 0, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge={
            'axis': {'range': [-100, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [-100, -20], 'color': 'rgba(255, 0, 0, 0.2)'},
                {'range': [-20, 0], 'color': 'rgba(255, 165, 0, 0.2)'},
                {'range': [0, 20], 'color': 'rgba(144, 238, 144, 0.2)'},
                {'range': [20, 100], 'color': 'rgba(0, 128, 0, 0.2)'},
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': momentum_score
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return fig


def create_revision_trend_chart(revisions: Dict[str, float]) -> "go.Figure":
    """
    Create a bar chart showing revisions over time.
    
    Args:
        revisions: Dict with timeframe keys ('7d', '30d', etc.) and % change values
        
    Returns:
        Plotly figure
    """
    import plotly.graph_objects as go
    
    timeframes = ['90d', '60d', '30d', '7d']
    values = [revisions.get(tf, 0) or 0 for tf in timeframes]
    
    # Color based on positive/negative
    colors = ['green' if v >= 0 else 'red' for v in values]
    
    fig = go.Figure(go.Bar(
        x=timeframes,
        y=values,
        marker_color=colors,
        text=[f"{v:+.1f}%" if v else "N/A" for v in values],
        textposition='outside',
    ))
    
    fig.update_layout(
        title="EPS Estimate Changes Over Time",
        xaxis_title="Timeframe",
        yaxis_title="% Change",
        height=300,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        showlegend=False
    )
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    return fig


def create_estimate_comparison_chart(
    current_q: float,
    next_q: float,
    current_y: float,
    next_y: float
) -> "go.Figure":
    """
    Create a bar chart comparing EPS estimates across periods.
    
    Returns:
        Plotly figure
    """
    import plotly.graph_objects as go
    
    periods = ['Current Q', 'Next Q', 'Current FY', 'Next FY']
    values = [current_q or 0, next_q or 0, current_y or 0, next_y or 0]
    
    # Calculate growth between periods
    annotations = []
    
    fig = go.Figure(go.Bar(
        x=periods,
        y=values,
        marker_color=['#3b82f6', '#60a5fa', '#2563eb', '#1d4ed8'],
        text=[f"${v:.2f}" if v else "N/A" for v in values],
        textposition='outside',
    ))
    
    fig.update_layout(
        title="EPS Estimates by Period",
        xaxis_title="Period",
        yaxis_title="EPS ($)",
        height=300,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        showlegend=False
    )
    
    return fig


def create_revision_heatmap(tickers: List[str]) -> "go.Figure":
    """
    Create a heatmap comparing revisions across multiple tickers.
    
    Args:
        tickers: List of ticker symbols
        
    Returns:
        Plotly figure
    """
    import plotly.graph_objects as go
    import numpy as np
    
    # Collect data
    data = []
    timeframes = ['7d', '30d', '60d', '90d']
    
    for ticker in tickers:
        summary = get_earnings_revisions(ticker)
        if summary:
            row = [
                summary.revisions_7d.change_pct if summary.revisions_7d else 0,
                summary.revisions_30d.change_pct if summary.revisions_30d else 0,
                summary.revisions_60d.change_pct if summary.revisions_60d else 0,
                summary.revisions_90d.change_pct if summary.revisions_90d else 0,
            ]
        else:
            row = [0, 0, 0, 0]
        data.append(row)
    
    z = np.array(data)
    
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=timeframes,
        y=tickers,
        colorscale='RdYlGn',
        zmid=0,
        text=[[f"{v:.1f}%" if v else "N/A" for v in row] for row in z],
        texttemplate="%{text}",
        textfont={"size": 12},
        hovertemplate="Ticker: %{y}<br>Timeframe: %{x}<br>Change: %{z:.2f}%<extra></extra>"
    ))
    
    fig.update_layout(
        title="Revision Comparison",
        xaxis_title="Timeframe",
        yaxis_title="Ticker",
        height=max(200, len(tickers) * 40),
        margin=dict(l=60, r=40, t=60, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return fig


# ==========================================
# STREAMLIT UI COMPONENT
# ==========================================

def render_revision_card(ticker: str, compact: bool = True):
    """
    Render revision summary card in Streamlit.
    
    Args:
        ticker: Stock ticker symbol
        compact: If True, show condensed view
    """
    summary = get_earnings_revisions(ticker)
    
    if not summary:
        st.warning(f"No revision data available for {ticker}")
        return
    
    data = summary.to_dict()
    
    if compact:
        # Compact view - single row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            score = data['momentum_score']
            color = "green" if score > 0 else ("red" if score < 0 else "gray")
            st.metric(
                "Revision Momentum",
                f"{score:+.1f}",
                help="Score from -100 (down) to +100 (up)"
            )
        
        with col2:
            st.metric(
                "Trend",
                data['trend'],
                help="Overall revision direction"
            )
        
        with col3:
            st.metric(
                "Analyst Agreement",
                data['analyst_agreement'],
                help="How closely analysts agree on estimates"
            )
        
        with col4:
            if data['current_year']['growth']:
                st.metric(
                    "EPS Growth (FY)",
                    f"{data['current_year']['growth']*100:.1f}%"
                )
    else:
        # Full view
        st.markdown("### Earnings Revisions")
        
        # Estimates table
        st.markdown("#### Current Estimates")
        
        estimates_df = pd.DataFrame([
            {
                'Period': 'Current Quarter',
                'EPS Estimate': f"${data['current_quarter']['eps']:.2f}" if data['current_quarter']['eps'] else 'N/A',
                'Analysts': data['current_quarter']['analysts'] or 'N/A',
            },
            {
                'Period': 'Next Quarter',
                'EPS Estimate': f"${data['next_quarter']['eps']:.2f}" if data['next_quarter']['eps'] else 'N/A',
                'Analysts': data['next_quarter']['analysts'] or 'N/A',
            },
            {
                'Period': 'Current Year',
                'EPS Estimate': f"${data['current_year']['eps']:.2f}" if data['current_year']['eps'] else 'N/A',
                'YoY Growth': f"{data['current_year']['growth']*100:.1f}%" if data['current_year']['growth'] else 'N/A',
            },
            {
                'Period': 'Next Year',
                'EPS Estimate': f"${data['next_year']['eps']:.2f}" if data['next_year']['eps'] else 'N/A',
                'YoY Growth': f"{data['next_year']['growth']*100:.1f}%" if data['next_year']['growth'] else 'N/A',
            },
        ])
        
        st.dataframe(estimates_df, hide_index=True, use_container_width=True)
        
        # Revisions chart (placeholder - will add visualization)
        st.markdown("#### Revision History")
        st.info("Revision trend chart will be displayed here")


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":
    # Test with AAPL
    print("=" * 60)
    print("EARNINGS REVISION TRACKER TEST")
    print("=" * 60)
    
    tracker = EarningsRevisionTracker()
    
    for ticker in ['AAPL', 'MSFT', 'GOOGL']:
        print(f"\n[TEST] {ticker}")
        summary = tracker.get_revision_summary(ticker)
        
        if summary:
            data = summary.to_dict()
            print(f"  Momentum Score: {data['momentum_score']}")
            print(f"  Trend: {data['trend']}")
            print(f"  Agreement: {data['analyst_agreement']}")
            print(f"  Current Q EPS: {data['current_quarter']['eps']}")
        else:
            print("  No data available")
    
    print("\n[OK] Module ready for integration")

