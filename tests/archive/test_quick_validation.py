"""
QUICK VALIDATION TEST
=====================
Test that the bulletproof test suite is working correctly.
Tests only AAPL (fast) to validate all our improvements.
"""

import sys
import time
from test_comprehensive_engine import ComprehensiveEngineTester

def quick_test():
    """Quick validation with just AAPL"""
    print("\n" + "="*80)
    print("BULLETPROOF TEST SUITE - QUICK VALIDATION")
    print("Testing AAPL only to validate improvements")
    print("="*80 + "\n")
    
    tester = ComprehensiveEngineTester()
    
    # Test just AAPL
    success = tester.test_company('AAPL')
    
    # Run meta-test
    print("\n" + "="*80)
    print("Running Meta-Test (Test the Tests)")
    print("="*80)
    tester.test_the_tests()
    
    # Quick summary
    print("\n" + "="*80)
    print("QUICK VALIDATION SUMMARY")
    print("="*80)
    
    total = tester.results['tests_run']
    passed = tester.results['tests_passed']
    failed = tester.results['tests_failed']
    warned = tester.results['tests_warnings']
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed:   {passed} ({passed/total*100:.1f}%)")
    print(f"⚠️  Warnings: {warned} ({warned/total*100:.1f}%)")
    print(f"❌ Failed:   {failed} ({failed/total*100:.1f}%)")
    
    if failed == 0:
        print("\n🎉 SUCCESS! All tests passing - bulletproof improvements working!")
        return True
    else:
        print(f"\n⚠️  {failed} tests failed - need fixes")
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)




