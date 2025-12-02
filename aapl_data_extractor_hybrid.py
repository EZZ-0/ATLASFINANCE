"""
AAPL Financial Data Extractor - HYBRID APPROACH
================================================
1. Try Excel extraction first (smart mapping)
2. Fall back to PDF extraction if Excel fails
3. Generate validation_truth_AAPL_FILLED.json

Usage: python aapl_data_extractor_hybrid.py
"""

import pandas as pd
import json
import re
from typing import Dict, Any, List, Tuple, Optional

# ============================================================================
# EXCEL EXTRACTION (PRIMARY METHOD)
# ============================================================================

def analyze_excel_structure(file_path: str = "AAPL_Financial_Report_20251127.xlsx") -> Optional[pd.ExcelFile]:
    """Analyze Excel file structure"""
    try:
        print("="*80)
        print("METHOD 1: EXCEL EXTRACTION")
        print("="*80)
        
        excel_file = pd.ExcelFile(file_path)
        
        print(f"\n[OK] Loaded Excel file: {len(excel_file.sheet_names)} sheets")
        print("\nSheet Preview:")
        for i, sheet in enumerate(excel_file.sheet_names[:10], 1):
            print(f"  {i}. {sheet}")
        
        if len(excel_file.sheet_names) > 10:
            print(f"  ... and {len(excel_file.sheet_names) - 10} more")
        
        return excel_file
    
    except Exception as e:
        print(f"[FAIL] Excel loading failed: {e}")
        return None

def smart_find_value(df: pd.DataFrame, search_terms: List[str]) -> Tuple[float, str]:
    """
    Smart value finder - searches entire DataFrame for keywords
    Handles various formats and locations
    """
    # Convert entire DataFrame to string for searching
    df_str = df.astype(str)
    
    for term in search_terms:
        # Search in all cells
        for col in df_str.columns:
            for idx, cell in df_str[col].items():
                if term.lower() in cell.lower():
                    # Found the label! Now find the corresponding value
                    
                    # Strategy 1: Look in the same row, next few columns
                    try:
                        row = df.iloc[idx]
                        for i in range(len(row)):
                            val = row.iloc[i]
                            if pd.notna(val) and val != cell:
                                # Try to parse as number
                                try:
                                    # Handle various formats
                                    if isinstance(val, (int, float)):
                                        return float(val), f"{term} (same row)"
                                    
                                    # String parsing
                                    if isinstance(val, str):
                                        # Remove formatting
                                        cleaned = val.replace(',', '').replace('$', '').replace('(', '-').replace(')', '').strip()
                                        # Try to convert
                                        if cleaned and cleaned != 'nan':
                                            num = float(cleaned)
                                            if abs(num) > 0.01:  # Skip zeros
                                                return num, f"{term} (parsed)"
                                except:
                                    continue
                    except:
                        pass
                    
                    # Strategy 2: Look in the next row, same column
                    try:
                        if idx + 1 < len(df):
                            next_val = df.iloc[idx + 1][col]
                            if pd.notna(next_val):
                                if isinstance(next_val, (int, float)):
                                    return float(next_val), f"{term} (next row)"
                    except:
                        pass
    
    return 0.0, "NOT_FOUND"

def extract_from_excel(excel_file: pd.ExcelFile) -> Dict[str, float]:
    """Extract all metrics from Excel"""
    print("\n" + "-"*80)
    print("EXTRACTING FINANCIAL METRICS FROM EXCEL")
    print("-"*80)
    
    extracted = {}
    
    # Define all metrics we need with multiple possible names
    metrics = {
        # Income Statement
        'total_revenue': ['total net sales', 'total revenue', 'net sales', 'products revenue', 'services revenue total'],
        'cost_of_revenue': ['cost of sales', 'cost of revenue', 'cost of products', 'cost of services'],
        'gross_profit': ['gross margin', 'gross profit'],
        'research_development': ['research and development', 'r&d'],
        'operating_income': ['operating income', 'income from operations'],
        'net_income': ['net income', 'net earnings'],
        
        # Balance Sheet
        'total_assets': ['total assets'],
        'total_liabilities': ['total liabilities'],
        'total_equity': ['total shareholders equity', 'total equity', 'stockholders equity'],
        'cash_and_equivalents': ['cash and cash equivalents'],
        
        # Cash Flow
        'operating_cash_flow': ['cash generated by operating', 'operating activities', 'cash provided by operating'],
        'capital_expenditures': ['payments for acquisition of property', 'capital expenditures', 'purchases of property'],
        'free_cash_flow': ['free cash flow'],
    }
    
    # Try to extract from each sheet
    success_count = 0
    
    for sheet_name in excel_file.sheet_names:
        # Load sheet
        try:
            df = excel_file.parse(sheet_name, header=None)  # No header assumption
            
            # Try to find each metric in this sheet
            for metric_key, search_terms in metrics.items():
                if metric_key not in extracted or extracted[metric_key] == 0:
                    value, found_method = smart_find_value(df, search_terms)
                    if value != 0:
                        extracted[metric_key] = value
                        success_count += 1
                        print(f"  [OK] {metric_key}: ${value:,.0f} from '{sheet_name}'")
        except Exception as e:
            continue
    
    print(f"\n[SUMMARY] Extracted {success_count}/{len(metrics)} metrics from Excel")
    
    return extracted

