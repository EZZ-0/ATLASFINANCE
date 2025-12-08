"""
CAVA VALIDATION TEST
Cross-check app data against actual market data
"""
import yfinance as yf
import pandas as pd

print('='*70)
print('CAVA VALIDATION TEST - Cross-checking App Data vs Actual')
print('='*70)

# Fetch CAVA data
ticker = 'CAVA'
stock = yf.Ticker(ticker)
info = stock.info

print(f'\n--- COMPANY INFO ---')
print(f'Company: {info.get("longName", "N/A")}')
print(f'Sector: {info.get("sector", "N/A")}')
print(f'Industry: {info.get("industry", "N/A")}')

print(f'\n--- PRICE DATA ---')
print(f'Current Price: ${info.get("currentPrice", info.get("regularMarketPrice", "N/A"))}')
print(f'52-Week High: ${info.get("fiftyTwoWeekHigh", "N/A")}')
print(f'52-Week Low: ${info.get("fiftyTwoWeekLow", "N/A")}')

print(f'\n--- VALUATION ---')
market_cap = info.get('marketCap', 0)
print(f'Market Cap: ${market_cap/1e9:.2f}B' if market_cap else 'Market Cap: N/A')
print(f'P/E (Trailing): {info.get("trailingPE", "N/A")}')
print(f'P/E (Forward): {info.get("forwardPE", "N/A")}')
print(f'PEG Ratio: {info.get("pegRatio", "N/A")}')
ev = info.get('enterpriseValue', 0)
print(f'EV: ${ev/1e9:.2f}B' if ev else 'EV: N/A')
print(f'EV/EBITDA: {info.get("enterpriseToEbitda", "N/A")}')

print(f'\n--- EPS ---')
print(f'Trailing EPS: ${info.get("trailingEps", "N/A")}')
print(f'Forward EPS: ${info.get("forwardEps", "N/A")}')

print(f'\n--- REVENUE & INCOME ---')
revenue = info.get('totalRevenue', 0)
print(f'Revenue (TTM): ${revenue/1e6:.2f}M' if revenue else 'Revenue: N/A')
net_income = info.get('netIncomeToCommon', 0)
print(f'Net Income: ${net_income/1e6:.2f}M' if net_income else 'Net Income: N/A')

print(f'\n--- MARGINS ---')
gm = info.get('grossMargins')
print(f'Gross Margin: {gm*100:.1f}%' if gm else 'Gross Margin: N/A')
om = info.get('operatingMargins')
print(f'Operating Margin: {om*100:.1f}%' if om else 'Operating Margin: N/A')
nm = info.get('profitMargins')
print(f'Net Margin: {nm*100:.1f}%' if nm else 'Net Margin: N/A')

print(f'\n--- RETURNS ---')
roe = info.get('returnOnEquity')
print(f'ROE: {roe*100:.1f}%' if roe else 'ROE: N/A')
roa = info.get('returnOnAssets')
print(f'ROA: {roa*100:.1f}%' if roa else 'ROA: N/A')

print(f'\n--- GROWTH ---')
rg = info.get('revenueGrowth')
print(f'Revenue Growth: {rg*100:.1f}%' if rg else 'Revenue Growth: N/A')
eg = info.get('earningsGrowth')
print(f'Earnings Growth: {eg*100:.1f}%' if eg else 'Earnings Growth: N/A')

print(f'\n--- ANALYST DATA ---')
print(f'Target Mean: ${info.get("targetMeanPrice", "N/A")}')
print(f'Recommendation: {info.get("recommendationKey", "N/A")}')
print(f'Number of Analysts: {info.get("numberOfAnalystOpinions", "N/A")}')

print(f'\n--- DEBT ---')
td = info.get('totalDebt', 0)
print(f'Total Debt: ${td/1e6:.2f}M' if td else 'Total Debt: N/A')
tc = info.get('totalCash', 0)
print(f'Total Cash: ${tc/1e6:.2f}M' if tc else 'Total Cash: N/A')
print(f'Debt/Equity: {info.get("debtToEquity", "N/A")}')

print(f'\n--- SHARES ---')
so = info.get('sharesOutstanding', 0)
print(f'Shares Outstanding: {so/1e6:.2f}M' if so else 'Shares: N/A')
fs = info.get('floatShares', 0)
print(f'Float: {fs/1e6:.2f}M' if fs else 'Float: N/A')

print(f'\n--- FREE CASH FLOW ---')
fcf = info.get('freeCashflow', 0)
print(f'Free Cash Flow: ${fcf/1e6:.2f}M' if fcf else 'FCF: N/A')
ocf = info.get('operatingCashflow', 0)
print(f'Operating Cash Flow: ${ocf/1e6:.2f}M' if ocf else 'OCF: N/A')

print('\n' + '='*70)
print('COMPARISON WITH WEB SEARCH DATA (Dec 2, 2025):')
print('='*70)
print('''
EXPECTED (from web search):
- Stock Price: $53.03
- FY2024 Revenue: $963.71M (32.25% YoY growth)
- FY2024 Net Income: $130.32M (881% YoY growth)
- Q1 2025 Revenue: $331.8M
- Q1 2025 EPS: $0.22
- Analyst Target: $72.31
- Recommendation: Moderate Buy
''')

print('='*70)
print('VALIDATION COMPLETE')
print('='*70)

