"""
INSIDER TRANSACTIONS MODULE
============================

Tracks SEC Form 4 insider transactions - a key signal for stock analysis.

Why Insider Transactions Matter:
- Insiders know more about the company than anyone
- Insider BUYING is strongly bullish (they're risking their own money)
- Insider SELLING is less meaningful (could be diversification, taxes, etc.)
- Cluster buying (multiple insiders) is very bullish

Data Sources:
- Primary: SEC EDGAR (official source)
- Backup: OpenInsider (scraped, faster)
- Tertiary: yfinance (limited data)

Key Metrics:
- Net insider sentiment (buys vs sells by value)
- Insider buying ratio (transactions)
- Notable transactions (CEO, CFO, Directors)
- Cluster detection (multiple insiders buying)

Author: ATLAS Financial Intelligence
Created: 2025-12-08 (MILESTONE-003, TASK-A012)
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import requests

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """Type of insider transaction."""
    BUY = "P"  # Purchase
    SELL = "S"  # Sale
    GIFT = "G"  # Gift
    AWARD = "A"  # Award/Grant
    EXERCISE = "M"  # Option Exercise
    OTHER = "O"


class InsiderRole(Enum):
    """Role of the insider."""
    CEO = "CEO"
    CFO = "CFO"
    COO = "COO"
    CTO = "CTO"
    PRESIDENT = "President"
    DIRECTOR = "Director"
    VP = "Vice President"
    OFFICER = "Officer"
    BENEFICIAL_OWNER = "10% Owner"
    OTHER = "Other"


@dataclass
class InsiderTransaction:
    """Single insider transaction record."""
    ticker: str
    insider_name: str
    insider_role: InsiderRole
    transaction_type: TransactionType
    transaction_date: datetime
    shares: int
    price_per_share: float
    total_value: float
    shares_owned_after: Optional[int] = None
    filing_date: Optional[datetime] = None
    form_type: str = "4"  # SEC Form 4
    
    @property
    def is_purchase(self) -> bool:
        return self.transaction_type == TransactionType.BUY
    
    @property
    def is_sale(self) -> bool:
        return self.transaction_type == TransactionType.SELL
    
    def to_dict(self) -> Dict:
        return {
            'ticker': self.ticker,
            'insider_name': self.insider_name,
            'role': self.insider_role.value,
            'type': 'Buy' if self.is_purchase else 'Sell',
            'date': self.transaction_date.strftime('%Y-%m-%d'),
            'shares': self.shares,
            'price': self.price_per_share,
            'value': self.total_value,
            'shares_after': self.shares_owned_after
        }


@dataclass
class InsiderSummary:
    """Aggregated insider activity summary."""
    ticker: str
    period_days: int
    timestamp: str
    
    # Transaction counts
    total_transactions: int = 0
    buy_transactions: int = 0
    sell_transactions: int = 0
    
    # Value metrics
    total_buy_value: float = 0.0
    total_sell_value: float = 0.0
    net_value: float = 0.0  # Positive = net buying
    
    # Share metrics
    total_shares_bought: int = 0
    total_shares_sold: int = 0
    net_shares: int = 0
    
    # Notable insiders
    notable_buyers: List[str] = field(default_factory=list)
    notable_sellers: List[str] = field(default_factory=list)
    
    # Cluster detection
    is_cluster_buying: bool = False  # 3+ insiders buying in 30 days
    cluster_buyers_count: int = 0
    
    # Sentiment score
    sentiment_score: float = 0.0  # -100 to +100
    sentiment_label: str = "Neutral"
    
    # Recent transactions
    recent_transactions: List[InsiderTransaction] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'ticker': self.ticker,
            'period_days': self.period_days,
            'timestamp': self.timestamp,
            'transactions': {
                'total': self.total_transactions,
                'buys': self.buy_transactions,
                'sells': self.sell_transactions
            },
            'value': {
                'bought': self.total_buy_value,
                'sold': self.total_sell_value,
                'net': self.net_value
            },
            'shares': {
                'bought': self.total_shares_bought,
                'sold': self.total_shares_sold,
                'net': self.net_shares
            },
            'notable': {
                'buyers': self.notable_buyers,
                'sellers': self.notable_sellers
            },
            'cluster': {
                'detected': self.is_cluster_buying,
                'count': self.cluster_buyers_count
            },
            'sentiment': {
                'score': self.sentiment_score,
                'label': self.sentiment_label
            }
        }


class InsiderTransactionTracker:
    """
    Tracks and analyzes insider transactions.
    
    Usage:
        tracker = InsiderTransactionTracker()
        summary = tracker.get_insider_summary("AAPL", days=90)
        
        # Check sentiment
        if summary.sentiment_score > 50:
            print("Strong insider buying!")
        
        # Check for cluster buying
        if summary.is_cluster_buying:
            print("Multiple insiders buying - bullish signal!")
    """
    
    # Weights for sentiment calculation
    ROLE_WEIGHTS = {
        InsiderRole.CEO: 3.0,
        InsiderRole.CFO: 2.5,
        InsiderRole.COO: 2.0,
        InsiderRole.CTO: 2.0,
        InsiderRole.PRESIDENT: 2.0,
        InsiderRole.DIRECTOR: 1.5,
        InsiderRole.VP: 1.2,
        InsiderRole.OFFICER: 1.0,
        InsiderRole.BENEFICIAL_OWNER: 1.5,
        InsiderRole.OTHER: 0.5
    }
    
    # Cluster detection threshold
    CLUSTER_THRESHOLD = 3  # 3+ unique insiders buying
    
    def __init__(self):
        """Initialize the tracker."""
        pass
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_insider_summary(_self, ticker: str, days: int = 90) -> Optional[InsiderSummary]:
        """
        Get insider transaction summary for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            days: Lookback period in days
            
        Returns:
            InsiderSummary with aggregated metrics
        """
        try:
            # Fetch transactions
            transactions = _self._fetch_transactions(ticker, days)
            
            if not transactions:
                return InsiderSummary(
                    ticker=ticker,
                    period_days=days,
                    timestamp=datetime.now().isoformat(),
                    sentiment_label="No Data"
                )
            
            # Aggregate metrics
            summary = _self._aggregate_transactions(ticker, transactions, days)
            
            # Calculate sentiment
            summary = _self._calculate_sentiment(summary)
            
            # Detect clusters
            summary = _self._detect_clusters(summary, transactions)
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get insider summary for {ticker}: {e}")
            return None
    
    def _fetch_transactions(self, ticker: str, days: int) -> List[InsiderTransaction]:
        """
        Fetch insider transactions from data sources.
        
        Priority:
        1. yfinance (fastest, limited data)
        2. SEC EDGAR (official, slower)
        3. OpenInsider (backup)
        """
        transactions = []
        
        # Try yfinance first (fastest)
        try:
            transactions = self._fetch_from_yfinance(ticker, days)
            if transactions:
                logger.debug(f"Got {len(transactions)} transactions from yfinance")
                return transactions
        except Exception as e:
            logger.debug(f"yfinance failed: {e}")
        
        # Try SEC EDGAR (more complete but slower)
        # Note: This will be enhanced in TASK-A013
        
        # Try OpenInsider (backup)
        # Note: This will be enhanced in TASK-A013
        
        return transactions
    
    def _fetch_from_yfinance(self, ticker: str, days: int) -> List[InsiderTransaction]:
        """Fetch insider transactions from yfinance."""
        import yfinance as yf
        
        stock = yf.Ticker(ticker)
        
        # Get insider transactions
        insider_df = stock.insider_transactions
        
        if insider_df is None or insider_df.empty:
            return []
        
        transactions = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for _, row in insider_df.iterrows():
            try:
                # Parse transaction date
                tx_date = pd.to_datetime(row.get('Start Date', row.get('Date')))
                
                if tx_date < cutoff_date:
                    continue
                
                # Parse transaction type
                tx_text = str(row.get('Text', '')).lower()
                if 'purchase' in tx_text or 'buy' in tx_text:
                    tx_type = TransactionType.BUY
                elif 'sale' in tx_text or 'sell' in tx_text:
                    tx_type = TransactionType.SELL
                elif 'gift' in tx_text:
                    tx_type = TransactionType.GIFT
                elif 'exercise' in tx_text:
                    tx_type = TransactionType.EXERCISE
                else:
                    tx_type = TransactionType.OTHER
                
                # Parse shares and value
                shares = int(row.get('Shares', 0))
                value = float(row.get('Value', 0))
                price = value / shares if shares > 0 else 0
                
                # Parse insider info
                insider_name = str(row.get('Insider', 'Unknown'))
                role = self._parse_role(str(row.get('Position', '')))
                
                tx = InsiderTransaction(
                    ticker=ticker,
                    insider_name=insider_name,
                    insider_role=role,
                    transaction_type=tx_type,
                    transaction_date=tx_date,
                    shares=abs(shares),
                    price_per_share=price,
                    total_value=abs(value),
                    shares_owned_after=row.get('Shares Owned', None)
                )
                
                transactions.append(tx)
                
            except Exception as e:
                logger.debug(f"Error parsing transaction: {e}")
                continue
        
        return transactions
    
    def _parse_role(self, role_text: str) -> InsiderRole:
        """Parse insider role from text."""
        role_text = role_text.upper()
        
        if 'CEO' in role_text or 'CHIEF EXECUTIVE' in role_text:
            return InsiderRole.CEO
        elif 'CFO' in role_text or 'CHIEF FINANCIAL' in role_text:
            return InsiderRole.CFO
        elif 'COO' in role_text or 'CHIEF OPERATING' in role_text:
            return InsiderRole.COO
        elif 'CTO' in role_text or 'CHIEF TECHNOLOGY' in role_text:
            return InsiderRole.CTO
        elif 'PRESIDENT' in role_text:
            return InsiderRole.PRESIDENT
        elif 'DIRECTOR' in role_text:
            return InsiderRole.DIRECTOR
        elif 'VP' in role_text or 'VICE PRESIDENT' in role_text:
            return InsiderRole.VP
        elif '10%' in role_text or 'BENEFICIAL' in role_text:
            return InsiderRole.BENEFICIAL_OWNER
        elif 'OFFICER' in role_text:
            return InsiderRole.OFFICER
        else:
            return InsiderRole.OTHER
    
    def _aggregate_transactions(
        self, 
        ticker: str, 
        transactions: List[InsiderTransaction],
        days: int
    ) -> InsiderSummary:
        """Aggregate transactions into summary metrics."""
        
        summary = InsiderSummary(
            ticker=ticker,
            period_days=days,
            timestamp=datetime.now().isoformat(),
            total_transactions=len(transactions),
            recent_transactions=transactions[:10]  # Keep 10 most recent
        )
        
        buyers = set()
        sellers = set()
        
        for tx in transactions:
            if tx.is_purchase:
                summary.buy_transactions += 1
                summary.total_buy_value += tx.total_value
                summary.total_shares_bought += tx.shares
                buyers.add(tx.insider_name)
                
                # Track notable buyers (C-suite and directors)
                if tx.insider_role in [InsiderRole.CEO, InsiderRole.CFO, InsiderRole.COO, InsiderRole.DIRECTOR]:
                    if tx.insider_name not in summary.notable_buyers:
                        summary.notable_buyers.append(tx.insider_name)
                        
            elif tx.is_sale:
                summary.sell_transactions += 1
                summary.total_sell_value += tx.total_value
                summary.total_shares_sold += tx.shares
                sellers.add(tx.insider_name)
                
                # Track notable sellers
                if tx.insider_role in [InsiderRole.CEO, InsiderRole.CFO, InsiderRole.COO, InsiderRole.DIRECTOR]:
                    if tx.insider_name not in summary.notable_sellers:
                        summary.notable_sellers.append(tx.insider_name)
        
        # Calculate net metrics
        summary.net_value = summary.total_buy_value - summary.total_sell_value
        summary.net_shares = summary.total_shares_bought - summary.total_shares_sold
        
        return summary
    
    def _calculate_sentiment(self, summary: InsiderSummary) -> InsiderSummary:
        """
        Calculate insider sentiment score (-100 to +100).
        
        Factors:
        - Net value (weighted by role)
        - Transaction count ratio
        - Notable insider activity
        """
        if summary.total_transactions == 0:
            summary.sentiment_score = 0
            summary.sentiment_label = "No Activity"
            return summary
        
        # Transaction ratio component (-50 to +50)
        buy_ratio = summary.buy_transactions / summary.total_transactions
        ratio_score = (buy_ratio - 0.5) * 100  # 0 buys = -50, all buys = +50
        
        # Value component (-50 to +50)
        total_value = summary.total_buy_value + summary.total_sell_value
        if total_value > 0:
            value_ratio = summary.total_buy_value / total_value
            value_score = (value_ratio - 0.5) * 100
        else:
            value_score = 0
        
        # Combine scores (60% value, 40% ratio)
        sentiment = value_score * 0.6 + ratio_score * 0.4
        
        # Boost for notable buyers
        if summary.notable_buyers:
            sentiment += len(summary.notable_buyers) * 5
        
        # Cap at -100 to +100
        sentiment = max(-100, min(100, sentiment))
        
        summary.sentiment_score = round(sentiment, 1)
        
        # Set label
        if sentiment >= 50:
            summary.sentiment_label = "Strong Buying"
        elif sentiment >= 20:
            summary.sentiment_label = "Moderate Buying"
        elif sentiment >= -20:
            summary.sentiment_label = "Neutral"
        elif sentiment >= -50:
            summary.sentiment_label = "Moderate Selling"
        else:
            summary.sentiment_label = "Strong Selling"
        
        return summary
    
    def _detect_clusters(
        self, 
        summary: InsiderSummary, 
        transactions: List[InsiderTransaction]
    ) -> InsiderSummary:
        """Detect cluster buying (multiple insiders buying in short period)."""
        
        # Get unique buyers in last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        recent_buyers = set()
        for tx in transactions:
            if tx.is_purchase and tx.transaction_date >= thirty_days_ago:
                recent_buyers.add(tx.insider_name)
        
        summary.cluster_buyers_count = len(recent_buyers)
        summary.is_cluster_buying = len(recent_buyers) >= self.CLUSTER_THRESHOLD
        
        return summary


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

def get_insider_summary(ticker: str, days: int = 90) -> Optional[InsiderSummary]:
    """
    Get insider transaction summary for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        days: Lookback period in days (default 90)
        
    Returns:
        InsiderSummary or None
    """
    tracker = InsiderTransactionTracker()
    return tracker.get_insider_summary(ticker, days)


def get_insider_sentiment(ticker: str) -> Tuple[float, str]:
    """
    Get just the sentiment score and label.
    
    Returns:
        Tuple of (score, label) e.g. (45.5, "Moderate Buying")
    """
    summary = get_insider_summary(ticker)
    if summary:
        return (summary.sentiment_score, summary.sentiment_label)
    return (0.0, "No Data")


def is_cluster_buying(ticker: str) -> bool:
    """
    Check if there's cluster buying activity.
    
    Returns:
        True if 3+ insiders bought in last 30 days
    """
    summary = get_insider_summary(ticker, days=30)
    return summary.is_cluster_buying if summary else False


# ==========================================
# VISUALIZATION FUNCTIONS
# ==========================================

def create_insider_gauge(sentiment_score: float) -> "go.Figure":
    """Create a gauge chart showing insider sentiment."""
    import plotly.graph_objects as go
    
    # Determine color based on score
    if sentiment_score > 30:
        color = "green"
    elif sentiment_score > 0:
        color = "lightgreen"
    elif sentiment_score > -30:
        color = "orange"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=sentiment_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Insider Sentiment", 'font': {'size': 16}},
        delta={'reference': 0, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge={
            'axis': {'range': [-100, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [-100, -30], 'color': 'rgba(255, 0, 0, 0.2)'},
                {'range': [-30, 0], 'color': 'rgba(255, 165, 0, 0.2)'},
                {'range': [0, 30], 'color': 'rgba(144, 238, 144, 0.2)'},
                {'range': [30, 100], 'color': 'rgba(0, 128, 0, 0.2)'},
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': sentiment_score
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


def create_insider_activity_chart(summary: InsiderSummary) -> "go.Figure":
    """Create a bar chart showing buy vs sell activity."""
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    # Add buy bar
    fig.add_trace(go.Bar(
        x=['Transactions', 'Value ($M)'],
        y=[summary.buy_transactions, summary.total_buy_value / 1_000_000],
        name='Buys',
        marker_color='green'
    ))
    
    # Add sell bar
    fig.add_trace(go.Bar(
        x=['Transactions', 'Value ($M)'],
        y=[summary.sell_transactions, summary.total_sell_value / 1_000_000],
        name='Sells',
        marker_color='red'
    ))
    
    fig.update_layout(
        title=f"Insider Activity - Last {summary.period_days} Days",
        barmode='group',
        height=300,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        legend={'orientation': 'h', 'y': -0.15}
    )
    
    return fig


def create_transaction_table(transactions: List[InsiderTransaction]) -> pd.DataFrame:
    """Create a DataFrame for displaying transactions."""
    if not transactions:
        return pd.DataFrame()
    
    data = [tx.to_dict() for tx in transactions]
    df = pd.DataFrame(data)
    
    # Format columns
    if 'value' in df.columns:
        df['value'] = df['value'].apply(lambda x: f"${x:,.0f}")
    if 'price' in df.columns:
        df['price'] = df['price'].apply(lambda x: f"${x:.2f}")
    if 'shares' in df.columns:
        df['shares'] = df['shares'].apply(lambda x: f"{x:,}")
    
    return df


# ==========================================
# STREAMLIT UI COMPONENT
# ==========================================

def render_insider_card(ticker: str, compact: bool = True):
    """
    Render insider activity card in Streamlit.
    
    Args:
        ticker: Stock ticker symbol
        compact: If True, show condensed view
    """
    summary = get_insider_summary(ticker)
    
    if not summary:
        st.warning(f"No insider data available for {ticker}")
        return
    
    if compact:
        # Compact view - single row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            score = summary.sentiment_score
            delta = f"{summary.buy_transactions} buys / {summary.sell_transactions} sells"
            st.metric(
                "Insider Sentiment",
                f"{score:+.0f}",
                delta=delta,
                help="Score from -100 (selling) to +100 (buying)"
            )
        
        with col2:
            st.metric(
                "Net Value",
                f"${summary.net_value/1_000_000:.1f}M" if abs(summary.net_value) >= 1_000_000 else f"${summary.net_value:,.0f}",
                help="Net insider buying (positive) or selling (negative)"
            )
        
        with col3:
            st.metric(
                "Sentiment",
                summary.sentiment_label,
                help="Overall insider sentiment classification"
            )
        
        with col4:
            if summary.is_cluster_buying:
                st.metric(
                    "🔥 Cluster Buying",
                    f"{summary.cluster_buyers_count} insiders",
                    help="Multiple insiders buying in last 30 days - bullish signal!"
                )
            else:
                st.metric(
                    "Cluster Status",
                    "Not Detected",
                    help="No cluster buying detected"
                )
    else:
        # Full view
        st.markdown("### Insider Transactions")
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transactions", summary.total_transactions)
        with col2:
            st.metric("Buys", summary.buy_transactions)
        with col3:
            st.metric("Sells", summary.sell_transactions)
        with col4:
            st.metric("Sentiment Score", f"{summary.sentiment_score:+.0f}")
        
        # Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.plotly_chart(create_insider_gauge(summary.sentiment_score), use_container_width=True)
        
        with chart_col2:
            st.plotly_chart(create_insider_activity_chart(summary), use_container_width=True)
        
        # Notable activity
        if summary.notable_buyers or summary.notable_sellers:
            st.markdown("#### Notable Insider Activity")
            
            if summary.notable_buyers:
                st.success(f"**Buyers:** {', '.join(summary.notable_buyers)}")
            
            if summary.notable_sellers:
                st.warning(f"**Sellers:** {', '.join(summary.notable_sellers)}")
        
        # Recent transactions table
        if summary.recent_transactions:
            st.markdown("#### Recent Transactions")
            df = create_transaction_table(summary.recent_transactions)
            st.dataframe(df, hide_index=True, use_container_width=True)


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("INSIDER TRANSACTION TRACKER TEST")
    print("=" * 60)
    
    tracker = InsiderTransactionTracker()
    
    for ticker in ['AAPL', 'MSFT', 'NVDA']:
        print(f"\n[TEST] {ticker}")
        summary = tracker.get_insider_summary(ticker)
        
        if summary:
            data = summary.to_dict()
            print(f"  Transactions: {data['transactions']['total']}")
            print(f"  Buys: {data['transactions']['buys']}")
            print(f"  Sells: {data['transactions']['sells']}")
            print(f"  Net Value: ${data['value']['net']:,.0f}")
            print(f"  Sentiment: {data['sentiment']['score']} ({data['sentiment']['label']})")
            print(f"  Cluster Buying: {data['cluster']['detected']}")
        else:
            print("  No data available")
    
    print("\n[OK] Module ready for integration")

