"""
ATLAS Financial Intelligence - News Tab
========================================
News aggregation with sentiment analysis
Extracted from usa_app.py lines 3729-3878
"""

import streamlit as st


def icon(name, size="1em", color=None):
    """Render a Bootstrap Icon"""
    style = f"font-size: {size};"
    if color:
        style += f" color: {color};"
    return f'<i class="bi bi-{name}" style="{style}"></i>'


def render_news_tab(ticker: str):
    """
    Render the News & Sentiment tab.
    
    Args:
        ticker: Stock ticker symbol
    """
    st.markdown(f"## {icon('newspaper', '1.5em')} Recent News & Market Sentiment", unsafe_allow_html=True)
    st.info("Multi-source news aggregation with sentiment analysis")
    
    # Toggle for NewsAPI (paid)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### News Sources")
    
    with col2:
        use_newsapi = st.checkbox(
            "Use NewsAPI",
            value=False,
            help="Enable NewsAPI for 30,000+ premium sources (requires API key). Leave unchecked for free RSS feeds.",
            key="news_use_api"
        )
    
    if use_newsapi:
        st.caption("NewsAPI enabled (paid/limited free tier - 100 requests/day)")
    else:
        st.caption("Using free RSS feeds (Yahoo Finance + Google News)")
    
    st.markdown("---")
    
    try:
        from news_analysis import get_ticker_news
        
        with st.spinner("Fetching latest news..."):
            news_data = get_ticker_news(ticker, use_newsapi=use_newsapi)
            
            if news_data['status'] == 'success':
                summary = news_data['summary']
                
                # Display API warning if present
                if 'api_warning' in news_data:
                    st.warning(f"{news_data['api_warning']}")
                
                # Summary metrics
                _render_news_summary(summary, news_data)
                
                st.markdown("---")
                
                # Sentiment breakdown
                _render_sentiment_breakdown(summary)
                
                st.markdown("---")
                
                # Sources used
                _render_sources(news_data)
                
                st.markdown("---")
                
                # Display articles
                _render_articles(news_data, summary)
                
                # API key setup instructions
                if not use_newsapi:
                    _render_api_instructions()
            
            else:
                st.error(f"{news_data.get('message', 'Failed to fetch news')}")
    
    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        st.caption("Tip: Make sure you have internet connection and RSS feeds are accessible.")


def _render_news_summary(summary: dict, news_data: dict):
    """Render news summary metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Articles", summary['total_articles'])
    
    with col2:
        st.metric("News Sources", summary['sources'])
    
    with col3:
        sentiment = news_data.get('overall_sentiment', 'Neutral')
        st.metric("Sentiment", sentiment)
    
    with col4:
        st.metric("Positive Articles", f"{summary['positive_articles']}/{summary['total_articles']}")


def _render_sentiment_breakdown(summary: dict):
    """Render sentiment breakdown"""
    st.markdown(f"### {icon('bar-chart-line', '1.2em')} Sentiment Breakdown", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"<div style='text-align: center;'><h3 style='color: green;'>{summary['positive_articles']}</h3><p>Positive</p></div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<div style='text-align: center;'><h3 style='color: gray;'>{summary['neutral_articles']}</h3><p>Neutral</p></div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"<div style='text-align: center;'><h3 style='color: red;'>{summary['negative_articles']}</h3><p>Negative</p></div>", unsafe_allow_html=True)


def _render_sources(news_data: dict):
    """Render news sources list"""
    st.markdown(f"### {icon('database', '1.2em')} Sources Used", unsafe_allow_html=True)
    
    for source in news_data['sources_used']:
        if 'Paid' in source:
            st.markdown(f"- [Premium] {source}")
        else:
            st.markdown(f"- [Free] {source}")


def _render_articles(news_data: dict, summary: dict):
    """Render news articles"""
    st.markdown(f"### {icon('list', '1.2em')} Recent Headlines (Latest {min(20, summary['total_articles'])})", unsafe_allow_html=True)
    
    for i, article in enumerate(news_data['articles'][:20], 1):
        with st.container():
            # Sentiment indicator
            sentiment_icons = {
                'Positive': '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">BULLISH</span>',
                'Negative': '<span style="background: #d32f2f; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">BEARISH</span>',
                'Neutral': '<span style="background: #9e9e9e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">NEUTRAL</span>'
            }
            
            sentiment_tag = sentiment_icons.get(article.get('sentiment', 'Neutral'), '')
            
            col1, col2 = st.columns([5, 2])
            
            with col1:
                st.markdown(f"{sentiment_tag} **{article['title']}**", unsafe_allow_html=True)
                if article.get('summary'):
                    st.markdown(f"_{article['summary'][:200]}..._")
            
            with col2:
                st.caption(f"{article['source']}")
                st.caption(f"{article['published'][:10]}")
                
                if article.get('author'):
                    st.caption(f"By {article['author']}")
                
                if article.get('sentiment_score'):
                    confidence = article['sentiment_score']
                    st.caption(f"Confidence: {confidence:.0%}")
                
                if article.get('summary'):
                    word_count = len(article['summary'].split())
                    read_time = max(1, word_count // 200)
                    st.caption(f"{read_time} min read")
            
            st.markdown(f'<a href="{article["link"]}" target="_blank" rel="noopener noreferrer">Read Full Article</a>', unsafe_allow_html=True)
            
            if i < len(news_data['articles'][:20]):
                st.markdown("---")


def _render_api_instructions():
    """Render NewsAPI setup instructions"""
    with st.expander("How to enable NewsAPI (optional)"):
        st.markdown("""
        **To unlock 30,000+ premium news sources:**
        
        1. Sign up at newsapi.org (free tier: 100 requests/day)
        2. Get your API key
        3. Set environment variable: `NEWSAPI_KEY=your_key_here`
        4. Check the "Use NewsAPI" box above
        
        **Note:** Free tier is limited. For production use, consider the paid plan.
        """)

