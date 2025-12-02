"""Test Forensic Shield Implementation"""
from usa_backend import quick_extract
from forensic_shield import analyze_forensic_shield

print("="*80)
print("TESTING FORENSIC SHIELD ON AAPL")
print("="*80)

# Extract AAPL data
print("\n[1/4] Extracting AAPL data...")
data = quick_extract('AAPL', fiscal_year_offset=0)

if not data:
    print("[FAIL] Extraction failed")
    exit(1)

print(f"[OK] Extraction complete")

# Run Forensic Shield
print("\n[2/4] Running Forensic Shield analysis...")
results = analyze_forensic_shield(data)

# Test 1: Altman Z-Score
print("\n" + "-"*80)
print("TEST 1: ALTMAN Z-SCORE (Bankruptcy Risk)")
print("-"*80)
altman = results['altman_z_score']
if altman['status'] == 'success':
    print(f"Z-Score:        {altman['z_score']:.2f}")
    print(f"Zone:           {altman['zone']}")
    print(f"Risk Level:     {altman['risk_level']}")
    print(f"Interpretation: {altman['interpretation']}")
    print("\nComponents:")
    for key, value in altman['components'].items():
        print(f"  {key}: {value:.4f}")
else:
    print(f"[FAIL] {altman['message']}")

# Test 2: Beneish M-Score
print("\n" + "-"*80)
print("TEST 2: BENEISH M-SCORE (Earnings Manipulation)")
print("-"*80)
beneish = results['beneish_m_score']
if beneish['status'] == 'success':
    print(f"M-Score:        {beneish['m_score']:.4f}")
    print(f"Risk Level:     {beneish['risk_level']}")
    print(f"Interpretation: {beneish['interpretation']}")
    if beneish.get('warning'):
        print(f"WARNING:        {beneish['warning']}")
    if beneish.get('red_flags'):
        print("\nRed Flags:")
        for flag in beneish['red_flags']:
            print(f"  - {flag}")
    print("\nComponents:")
    for key, value in beneish['components'].items():
        print(f"  {key}: {value:.4f}")
else:
    print(f"[FAIL] {beneish['message']}")

# Test 3: Piotroski F-Score
print("\n" + "-"*80)
print("TEST 3: PIOTROSKI F-SCORE (Quality Assessment)")
print("-"*80)
piotroski = results['piotroski_f_score']
if piotroski['status'] == 'success':
    print(f"F-Score:        {piotroski['f_score']}/{piotroski['max_score']}")
    print(f"Quality:        {piotroski['quality']}")
    print(f"Interpretation: {piotroski['interpretation']}")
    print("\nBreakdown:")
    for test, passed in piotroski['breakdown'].items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"  {status} {test}")
else:
    print(f"[FAIL] {piotroski.get('message', 'Unknown error')}")

# Overall Assessment
print("\n" + "="*80)
print("OVERALL FORENSIC ASSESSMENT")
print("="*80)
overall = results['overall_assessment']
print(f"Risk Level: {overall['risk_level']}")
print(f"Summary: {overall['summary']}")
if overall.get('risk_factors'):
    print("\nRisk Factors:")
    for factor in overall['risk_factors']:
        print(f"  - {factor}")

print("\n[3/4] Forensic Shield test complete!")
print("="*80)






