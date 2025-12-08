"""
CRASH/TIMEOUT DIAGNOSTIC
========================
Identify why tests are timing out and causing crashes.
"""

import sys
import os
import traceback
from datetime import datetime

def diagnose():
    """Run diagnostic to find issues"""
    
    print("="*80)
    print("CRASH/TIMEOUT DIAGNOSTIC")
    print("="*80)
    print(f"Started: {datetime.now()}")
    
    issues_found = []
    
    # Check 1: Import test
    print("\n[1/6] Testing imports...")
    try:
        from usa_backend import USAFinancialExtractor
        from dcf_modeling import DCFModel
        from quant_engine import QuantEngine
        import test_config
        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import error: {e}")
        issues_found.append(f"Import Error: {e}")
        traceback.print_exc()
    
    # Check 2: Backend initialization
    print("\n[2/6] Testing backend initialization...")
    try:
        extractor = USAFinancialExtractor()
        print("✅ Backend initialized")
    except Exception as e:
        print(f"❌ Backend init error: {e}")
        issues_found.append(f"Backend Init Error: {e}")
        traceback.print_exc()
    
    # Check 3: Quick data fetch (timeout test)
    print("\n[3/6] Testing quick data fetch (30s timeout)...")
    try:
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Fetch took >30s")
        
        # Set alarm (Unix only - Windows will skip)
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
        except:
            print("⚠️  Timeout check skipped (Windows)")
        
        data = extractor.extract_financials('AAPL')  # FIXED: correct method name
        
        try:
            signal.alarm(0)  # Cancel alarm
        except:
            pass
            
        if data:
            print(f"✅ Data fetched successfully ({len(str(data))} bytes)")
        else:
            print("⚠️  Data fetch returned empty")
            issues_found.append("Empty data returned")
            
    except TimeoutError:
        print("❌ TIMEOUT: Data fetch took >30 seconds")
        issues_found.append("Data fetch timeout >30s")
    except Exception as e:
        print(f"❌ Data fetch error: {e}")
        issues_found.append(f"Data Fetch Error: {e}")
        traceback.print_exc()
    
    # Check 4: Log file size check
    print("\n[4/6] Checking for oversized log files...")
    try:
        large_files = []
        for root, dirs, files in os.walk('.'):
            # Skip venv/cache
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', 'env', '.venv'}]
            
            for file in files:
                if file.endswith(('.log', '.txt', '.md')) and not file.startswith('merge'):
                    filepath = os.path.join(root, file)
                    try:
                        size = os.path.getsize(filepath)
                        if size > 10_000_000:  # >10MB
                            large_files.append((filepath, size / 1_000_000))
                    except:
                        pass
        
        if large_files:
            print(f"⚠️  Found {len(large_files)} large files:")
            for filepath, size_mb in sorted(large_files, key=lambda x: x[1], reverse=True)[:10]:
                print(f"    - {filepath}: {size_mb:.1f} MB")
                issues_found.append(f"Large file: {filepath} ({size_mb:.1f} MB)")
        else:
            print("✅ No oversized log files")
            
    except Exception as e:
        print(f"⚠️  Log check error: {e}")
    
    # Check 5: Memory usage estimate
    print("\n[5/6] Checking memory usage...")
    try:
        import psutil
        process = psutil.Process()
        mem_mb = process.memory_info().rss / 1_000_000
        print(f"ℹ️  Current memory usage: {mem_mb:.1f} MB")
        
        if mem_mb > 1000:
            print("⚠️  High memory usage detected")
            issues_found.append(f"High memory usage: {mem_mb:.1f} MB")
        else:
            print("✅ Memory usage normal")
    except ImportError:
        print("⚠️  psutil not installed, skipping memory check")
    except Exception as e:
        print(f"⚠️  Memory check error: {e}")
    
    # Check 6: Test config sanity
    print("\n[6/6] Checking test configuration...")
    try:
        import test_config
        print(f"ℹ️  Test companies: {len(test_config.TEST_COMPANIES)}")
        print(f"ℹ️  Validation thresholds: {len(test_config.VALIDATION_THRESHOLDS)} categories")
        print("✅ Test config valid")
    except Exception as e:
        print(f"❌ Test config error: {e}")
        issues_found.append(f"Test Config Error: {e}")
        traceback.print_exc()
    
    # Summary
    print("\n" + "="*80)
    print("DIAGNOSTIC SUMMARY")
    print("="*80)
    
    if issues_found:
        print(f"\n❌ Found {len(issues_found)} issue(s):")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        print("\n🔧 RECOMMENDED ACTIONS:")
        
        if any('timeout' in str(i).lower() for i in issues_found):
            print("   - Optimize data fetching (add caching)")
            print("   - Run tests with smaller company set first")
            
        if any('large file' in str(i).lower() for i in issues_found):
            print("   - Clean up large log files")
            print("   - Add log rotation")
            
        if any('memory' in str(i).lower() for i in issues_found):
            print("   - Process companies individually")
            print("   - Clear caches between tests")
            
        return False
    else:
        print("\n✅ NO CRITICAL ISSUES FOUND")
        print("System appears healthy. Crashes may be due to:")
        print("   - External factors (network, API limits)")
        print("   - Cursor resource limits")
        print("   - Test suite complexity (381 metrics × 17 companies)")
        return True

if __name__ == "__main__":
    success = diagnose()
    sys.exit(0 if success else 1)

