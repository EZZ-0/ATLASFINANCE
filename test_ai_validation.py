"""
AI VALIDATION TEST SUITE
=========================
Specialized tests to validate AI response quality
Try to break the AI and catch errors
"""

import sys
from financial_ai import FinancialAI, explain_metric

class AIValidationTests:
    """
    Test suite to validate AI quality and catch issues
    """
    
    def __init__(self):
        self.ai = FinancialAI(tier='free')
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
    
    def test_trick_questions(self):
        """Questions designed to catch hallucinations"""
        print("\n" + "="*80)
        print("TEST 1: Trick Questions (Hallucination Detection)")
        print("="*80)
        
        trick_tests = [
            {
                'question': "What's Tesla's dividend yield?",
                'data': {'ticker': 'TSLA', 'company_name': 'Tesla', 'dividend_yield': 0},
                'expected_keywords': ['no dividend', 'does not pay', '0%'],
                'name': 'Non-existent dividend'
            },
            {
                'question': "Is a P/E ratio of -50 good or bad?",
                'data': {'ticker': 'TEST', 'pe_ratio': -50},
                'expected_keywords': ['negative', 'loss', 'not profitable'],
                'name': 'Negative P/E logic'
            },
        ]
        
        for test in trick_tests:
            self.tests_run += 1
            print(f"\n🧪 Testing: {test['name']}")
            print(f"   Question: {test['question']}")
            
            result = self.ai.ask(test['question'], test['data'])
            response_lower = result['response'].lower()
            
            # Check if expected keywords present
            found = any(keyword in response_lower for keyword in test['expected_keywords'])
            
            if found:
                print(f"   ✅ PASS - AI correctly handled trick question")
                print(f"   Confidence: {result['confidence']}%")
                self.tests_passed += 1
            else:
                print(f"   ❌ FAIL - AI may have hallucinated")
                print(f"   Response: {result['response'][:200]}...")
                self.tests_failed += 1
    
    def test_math_accuracy(self):
        """Verify AI calculates and reports correctly"""
        print("\n" + "="*80)
        print("TEST 2: Math Accuracy")
        print("="*80)
        
        math_tests = [
            {
                'question': "What is the P/E ratio?",
                'data': {'ticker': 'AAPL', 'pe_ratio': 28.5, 'price': 195.50},
                'expected_value': 28.5,
                'tolerance': 0.5,
                'name': 'P/E ratio accuracy'
            },
        ]
        
        for test in math_tests:
            self.tests_run += 1
            print(f"\n🧪 Testing: {test['name']}")
            print(f"   Expected: {test['expected_value']}")
            
            result = self.ai.ask(test['question'], test['data'])
            
            # Extract numbers from response
            import re
            numbers = re.findall(r'[\d]+\.?[\d]*', result['response'])
            numbers = [float(n) for n in numbers if n]
            
            # Check if expected value is close to any number in response
            found_match = any(
                abs(num - test['expected_value']) <= test['tolerance']
                for num in numbers
            )
            
            if found_match:
                print(f"   ✅ PASS - Math is accurate")
                self.tests_passed += 1
            else:
                print(f"   ❌ FAIL - Numbers don't match")
                print(f"   Found numbers: {numbers}")
                self.tests_failed += 1
    
    def test_consistency(self):
        """Ask same question differently, check consistency"""
        print("\n" + "="*80)
        print("TEST 3: Response Consistency")
        print("="*80)
        
        self.tests_run += 1
        
        test_data = {
            'ticker': 'AAPL',
            'company_name': 'Apple Inc.',
            'pe_ratio': 28.5,
            'sector': 'Technology'
        }
        
        # Ask same thing two different ways
        q1 = "Is Apple's P/E ratio high?"
        q2 = "Is a P/E of 28.5 expensive for a tech stock?"
        
        print(f"\n🧪 Testing consistency")
        print(f"   Q1: {q1}")
        print(f"   Q2: {q2}")
        
        r1 = self.ai.ask(q1, test_data)
        r2 = self.ai.ask(q2, test_data)
        
        # Check if both agree it's relatively high
        high_keywords = ['high', 'expensive', 'premium', 'above average']
        
        r1_says_high = any(kw in r1['response'].lower() for kw in high_keywords)
        r2_says_high = any(kw in r2['response'].lower() for kw in high_keywords)
        
        if r1_says_high == r2_says_high:
            print(f"   ✅ PASS - Responses are consistent")
            self.tests_passed += 1
        else:
            print(f"   ❌ FAIL - Contradictory responses")
            self.tests_failed += 1
    
    def test_edge_cases(self):
        """Test special cases: banks, negative earnings, etc."""
        print("\n" + "="*80)
        print("TEST 4: Edge Cases")
        print("="*80)
        
        edge_tests = [
            {
                'question': "Analyze this bank's financials",
                'data': {
                    'ticker': 'JPM',
                    'company_name': 'JPMorgan',
                    'sector': 'Finance',
                    'current_ratio': 0.9  # Banks have low current ratios
                },
                'expected_keywords': ['bank', 'financial', 'different'],
                'name': 'Bank special accounting'
            },
        ]
        
        for test in edge_tests:
            self.tests_run += 1
            print(f"\n🧪 Testing: {test['name']}")
            
            result = self.ai.ask(test['question'], test['data'])
            response_lower = result['response'].lower()
            
            found = any(keyword in response_lower for keyword in test['expected_keywords'])
            
            if found:
                print(f"   ✅ PASS - Handled edge case correctly")
                self.tests_passed += 1
            else:
                print(f"   ⚠️  WARN - May not handle edge case properly")
                print(f"   Response: {result['response'][:200]}...")
                self.tests_failed += 1
    
    def test_validation_layer(self):
        """Test that validation catches issues"""
        print("\n" + "="*80)
        print("TEST 5: Validation Layer")
        print("="*80)
        
        self.tests_run += 1
        
        # Create data with obvious issues
        bad_data = {
            'ticker': 'TEST',
            'pe_ratio': -50,  # Negative (unusual)
            'growth_rate': 500,  # Impossible growth
            'roe': 9999  # Impossible ROE
        }
        
        print(f"\n🧪 Testing validation with bad data")
        result = self.ai.ask("Analyze this company", bad_data)
        
        # Check if validation caught issues
        if result['warnings'] or result['confidence'] < 90:
            print(f"   ✅ PASS - Validation layer working")
            print(f"   Confidence: {result['confidence']}%")
            print(f"   Warnings: {result['warnings']}")
            self.tests_passed += 1
        else:
            print(f"   ❌ FAIL - Validation didn't catch obvious issues")
            self.tests_failed += 1
    
    def test_explanation_brevity(self):
        """Test inline explanations are concise"""
        print("\n" + "="*80)
        print("TEST 6: Explanation Brevity (Inline Tooltips)")
        print("="*80)
        
        self.tests_run += 1
        
        test_data = {
            'ticker': 'AAPL',
            'pe_ratio': 28.5,
            'sector': 'Technology'
        }
        
        print(f"\n🧪 Testing inline explanation length")
        explanation = explain_metric("P/E Ratio", 28.5, test_data, self.ai)
        
        words = len(explanation.split())
        
        print(f"   Explanation length: {words} words")
        
        if 30 <= words <= 100:  # Should be 2-4 sentences
            print(f"   ✅ PASS - Explanation is appropriately concise")
            self.tests_passed += 1
        else:
            print(f"   ⚠️  WARN - Explanation may be too {'long' if words > 100 else 'short'}")
            self.tests_failed += 1
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("\n" + "="*80)
        print("AI FINANCIAL ADVISOR - VALIDATION TEST SUITE")
        print("="*80)
        print("Testing AI quality, accuracy, and reliability")
        print()
        
        # Run tests
        self.test_trick_questions()
        self.test_math_accuracy()
        self.test_consistency()
        self.test_edge_cases()
        self.test_validation_layer()
        self.test_explanation_brevity()
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Tests Run:    {self.tests_run}")
        print(f"✅ Passed:     {self.tests_passed} ({self.tests_passed/self.tests_run*100:.1f}%)")
        print(f"❌ Failed:     {self.tests_failed} ({self.tests_failed/self.tests_run*100:.1f}%)")
        print()
        
        if self.tests_failed == 0:
            print("🎉 ALL TESTS PASSED - AI is working correctly!")
            return True
        else:
            print(f"⚠️  {self.tests_failed} test(s) failed - review results above")
            return False


if __name__ == "__main__":
    tester = AIValidationTests()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


