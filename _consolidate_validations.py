"""Consolidate all validation files into one master JSON"""
import json

# Load all validation files
validations = {}
companies = ['AAPL', 'FIVE', 'MSFT', 'JPM', 'TSLA', 'WMT', 'NVDA']

for company in companies:
    try:
        with open(f'validation_truth_{company}.json', 'r') as f:
            validations[company] = json.load(f)
        print(f"[OK] Loaded {company}")
    except Exception as e:
        print(f"[ERROR] Failed to load {company}: {e}")

# Write consolidated file
with open('FINANCIAL_DATA_VALIDATIONS.json', 'w') as f:
    json.dump(validations, f, indent=2)

print(f"\n[SUCCESS] Consolidated {len(validations)} companies into FINANCIAL_DATA_VALIDATIONS.json")






