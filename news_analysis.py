"""
NEWS ANALYSIS MODULE
================================================================================
Multi-source news aggregation with optional paid API support.

Features:
- RSS feeds (Yahoo Finance, Google News) - FREE
- NewsAPI integration (optional paid) - $$$
- Sentiment analysis (keyword-based)
- Article filtering and ranking
- Toggle between free/paid sources

Data Sources:
- Yahoo Finance RSS (Free, always available)
- Google News RSS (Free, always available)
- Reuters RSS (Free, always available)
- MarketWatch RSS (Free, always available)
- CNBC RSS (Free, always available)
- NewsAPI (Paid/Free tier, optional)

Author: Atlas Financial Intelligence
Date: November 2025
"""

import requests
import feedparser
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import os
import re


@st.cache_data(ttl=1800)  # Cache for 30 minutes (news changes frequently)
def get_ticker_news(ticker: str, use_newsapi: bool = False, days_back: int = 7) -> Dict:
    """
    Fetch recent news for a ticker from multiple sources
    
    Args:
        ticker: Stock ticker symbol
        use_newsapi: Whether to use NewsAPI (requires API key)
        days_back: Number of days to look back
        
    Returns:
        Dictionary with news articles and sentiment
    """
    try:
        print(f"\n[INFO] Fetching news for {ticker}...")
        
        news_data = {
            'status': 'success',
            'articles': [],
            'summary': {},
            'sources_used': []
        }
        
        # ====================================
        # SOURCE 1: YAHOO FINANCE RSS (FREE)
        # ====================================
        try:
            yahoo_rss = f"https://finance.yahoo.com/rss/headline?s={ticker}"
            feed = feedparser.parse(yahoo_rss)
            
            for entry in feed.entries[:15]:
                pub_date = entry.get('published', 'N/A')
                
                # Parse date
                try:
                    pub_datetime = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                    pub_date_str = pub_datetime.strftime('%Y-%m-%d %H:%M')
                except:
                    pub_datetime = datetime.now(timezone.utc)
                    pub_date_str = pub_date[:16] if len(pub_date) > 16 else pub_date
                
                news_data['articles'].append({
                    'source': 'Yahoo Finance',
                    'title': entry.title,
                    'link': entry.link,
                    'published': pub_date_str,
                    'summary': entry.get('summary', '')[:250],
                    'timestamp': pub_datetime
                })
            
            news_data['sources_used'].append('Yahoo Finance RSS')
            print(f"[OK] Yahoo Finance: {len([a for a in news_data['articles'] if a['source'] == 'Yahoo Finance'])} articles")
            
        except Exception as e:
            print(f"[WARN] Yahoo RSS failed: {e}")
        
        # ====================================
        # SOURCE 2: GOOGLE NEWS RSS (FREE)
        # ====================================
        try:
            # Search for company ticker + stock news
            google_rss = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(google_rss)
            
            for entry in feed.entries[:15]:
                pub_date = entry.get('published', 'N/A')
                
                # Parse date
                try:
                    pub_datetime = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    # Make timezone-aware
                    if pub_datetime.tzinfo is None:
                        pub_datetime = pub_datetime.replace(tzinfo=timezone.utc)
                    pub_date_str = pub_datetime.strftime('%Y-%m-%d %H:%M')
                except:
                    pub_datetime = datetime.now(timezone.utc)
                    pub_date_str = pub_date[:16] if len(pub_date) > 16 else pub_date
                
                # Google News doesn't provide summaries, just titles
                news_data['articles'].append({
                    'source': 'Google News',
                    'title': entry.title,
                    'link': entry.link,
                    'published': pub_date_str,
                    'summary': '',
                    'timestamp': pub_datetime
                })
            
            news_data['sources_used'].append('Google News RSS')
            print(f"[OK] Google News: {len([a for a in news_data['articles'] if a['source'] == 'Google News'])} articles")
            
        except Exception as e:
            print(f"[WARN] Google RSS failed: {e}")
        
        # ====================================
        # SOURCE 3: REUTERS RSS (FREE)
        # ====================================
        try:
            # Reuters ticker-specific feed
            reuters_rss = f"https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best"
            feed = feedparser.parse(reuters_rss)
            
            # Filter for ticker mentions
            for entry in feed.entries[:20]:
                title_lower = entry.title.lower()
                ticker_lower = ticker.lower()
                
                # Only include if ticker is mentioned
                if ticker_lower in title_lower or ticker in entry.title:
                    pub_date = entry.get('published', 'N/A')
                    
                    try:
                        pub_datetime = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                        pub_date_str = pub_datetime.strftime('%Y-%m-%d %H:%M')
                    except:
                        pub_datetime = datetime.now(timezone.utc)
                        pub_date_str = pub_date[:16] if len(pub_date) > 16 else pub_date
                    
                    news_data['articles'].append({
                        'source': 'Reuters',
                        'title': entry.title,
                        'link': entry.link,
                        'published': pub_date_str,
                        'summary': entry.get('summary', '')[:250],
                        'timestamp': pub_datetime
                    })
            
            news_data['sources_used'].append('Reuters RSS')
            print(f"[OK] Reuters: {len([a for a in news_data['articles'] if a['source'] == 'Reuters'])} articles")
            
        except Exception as e:
            print(f"[WARN] Reuters RSS failed: {e}")
        
        # ====================================
        # SOURCE 4: MARKETWATCH RSS (FREE)
        # ====================================
        try:
            # MarketWatch latest news
            mw_rss = f"http://feeds.marketwatch.com/marketwatch/topstories/"
            feed = feedparser.parse(mw_rss)
            
            # Filter for ticker mentions
            for entry in feed.entries[:20]:
                title_lower = entry.title.lower()
                summary_lower = entry.get('summary', '').lower()
                ticker_lower = ticker.lower()
                
                # Only include if ticker is mentioned in title or summary
                if ticker_lower in title_lower or ticker in entry.title or ticker_lower in summary_lower:
                    pub_date = entry.get('published', 'N/A')
                    
                    try:
                        pub_datetime = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                        pub_date_str = pub_datetime.strftime('%Y-%m-%d %H:%M')
                    except:
                        pub_datetime = datetime.now(timezone.utc)
                        pub_date_str = pub_date[:16] if len(pub_date) > 16 else pub_date
                    
                    news_data['articles'].append({
                        'source': 'MarketWatch',
                        'title': entry.title,
                        'link': entry.link,
                        'published': pub_date_str,
                        'summary': entry.get('summary', '')[:250],
                        'timestamp': pub_datetime
                    })
            
            news_data['sources_used'].append('MarketWatch RSS')
            print(f"[OK] MarketWatch: {len([a for a in news_data['articles'] if a['source'] == 'MarketWatch'])} articles")
            
        except Exception as e:
            print(f"[WARN] MarketWatch RSS failed: {e}")
        
        # ====================================
        # SOURCE 5: CNBC RSS (FREE)
        # ====================================
        try:
            # CNBC top news
            cnbc_rss = "https://www.cnbc.com/id/100003114/device/rss/rss.html"
            feed = feedparser.parse(cnbc_rss)
            
            # Filter for ticker mentions
            for entry in feed.entries[:20]:
                title_lower = entry.title.lower()
                summary_lower = entry.get('summary', '').lower()
                ticker_lower = ticker.lower()
                
                # Only include if ticker is mentioned
                if ticker_lower in title_lower or ticker in entry.title or ticker_lower in summary_lower:
                    pub_date = entry.get('published', 'N/A')
                    
                    try:
                        pub_datetime = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                        pub_date_str = pub_datetime.strftime('%Y-%m-%d %H:%M')
                    except:
                        pub_datetime = datetime.now(timezone.utc)
                        pub_date_str = pub_date[:16] if len(pub_date) > 16 else pub_date
                    
                    news_data['articles'].append({
                        'source': 'CNBC',
                        'title': entry.title,
                        'link': entry.link,
                        'published': pub_date_str,
                        'summary': entry.get('summary', '')[:250],
                        'timestamp': pub_datetime
                    })
            
            news_data['sources_used'].append('CNBC RSS')
            print(f"[OK] CNBC: {len([a for a in news_data['articles'] if a['source'] == 'CNBC'])} articles")
            
        except Exception as e:
            print(f"[WARN] CNBC RSS failed: {e}")
        
        # ====================================
        # SOURCE 6: NEWSAPI (PAID - OPTIONAL)
        # ====================================
        if use_newsapi:
            api_key = os.getenv('NEWSAPI_KEY')
            
            if api_key:
                try:
                    url = "https://newsapi.org/v2/everything"
                    
                    # Calculate date range
                    from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
                    
                    params = {
                        'q': f'{ticker} stock OR {ticker} earnings OR {ticker} company',
                        'apiKey': api_key,
                        'language': 'en',
                        'sortBy': 'publishedAt',
                        'from': from_date,
                        'pageSize': 30
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for article in data.get('articles', []):
                            # Parse published date (already timezone-aware from ISO format)
                            try:
                                pub_datetime = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
                            except:
                                pub_datetime = datetime.now(timezone.utc)
                            
                            news_data['articles'].append({
                                'source': article['source']['name'],
                                'title': article['title'],
                                'link': article['url'],
                                'published': pub_datetime.strftime('%Y-%m-%d %H:%M'),
                                'summary': article.get('description', '')[:250],
                                'timestamp': pub_datetime
                            })
                        
                        news_data['sources_used'].append('NewsAPI (Paid)')
                        print(f"[OK] NewsAPI: {len([a for a in news_data['articles'] if 'NewsAPI' in str(a)])} articles")
                    
                    elif response.status_code == 429:
                        print(f"[WARN] NewsAPI rate limit exceeded")
                        news_data['api_warning'] = 'NewsAPI rate limit reached (falling back to free sources)'
                    
                    else:
                        print(f"[WARN] NewsAPI error: {response.status_code}")
                
                except Exception as e:
                    print(f"[WARN] NewsAPI failed: {e}")
            else:
                print(f"[INFO] NewsAPI key not found (using free sources only)")
                news_data['api_warning'] = 'NewsAPI key not set (using free RSS feeds)'
        
        # ====================================
        # DEDUPLICATE & SORT
        # ====================================
        
        # Remove duplicates based on title similarity
        unique_articles = []
        seen_titles = set()
        
        for article in news_data['articles']:
            # Normalize title for comparison
            title_norm = re.sub(r'[^a-z0-9]', '', article['title'].lower())
            
            if title_norm not in seen_titles:
                seen_titles.add(title_norm)
                unique_articles.append(article)
        
        # Sort by timestamp (newest first) - use timezone-aware min
        unique_articles.sort(key=lambda x: x.get('timestamp', datetime.min.replace(tzinfo=timezone.utc)), reverse=True)
        
        news_data['articles'] = unique_articles[:50]  # Limit to 50 articles
        
        # ====================================
        # SENTIMENT ANALYSIS (KEYWORD-BASED)
        # ====================================
        
        positive_keywords = [
            'beat', 'beats', 'surge', 'surges', 'gain', 'gains', 'up', 'rise', 'rises',
            'growth', 'profit', 'bullish', 'strong', 'outperform', 'buy', 'upgrade',
            'positive', 'success', 'win', 'record', 'high', 'soar', 'rally'
        ]
        
        negative_keywords = [
            'miss', 'misses', 'fall', 'falls', 'down', 'drop', 'drops', 'loss', 'losses',
            'bearish', 'weak', 'underperform', 'sell', 'downgrade', 'negative', 'concern',
            'concerns', 'warning', 'risk', 'decline', 'plunge', 'crash', 'lawsuit'
        ]
        
        sentiment_score = 0
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for article in news_data['articles']:
            title_lower = article['title'].lower()
            summary_lower = article.get('summary', '').lower()
            combined_text = title_lower + ' ' + summary_lower
            
            article_sentiment = 0
            
            # Count positive words
            pos_matches = sum(1 for word in positive_keywords if word in combined_text)
            # Count negative words
            neg_matches = sum(1 for word in negative_keywords if word in combined_text)
            
            article_sentiment = pos_matches - neg_matches
            
            if article_sentiment > 0:
                positive_count += 1
                article['sentiment'] = 'Positive'
            elif article_sentiment < 0:
                negative_count += 1
                article['sentiment'] = 'Negative'
            else:
                neutral_count += 1
                article['sentiment'] = 'Neutral'
            
            sentiment_score += article_sentiment
        
        # Overall sentiment
        total_articles = len(news_data['articles'])
        
        if total_articles > 0:
            sentiment_ratio = sentiment_score / total_articles
            
            if sentiment_ratio > 0.5:
                news_data['overall_sentiment'] = 'Bullish'
                news_data['sentiment_color'] = 'green'
            elif sentiment_ratio > 0:
                news_data['overall_sentiment'] = 'Slightly Bullish'
                news_data['sentiment_color'] = 'lightgreen'
            elif sentiment_ratio == 0:
                news_data['overall_sentiment'] = 'Neutral'
                news_data['sentiment_color'] = 'gray'
            elif sentiment_ratio > -0.5:
                news_data['overall_sentiment'] = 'Slightly Bearish'
                news_data['sentiment_color'] = 'orange'
            else:
                news_data['overall_sentiment'] = 'Bearish'
                news_data['sentiment_color'] = 'red'
        
        # ====================================
        # SUMMARY STATISTICS
        # ====================================
        
        news_data['summary'] = {
            'total_articles': total_articles,
            'sources': len(news_data['sources_used']),
            'positive_articles': positive_count,
            'negative_articles': negative_count,
            'neutral_articles': neutral_count,
            'latest': news_data['articles'][0]['published'] if news_data['articles'] else 'N/A',
            'sentiment_score': sentiment_score
        }
        
        print(f"[OK] News analysis complete")
        print(f"     Total Articles: {total_articles}")
        print(f"     Sources: {len(news_data['sources_used'])}")
        print(f"     Sentiment: {news_data.get('overall_sentiment', 'N/A')}")
        
        return news_data
        
    except Exception as e:
        print(f"[ERROR] News analysis failed: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error fetching news: {str(e)}'
        }


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING NEWS ANALYSIS MODULE")
    print("="*80)
    
    test_ticker = "AAPL"
    
    # Test FREE version (RSS only)
    print(f"\n[TEST 1] News Analysis for {test_ticker} (FREE - RSS only)")
    print("-"*80)
    news_data = get_ticker_news(test_ticker, use_newsapi=False)
    
    if news_data['status'] == 'success':
        summary = news_data['summary']
        
        print(f"\nSummary:")
        print(f"  Total Articles: {summary['total_articles']}")
        print(f"  Sources: {summary['sources']}")
        print(f"  Positive: {summary['positive_articles']}")
        print(f"  Negative: {summary['negative_articles']}")
        print(f"  Neutral: {summary['neutral_articles']}")
        print(f"  Overall Sentiment: {news_data.get('overall_sentiment', 'N/A')}")
        
        print(f"\nSources Used:")
        for source in news_data['sources_used']:
            print(f"  • {source}")
        
        print(f"\nLatest 5 Headlines:")
        for i, article in enumerate(news_data['articles'][:5], 1):
            print(f"  {i}. [{article['source']}] {article['title'][:80]}")
        
        print("\n[OK] Test PASSED (FREE mode)")
    else:
        print(f"\n[FAIL] {news_data['message']}")
    
    # Test PAID version (with NewsAPI if available)
    print(f"\n\n[TEST 2] News Analysis for {test_ticker} (PAID - with NewsAPI)")
    print("-"*80)
    news_data_paid = get_ticker_news(test_ticker, use_newsapi=True)
    
    if news_data_paid['status'] == 'success':
        summary = news_data_paid['summary']
        
        print(f"\nSummary:")
        print(f"  Total Articles: {summary['total_articles']}")
        print(f"  Sources: {summary['sources']}")
        print(f"  Overall Sentiment: {news_data_paid.get('overall_sentiment', 'N/A')}")
        
        print(f"\nSources Used:")
        for source in news_data_paid['sources_used']:
            print(f"  • {source}")
        
        if 'api_warning' in news_data_paid:
            print(f"\n⚠️  {news_data_paid['api_warning']}")
        
        print("\n[OK] Test PASSED (PAID mode)")
    else:
        print(f"\n[FAIL] {news_data_paid['message']}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    print(f"\nFeatures:")
    print(f"  • FREE: Yahoo Finance RSS + Google News RSS")
    print(f"  • PAID: +NewsAPI (30,000+ sources)")
    print(f"  • Sentiment Analysis: Keyword-based")
    print(f"  • Deduplication: Yes")
    print(f"  • Caching: 30 minutes")

