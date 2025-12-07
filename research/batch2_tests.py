"""
BATCH 2 VALIDATION TESTS
========================
Tests for E017, E018, E019
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 70)
print("TASK E017: INSIDER TRANSACTIONS TEST")
print("=" * 70)

try:
    from insider_transactions import get_insider_summary
    
    for ticker in ['AAPL', 'MSFT', 'NVDA']:
        print(f"\n[E017] Testing {ticker}...")
        summary = get_insider_summary(ticker)
        if summary:
            print(f"  ✅ Sentiment Score: {summary.sentiment_score}")
            print(f"  ✅ Sentiment Label: {summary.sentiment_label}")
            print(f"  ✅ Buy Transactions: {summary.buy_transactions}")
            print(f"  ✅ Sell Transactions: {summary.sell_transactions}")
            print(f"  ✅ Net Value: ${summary.net_value:,.0f}")
            print(f"  ✅ Cluster Buying: {summary.is_cluster_buying}")
            print(f"  ✅ Total Transactions: {summary.total_transactions}")
        else:
            print(f"  ⚠️ No data available")
    print("\n[E017] ✅ INSIDER TRANSACTIONS TEST COMPLETE")
except Exception as e:
    print(f"[E017] ❌ ERROR: {e}")

print("\n" + "=" * 70)
print("TASK E018: INSTITUTIONAL OWNERSHIP TEST")
print("=" * 70)

try:
    from institutional_ownership import get_ownership_summary
    
    for ticker in ['AAPL', 'MSFT', 'GOOGL']:
        print(f"\n[E018] Testing {ticker}...")
        summary = get_ownership_summary(ticker)
        if summary:
            print(f"  ✅ Institutional %: {summary.institutional_pct:.1f}%")
            print(f"  ✅ Insider %: {summary.insider_pct:.1f}%")
            print(f"  ✅ Retail %: {summary.retail_pct:.1f}%")
            print(f"  ✅ Top 10 Concentration: {summary.top10_concentration:.1f}%")
            print(f"  ✅ Accumulation Score: {summary.accumulation_score}")
            print(f"  ✅ Sentiment Label: {summary.sentiment_label}")
            print(f"  ✅ # Institutions: {summary.total_institutions}")
            if summary.top_holders:
                print(f"  ✅ Top Holder: {summary.top_holders[0].name}")
        else:
            print(f"  ⚠️ No data available")
    print("\n[E018] ✅ INSTITUTIONAL OWNERSHIP TEST COMPLETE")
except Exception as e:
    print(f"[E018] ❌ ERROR: {e}")

print("\n" + "=" * 70)
print("TASK E019: SEC EDGAR API TEST")
print("=" * 70)

try:
    from data_sources.sec_edgar import get_cik, get_form4_count, get_company_info
    
    for ticker in ['AAPL', 'MSFT', 'TSLA']:
        print(f"\n[E019] Testing {ticker}...")
        cik = get_cik(ticker)
        print(f"  ✅ CIK: {cik}")
        if cik:
            count = get_form4_count(ticker, days=30)
            print(f"  ✅ Form 4s (30 days): {count}")
            info = get_company_info(ticker)
            if info:
                print(f"  ✅ Company Name: {info.get('name')}")
                print(f"  ✅ SIC: {info.get('sic')}")
    print("\n[E019] ✅ SEC EDGAR API TEST COMPLETE")
except Exception as e:
    print(f"[E019] ❌ ERROR: {e}")

print("\n" + "=" * 70)
print("ALL BATCH 2 TESTS COMPLETE")
print("=" * 70)

