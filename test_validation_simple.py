"""
SIMPLE VALIDATION TEST
======================
Quick test to ensure validation engine works correctly
Tests just 1 company (AAPL) to verify functionality
"""

from validation_engine import quick_validate, DataValidator
from test_companies_expanded import QUICK_TEST

def test_single_company():
    """Test validation on a single company"""
    print("="*60)
    print("SIMPLE VALIDATION TEST")
    print("="*60)
    print("\nTesting: AAPL (known-good baseline)")
    print("-"*60)
    
    try:
        report = quick_validate("AAPL")
        
        print("\n✅ VALIDATION ENGINE WORKS!")
        print(f"   Status: {report['overall_status']}")
        print(f"   Quality Score: {report['quality_score']}/100")
        
        return True
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_single_company()
    
    if success:
        print("\n" + "="*60)
        print("✅ VALIDATION ENGINE READY")
        print("="*60)
        print("\nNext steps:")
        print("  python test_validation_batch.py quick   # 5 companies")
        print("  python test_validation_batch.py medium  # 20 companies")
        print("  python test_validation_batch.py full    # 50 companies")
    else:
        print("\n❌ Fix errors before proceeding")