# ============================================================================
# PDF EXTRACTION (FALLBACK METHOD)
# ============================================================================

def extract_from_pdf(file_path: str = "aapl-20240928.pdf") -> Dict[str, float]:
    """Extract from PDF using text parsing (fallback)"""
    print("\n" + "="*80)
    print("METHOD 2: PDF EXTRACTION (FALLBACK)")
    print("="*80)
    
    try:
        # Try pdfplumber first
        import pdfplumber
        
        print(f"\n[INFO] Opening PDF: {file_path}")
        
        with pdfplumber.open(file_path) as pdf:
            print(f"[OK] Loaded {len(pdf.pages)} pages")
            
            # Extract text from first 50 pages (financials are usually in first section)
            all_text = ""
            for page_num in range(min(50, len(pdf.pages))):
                page = pdf.pages[page_num]
                all_text += page.extract_text() or ""
            
            print(f"[OK] Extracted {len(all_text)} characters of text")
            
            # Parse using regex patterns
            extracted = parse_text_for_metrics(all_text)
            
            return extracted
    
    except ImportError:
        print("[WARN] pdfplumber not installed. Install with: pip install pdfplumber")
        print("[INFO] Attempting basic PDF text extraction...")
        
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                all_text = ""
                for page in reader.pages[:50]:
                    all_text += page.extract_text() or ""
            
            extracted = parse_text_for_metrics(all_text)
            return extracted
        
        except Exception as e:
            print(f"[FAIL] PDF extraction failed: {e}")
            return {}
    
    except Exception as e:
        print(f"[FAIL] PDF extraction failed: {e}")
        return {}

def parse_text_for_metrics(text: str) -> Dict[str, float]:
    """Parse extracted text for financial metrics using regex"""
    print("\n[INFO] Parsing text for financial metrics...")
    
    extracted = {}
    
    # Define patterns for each metric (pattern: metric_name)
    patterns = {
        'total_revenue': [
            r'Total net sales[:\s]+\$?([\d,]+)',
            r'Net sales[:\s]+\$?([\d,]+)',
        ],
        'net_income': [
            r'Net income[:\s]+\$?([\d,]+)',
            r'Net earnings[:\s]+\$?([\d,]+)',
        ],
        'total_assets': [
            r'Total assets[:\s]+\$?([\d,]+)',
        ],
        'total_equity': [
            r'Total shareholders.? equity[:\s]+\$?([\d,]+)',
        ],
    }
    
    for metric_key, pattern_list in patterns.items():
        for pattern in pattern_list:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Take the first substantial match
                    value_str = matches[0].replace(',', '')
                    value = float(value_str)
                    if value > 1000:  # Sanity check (in millions)
                        extracted[metric_key] = value * 1000000  # Convert to actual dollars
                        print(f"  [OK] {metric_key}: ${value:,.0f}M")
                        break
                except:
                    continue
    
    return extracted

# ============================================================================
# MAIN HYBRID LOGIC
# ============================================================================

def calculate_derived_metrics(extracted: Dict[str, float]) -> Dict[str, float]:
    """Calculate ratios and derived metrics"""
    print("\n" + "-"*80)
    print("CALCULATING DERIVED METRICS")
    print("-"*80)
    
    ratios = {}
    
    # Extract needed values
    revenue = extracted.get('total_revenue', 0)
    gross_profit = extracted.get('gross_profit', 0)
    operating_income = extracted.get('operating_income', 0)
    net_income = extracted.get('net_income', 0)
    total_assets = extracted.get('total_assets', 0)
    total_liabilities = extracted.get('total_liabilities', 0)
    total_equity = extracted.get('total_equity', 0)
    ocf = extracted.get('operating_cash_flow', 0)
    capex = extracted.get('capital_expenditures', 0)
    
    # Calculate ratios
    if revenue > 0:
        ratios['gross_margin'] = gross_profit / revenue
        ratios['operating_margin'] = operating_income / revenue
        ratios['net_margin'] = net_income / revenue
        print(f"  [OK] Gross Margin: {ratios['gross_margin']*100:.2f}%")
        print(f"  [OK] Operating Margin: {ratios['operating_margin']*100:.2f}%")
        print(f"  [OK] Net Margin: {ratios['net_margin']*100:.2f}%")
    
    if total_equity > 0:
        ratios['roe'] = net_income / total_equity
        ratios['debt_to_equity'] = total_liabilities / total_equity
        print(f"  [OK] ROE: {ratios['roe']*100:.2f}%")
        print(f"  [OK] Debt/Equity: {ratios['debt_to_equity']:.2f}")
    
    if total_assets > 0:
        ratios['roa'] = net_income / total_assets
        print(f"  [OK] ROA: {ratios['roa']*100:.2f}%")
    
    if ocf != 0 and capex != 0:
        ratios['free_cash_flow'] = ocf + capex  # capex is negative
        print(f"  [OK] Free Cash Flow: ${ratios['free_cash_flow']:,.0f}")
    
    return ratios

