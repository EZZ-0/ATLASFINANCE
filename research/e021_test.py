"""E021: Test ownership change detection"""
import yfinance as yf

print("=" * 60)
print("E021: OWNERSHIP CHANGE DETECTION TEST")
print("=" * 60)

for ticker in ['AAPL', 'MSFT', 'NVDA']:
    stock = yf.Ticker(ticker)
    holders = stock.institutional_holders
    
    if holders is not None and not holders.empty:
        print(f"\n{ticker} Top 5 Holders with Quarter Changes:")
        print("-" * 50)
        
        for i, row in holders.head(5).iterrows():
            holder = str(row['Holder'])[:35]
            change = row.get('pctChange', None)
            
            if change is not None:
                if change > 0.05:
                    signal = "ACCUMULATING 📈"
                elif change < -0.05:
                    signal = "DISTRIBUTING 📉"
                else:
                    signal = "HOLDING ➡️"
                print(f"  {holder}: {change:+.1%} {signal}")
            else:
                print(f"  {holder}: N/A")
    print()

print("=" * 60)
print("CHANGE DETECTION SUMMARY")
print("=" * 60)

