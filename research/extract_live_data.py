"""
TASK-E014: Extract Live Earnings Data
"""
import yfinance as yf
import json

def extract_earnings_data(ticker):
    """Extract all earnings-related data for a ticker."""
    stock = yf.Ticker(ticker)
    info = stock.info
    
    result = {
        'ticker': ticker,
        'current_estimates': {
            'forwardEps': info.get('forwardEps'),
            'trailingEps': info.get('trailingEps'),
            'earningsGrowth': info.get('earningsGrowth'),
            'earningsQuarterlyGrowth': info.get('earningsQuarterlyGrowth'),
        },
        'price_targets': {
            'currentPrice': info.get('currentPrice'),
            'targetMeanPrice': info.get('targetMeanPrice'),
            'targetHighPrice': info.get('targetHighPrice'),
            'targetLowPrice': info.get('targetLowPrice'),
        },
        'analyst_info': {
            'numberOfAnalystOpinions': info.get('numberOfAnalystOpinions'),
            'recommendationKey': info.get('recommendationKey'),
            'recommendationMean': info.get('recommendationMean'),
        },
        'valuation': {
            'forwardPE': info.get('forwardPE'),
            'trailingPE': info.get('trailingPE'),
        }
    }
    
    # Get earnings history
    try:
        ed = stock.earnings_dates
        if ed is not None and not ed.empty:
            result['earnings_history'] = []
            for date, row in ed.head(4).iterrows():
                result['earnings_history'].append({
                    'date': str(date),
                    'eps_estimate': row.get('EPS Estimate'),
                    'reported_eps': row.get('Reported EPS'),
                    'surprise_pct': row.get('Surprise(%)')
                })
    except:
        result['earnings_history'] = []
    
    return result

if __name__ == "__main__":
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    
    print("="*60)
    print("LIVE EARNINGS DATA EXTRACTION")
    print("="*60)
    
    all_data = {}
    
    for ticker in tickers:
        print(f"\n[Extracting] {ticker}...")
        data = extract_earnings_data(ticker)
        all_data[ticker] = data
        
        # Print summary
        print(f"\n{ticker} Summary:")
        print(f"  Forward EPS: {data['current_estimates']['forwardEps']}")
        print(f"  Trailing EPS: {data['current_estimates']['trailingEps']}")
        print(f"  Price Target: ${data['price_targets']['targetMeanPrice']}")
        print(f"  Current Price: ${data['price_targets']['currentPrice']}")
        print(f"  Analyst Count: {data['analyst_info']['numberOfAnalystOpinions']}")
        print(f"  Recommendation: {data['analyst_info']['recommendationKey']}")
        
        if data.get('earnings_history'):
            print(f"  Recent Earnings:")
            for eh in data['earnings_history'][:2]:
                print(f"    {eh['date']}: Est ${eh['eps_estimate']} | Act ${eh['reported_eps']} | {eh['surprise_pct']}%")
    
    # Save to JSON
    with open('research/live_earnings_data.json', 'w') as f:
        json.dump(all_data, f, indent=2, default=str)
    
    print("\n" + "="*60)
    print("[COMPLETE] Data saved to research/live_earnings_data.json")
    print("="*60)