def update_validation_template(extracted: Dict, ratios: Dict, 
                               template_file: str = "validation_truth_AAPL.json") -> str:
    """Update validation template with extracted data"""
    print("\n" + "="*80)
    print("UPDATING VALIDATION TEMPLATE")
    print("="*80)
    
    # Load template
    with open(template_file, 'r') as f:
        template = json.load(f)
    
    # Update income statement
    income_mapping = {
        'total_revenue': 'total_revenue',
        'cost_of_revenue': 'cost_of_revenue',
        'gross_profit': 'gross_profit',
        'research_development': 'research_development',
        'operating_income': 'operating_income',
        'net_income': 'net_income',
    }
    
    for key, template_key in income_mapping.items():
        if key in extracted and extracted[key] != 0:
            template['income_statement'][template_key] = extracted[key]
    
    # Update balance sheet
    balance_mapping = {
        'total_assets': 'total_assets',
        'total_liabilities': 'total_liabilities',
        'total_equity': 'total_equity',
        'cash_and_equivalents': 'cash_and_equivalents',
    }
    
    for key, template_key in balance_mapping.items():
        if key in extracted and extracted[key] != 0:
            template['balance_sheet'][template_key] = extracted[key]
    
    # Update cash flow
    cashflow_mapping = {
        'operating_cash_flow': 'operating_cash_flow',
        'capital_expenditures': 'capital_expenditures',
        'free_cash_flow': 'free_cash_flow_manual',
    }
    
    for key, template_key in cashflow_mapping.items():
        if key in extracted and extracted[key] != 0:
            template['cash_flow'][template_key] = extracted[key]
    
    # Update calculated ratios
    for key, value in ratios.items():
        if key in template['calculated_ratios']:
            template['calculated_ratios'][key] = value
    
    # Save updated template
    output_file = "validation_truth_AAPL_FILLED.json"
    with open(output_file, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"\n[OK] Template updated: {output_file}")
    
    # Count filled fields
    filled_income = sum(1 for v in template['income_statement'].values() if v is not None)
    filled_balance = sum(1 for v in template['balance_sheet'].values() if v is not None)
    filled_cashflow = sum(1 for v in template['cash_flow'].values() if v is not None)
    filled_ratios = sum(1 for v in template['calculated_ratios'].values() if v is not None)
    
    print(f"\nFields Filled:")
    print(f"  Income Statement: {filled_income}")
    print(f"  Balance Sheet: {filled_balance}")
    print(f"  Cash Flow: {filled_cashflow}")
    print(f"  Calculated Ratios: {filled_ratios}")
    print(f"  Total: {filled_income + filled_balance + filled_cashflow + filled_ratios}")
    
    return output_file

def main():
    """Main hybrid extraction logic"""
    print("\n" + "="*80)
    print("  AAPL FINANCIAL DATA EXTRACTOR - HYBRID APPROACH")
    print("="*80)
    
    extracted = {}
    
    # Method 1: Try Excel first
    excel_file = analyze_excel_structure()
    if excel_file:
        extracted = extract_from_excel(excel_file)
    
    # Check if Excel extraction was successful
    success_rate = sum(1 for v in extracted.values() if v != 0) / max(len(extracted), 1)
    
    print(f"\n[INFO] Excel extraction success rate: {success_rate*100:.1f}%")
    
    # Method 2: Fall back to PDF if Excel failed
    if success_rate < 0.3:  # Less than 30% success
        print("\n[WARN] Excel extraction insufficient, trying PDF...")
        pdf_extracted = extract_from_pdf()
        
        # Merge PDF results (prefer PDF values if available)
        for key, value in pdf_extracted.items():
            if value != 0:
                extracted[key] = value
    
    # Calculate derived metrics
    ratios = calculate_derived_metrics(extracted)
    
    # Update validation template
    output_file = update_validation_template(extracted, ratios)
    
    print("\n" + "="*80)
    print("  EXTRACTION COMPLETE!")
    print("="*80)
    print(f"\n[OK] Generated: {output_file}")
    print("\nNext Steps:")
    print("  1. Review the file for accuracy")
    print("  2. Manually fill any missing values")
    print("  3. Rename to: validation_truth_AAPL.json")
    print("  4. Run validation tests")
    
    return extracted, ratios, output_file

if __name__ == "__main__":
    try:
        extracted, ratios, output_file = main()
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()

