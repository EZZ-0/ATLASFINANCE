"""Quick test to see yfinance data structure"""
import yfinance as yf

ticker = yf.Ticker("AAPL")
income = ticker.financials
balance = ticker.balance_sheet

print("Income Statement Index (first 10):")
print(income.index[:10].tolist())
print("\nBalance Sheet Index (first 10):")
print(balance.index[:10].tolist())

print("\n\nFirst column of income:")
print(income.iloc[:, 0].head(20))

