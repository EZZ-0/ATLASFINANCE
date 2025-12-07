"""
YFINANCE EARNINGS RESEARCH SCRIPT
Task: E011 - Research yfinance Earnings Fields
"""

import yfinance as yf

def research_ticker(ticker):
    print(f"\n{'='*60}")
    print(f"YFINANCE EARNINGS RESEARCH - {ticker}")
    print('='*60)
    
    stock = yf.Ticker(ticker)
    
    # 1. Earnings Dates
    print('\n1. EARNINGS_DATES:')
    try:
        ed = stock.earnings_dates
        if ed is not None and not ed.empty:
            print(f'  Type: {type(ed).__name__}')
            print(f'  Shape: {ed.shape}')
            print(f'  Columns: {list(ed.columns)}')
            print('  Sample (head 5):')
            print(ed.head(5).to_string())
        else:
            print('  No data available')
    except Exception as e:
        print(f'  Error: {e}')
    
    # 2. Earnings History
    print('\n2. EARNINGS_HISTORY:')
    try:
        eh = stock.earnings_history
        if eh is not None:
            print(f'  Type: {type(eh).__name__}')
            print(f'  Data: {eh}')
        else:
            print('  No data available')
    except Exception as e:
        print(f'  Error: {e}')
    
    # 3. Analyst Price Targets
    print('\n3. ANALYST_PRICE_TARGETS:')
    try:
        apt = stock.analyst_price_targets
        if apt is not None:
            print(f'  Type: {type(apt).__name__}')
            print(f'  Data: {apt}')
        else:
            print('  No data available')
    except Exception as e:
        print(f'  Error: {e}')
    
    # 4. Recommendations
    print('\n4. RECOMMENDATIONS:')
    try:
        rec = stock.recommendations
        if rec is not None and not rec.empty:
            print(f'  Type: {type(rec).__name__}')
            print(f'  Shape: {rec.shape}')
            print(f'  Columns: {list(rec.columns)}')
            print('  Sample (tail 5):')
            print(rec.tail(5).to_string())
        else:
            print('  No data available')
    except Exception as e:
        print(f'  Error: {e}')
    
    # 5. Info - EPS related fields
    print('\n5. INFO (EPS/Earnings related fields):')
    try:
        info = stock.info
        eps_fields = [
            'forwardEps', 'trailingEps', 'earningsGrowth', 'earningsQuarterlyGrowth',
            'targetMeanPrice', 'targetHighPrice', 'targetLowPrice', 'numberOfAnalystOpinions',
            'recommendationMean', 'recommendationKey', 'currentPrice', 'fiftyTwoWeekHigh',
            'fiftyTwoWeekLow', 'forwardPE', 'trailingPE', 'priceToBook'
        ]
        for field in eps_fields:
            value = info.get(field, 'N/A')
            print(f'  {field}: {value}')
    except Exception as e:
        print(f'  Error: {e}')
    
    # 6. Calendar (Earnings Date)
    print('\n6. CALENDAR:')
    try:
        cal = stock.calendar
        if cal is not None:
            print(f'  Type: {type(cal).__name__}')
            print(f'  Data: {cal}')
        else:
            print('  No data available')
    except Exception as e:
        print(f'  Error: {e}')
    
    # 7. Upgrades/Downgrades
    print('\n7. UPGRADES_DOWNGRADES:')
    try:
        ud = stock.upgrades_downgrades
        if ud is not None and not ud.empty:
            print(f'  Type: {type(ud).__name__}')
            print(f'  Shape: {ud.shape}')
            print(f'  Columns: {list(ud.columns)}')
            print('  Sample (tail 5):')
            print(ud.tail(5).to_string())
        else:
            print('  No data available')
    except Exception as e:
        print(f'  Error: {e}')
    
    print('\n' + '='*60)

if __name__ == "__main__":
    for ticker in ['AAPL', 'MSFT', 'GOOGL']:
        research_ticker(ticker)
    
    print("\n[RESEARCH COMPLETE]")

