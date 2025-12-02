"""
BATCH VALIDATION TEST SUITE
============================
Test extraction and validation across expanded company set

Usage:
    python test_validation_batch.py quick    # 5 companies
    python test_validation_batch.py medium   # 20 companies
    python test_validation_batch.py full     # 50 companies
"""

import sys
import pandas as pd
from datetime import datetime
from validation_engine import DataValidator
from test_companies_expanded import QUICK_TEST, MEDIUM_TEST, FULL_TEST

def run_validation_batch(test_set_name: str):
    """
    Run validation on a test set
    
    Args:
        test_set_name: 'quick', 'medium', or 'full'
    """
    
    # Select test set
    if test_set_name == 'quick':
        tickers = QUICK_TEST
    elif test_set_name == 'medium':
        tickers = MEDIUM_TEST
    elif test_set_name == 'full':
        tickers = FULL_TEST
    else:
        print(f"❌ Unknown test set: {test_set_name}")
        print("Usage: python test_validation_batch.py [quick|medium|full]")
        return
    
    print("="*80)
    print(f"🔍 BATCH VALIDATION TEST: {test_set_name.upper()}")
    print("="*80)
    print(f"Companies: {len(tickers)}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Initialize validator
    validator = DataValidator()
    
    # Run validation
    print(f"\n[1/3] Running validation on {len(tickers)} companies...")
    results_df = validator.validate_batch(tickers)
    
    # Generate report
    print(f"\n[2/3] Generating validation report...")
    report_file = f"VALIDATION_REPORT_{test_set_name.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report = validator.generate_validation_report(results_df, report_file)
    
    # Save results CSV
    csv_file = f"validation_results_{test_set_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    results_df.to_csv(csv_file, index=False)
    print(f"✅ Results CSV saved to: {csv_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("📊 VALIDATION SUMMARY")
    print("="*80)
    print(f"\nTotal Companies: {len(results_df)}")
    print(f"✅ PASS: {len(results_df[results_df['Status'] == 'PASS'])} ({len(results_df[results_df['Status'] == 'PASS'])/len(results_df)*100:.1f}%)")
    print(f"⚠️  WARN: {len(results_df[results_df['Status'] == 'WARN'])} ({len(results_df[results_df['Status'] == 'WARN'])/len(results_df)*100:.1f}%)")
    print(f"❌ FAIL: {len(results_df[results_df['Status'] == 'FAIL'])} ({len(results_df[results_df['Status'] == 'FAIL'])/len(results_df)*100:.1f}%)")
    
    print(f"\n📈 Quality Metrics:")
    print(f"   Average Quality Score: {results_df['Quality_Score'].mean():.1f}/100")
    print(f"   Median Quality Score: {results_df['Quality_Score'].median():.1f}/100")
    print(f"   Min Quality Score: {results_df['Quality_Score'].min():.1f}/100")
    print(f"   Max Quality Score: {results_df['Quality_Score'].max():.1f}/100")
    
    print(f"\n⚠️  Issues:")
    print(f"   Total Warnings: {results_df['Warnings'].sum()}")
    print(f"   Total Errors: {results_df['Errors'].sum()}")
    
    # Show failed companies
    failed = results_df[results_df['Status'] == 'FAIL']
    if len(failed) > 0:
        print(f"\n❌ FAILED VALIDATIONS ({len(failed)}):")
        for _, row in failed.iterrows():
            print(f"   - {row['Ticker']}: Quality Score {row['Quality_Score']}/100 ({row['Errors']} errors)")
    
    # Show warned companies
    warned = results_df[results_df['Status'] == 'WARN']
    if len(warned) > 0:
        print(f"\n⚠️  WARNINGS ({len(warned)}):")
        for _, row in warned.iterrows():
            print(f"   - {row['Ticker']}: Quality Score {row['Quality_Score']}/100 ({row['Warnings']} warnings)")
    
    print("\n" + "="*80)
    print(f"[3/3] Validation complete!")
    print(f"Report saved to: {report_file}")
    print("="*80)
    
    # Return pass rate for automated testing
    pass_rate = len(results_df[results_df['Status'] == 'PASS']) / len(results_df)
    
    # Exit code based on pass rate
    if pass_rate >= 0.90:  # 90%+ pass
        print("\n✅ VALIDATION PASSED: 90%+ companies validated successfully")
        sys.exit(0)
    elif pass_rate >= 0.75:  # 75-90% pass
        print("\n⚠️  VALIDATION WARNING: 75-90% companies validated, review warnings")
        sys.exit(0)  # Still exit 0, but with warning
    else:  # < 75% pass
        print("\n❌ VALIDATION FAILED: < 75% companies validated successfully")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_validation_batch.py [quick|medium|full]")
        print("\nTest Sets:")
        print(f"  quick  - {len(QUICK_TEST)} companies (5 min)")
        print(f"  medium - {len(MEDIUM_TEST)} companies (15 min)")
        print(f"  full   - {len(FULL_TEST)} companies (45 min)")
        sys.exit(1)
    
    test_set = sys.argv[1].lower()
    run_validation_batch(test_set)


