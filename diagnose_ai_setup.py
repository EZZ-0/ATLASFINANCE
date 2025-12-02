"""
Quick diagnostic to check AI setup
"""
import os
from dotenv import load_dotenv

print("=" * 50)
print("AI SETUP DIAGNOSTIC")
print("=" * 50)
print()

# Load .env
print("1. Loading .env file...")
load_dotenv()
print("   ✓ dotenv loaded")
print()

# Check Gemini key
print("2. Checking Gemini API key...")
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    print(f"   ✓ Found: {gemini_key[:10]}...{gemini_key[-4:]}")
else:
    print("   ✗ NOT FOUND - Create .env file!")
    print("   Copy contents from: CREATE_DOT_ENV_FILE.txt")
print()

# Check if google-generativeai is installed
print("3. Checking google-generativeai package...")
try:
    import google.generativeai as genai
    print("   ✓ Package installed")
    
    # Try to initialize
    if gemini_key:
        print("4. Testing Gemini connection...")
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("   ✓ Gemini initialized successfully!")
            
            # Quick test
            print("5. Testing AI response...")
            response = model.generate_content("Say 'Hello'")
            print(f"   ✓ Response: {response.text}")
            
        except Exception as e:
            print(f"   ✗ Gemini error: {e}")
    else:
        print("4. Skipping Gemini test (no API key)")
        
except ImportError:
    print("   ✗ Package not installed")
    print("   Run: pip install google-generativeai")
print()

# Check financial_ai.py
print("6. Testing FinancialAI class...")
try:
    from financial_ai import FinancialAI
    print("   ✓ financial_ai.py imports correctly")
    
    ai = FinancialAI(tier='free')
    print("   ✓ FinancialAI initialized")
    
    # Check which models loaded
    if hasattr(ai, 'primary_model') and ai.primary_model:
        print("   ✓ Primary model (Gemini) loaded")
    else:
        print("   ✗ Primary model (Gemini) NOT loaded")
        
    if hasattr(ai, 'fallback_model') and ai.fallback_model:
        print("   ✓ Fallback model (Ollama) loaded")
    else:
        print("   ⚠ Fallback model (Ollama) not available (optional)")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
print()

print("=" * 50)
print("DIAGNOSTIC COMPLETE")
print("=" * 50)
print()

print("NEXT STEPS:")
print("1. If .env missing: Copy CREATE_DOT_ENV_FILE.txt to .env")
print("2. If package missing: pip install google-generativeai")
print("3. If all OK: Run streamlit run usa_app.py")


