"""
AAPL Financial Report Excel Mapper
Intelligently extracts data from messy Excel export and maps to validation template
"""

import pandas as pd
import json
from typing import Dict, Any, List, Tuple
import os

def analyze_excel_structure(file_path: str = "AAPL_Financial_Report_20251127.xlsx"):
    """
    Step 1: Analyze Excel file structure
    """
    print("="*80)
    print("ANALYZING AAPL FINANCIAL REPORT EXCEL STRUCTURE")
    print("="*80)
    
    if not os.path.exists(file_path):
        print(f"\n[ERROR] File not found: {file_path}")
        print("Please ensure AAPL_Financial_Report_20251127.xlsx is in the current directory.")
        return None
    
    # Load all sheets
    excel_file = pd.ExcelFile(file_path)
    
    print(f"\nTotal Sheets: {len(excel_file.sheet_names)}")
    print("\nSheet Names:")
    for i, sheet in enumerate(excel_file.sheet_names, 1):
        print(f"  {i}. {sheet}")
    
    return excel_file

def find_financial_tables(excel_file: pd.ExcelFile) -> Dict:
    """
    Step 2: Identify key financial statement tables
    """
    print("\n" + "="*80)
    print("IDENTIFYING FINANCIAL STATEMENT TABLES")
    print("="*80)
    
    # Common keywords for different statements
    income_keywords = ['revenue', 'sales', 'income', 'earnings', 'operations', 'profit']
    balance_keywords = ['assets', 'liabilities', 'equity', 'stockholders', 'balance']
    cashflow_keywords = ['cash flow', 'operating activities', 'investing', 'financing']
    
    identified_tables = {
        'income_statement': [],
        'balance_sheet': [],
        'cash_flow': [],
        'other': []
    }
    
    for sheet_name in excel_file.sheet_names:
        sheet_lower = sheet_name.lower()
        
        if any(kw in sheet_lower for kw in income_keywords):
            identified_tables['income_statement'].append(sheet_name)
        elif any(kw in sheet_lower for kw in balance_keywords):
            identified_tables['balance_sheet'].append(sheet_name)
        elif any(kw in sheet_lower for kw in cashflow_keywords):
            identified_tables['cash_flow'].append(sheet_name)
        else:
            identified_tables['other'].append(sheet_name)
    
    print("\nIncome Statement Sheets:")
    for sheet in identified_tables['income_statement']:
        print(f"  - {sheet}")
    
    print("\nBalance Sheet Sheets:")
    for sheet in identified_tables['balance_sheet']:
        print(f"  - {sheet}")
    
    print("\nCash Flow Sheets:")
    for sheet in identified_tables['cash_flow']:
        print(f"  - {sheet}")
    
    print(f"\nOther Sheets: {len(identified_tables['other'])}")
    
    return identified_tables

def smart_extract_value(df: pd.DataFrame, search_terms: List[str]) -> Tuple[float, str, str]:
    """
    Step 3: Smart value extraction from messy tables
    
    Args:
        df: DataFrame to search
        search_terms: List of possible field names
    
    Returns:
        (value, field_name_found, location)
    """
    for term in search_terms:
        # Search in all cells
        for col_idx, col in enumerate(df.columns):
            for row_idx, val in df[col].items():
                if pd.notna(val) and isinstance(val, str):
                    val_lower = val.lower().strip()
                    term_lower = term.lower().strip()
                    
                    # Check for match
                    if term_lower in val_lower or val_lower in term_lower:
                        # Found it! Now get the value (usually in adjacent cells)
                        try:
                            # Try same row, next columns
                            row_data = df.iloc[row_idx]
                            for i in range(col_idx + 1, len(row_data)):
                                cell_val = row_data.iloc[i]
                                
                                # Try to parse as number
                                if pd.notna(cell_val):
                                    if isinstance(cell_val, (int, float)):
                                        return float(cell_val), str(val), f"Row {row_idx}, Col {i}"
                                    
                                    if isinstance(cell_val, str):
                                        # Clean and parse
                                        cleaned = cell_val.replace(',', '').replace('$', '').replace('(', '-').replace(')', '').strip()
                                        try:
                                            num_val = float(cleaned)
                                            return num_val, str(val), f"Row {row_idx}, Col {i}"
                                        except:
                                            continue
                        except Exception as e:
                            continue
    
    return 0.0, "NOT_FOUND", "N/A"

def extract_all_metrics(excel_file: pd.ExcelFile, identified_tables: Dict) -> Dict:
    """
    Step 4: Extract all metrics needed for validation
    """
    print("\n" + "="*80)
    print("EXTRACTING FINANCIAL METRICS")
    print("="*80)
    
    extracted = {}
    
    # Income Statement Metrics
    print("\n[1/3] Income Statement...")
    if identified_tables['income_statement']:
        for sheet_name in identified_tables['income_statement']:
            print(f"\n  Analyzing sheet: {sheet_name}")
            df = excel_file.parse(sheet_name, header=None)  # No header assumption
            
            income_metrics = {
                'total_revenue': ['total revenue', 'net sales', 'total net sales', 'revenues'],
                'cost_of_revenue': ['cost of revenue', 'cost of sales', 'cost of goods sold', 'cogs'],
                'gross_profit': ['gross profit', 'gross margin', 'gross income'],
                'operating_income': ['operating income', 'income from operations', 'operating profit', 'ebit'],
                'net_income': ['net income', 'net earnings', 'consolidated net income'],
            }
            
            for metric, search_terms in income_metrics.items():
                if metric not in extracted or extracted[metric] == 0:
                    value, found, loc = smart_extract_value(df, search_terms)
                    if value != 0:
                        extracted[metric] = value
                        print(f"    [OK] {metric}: ${value:,.0f} (found: '{found}' at {loc})")
    
    # Balance Sheet Metrics
    print("\n[2/3] Balance Sheet...")
    if identified_tables['balance_sheet']:
        for sheet_name in identified_tables['balance_sheet']:
            print(f"\n  Analyzing sheet: {sheet_name}")
            df = excel_file.parse(sheet_name, header=None)
            
            balance_metrics = {
                'total_assets': ['total assets'],
                'total_liabilities': ['total liabilities'],
                'total_equity': ['total equity', 'stockholders equity', 'shareholders equity', 'total stockholders'],
                'cash_and_equivalents': ['cash and cash equivalents', 'cash and equivalents'],
                'total_current_assets': ['total current assets', 'current assets'],
                'total_current_liabilities': ['total current liabilities', 'current liabilities'],
            }
            
            for metric, search_terms in balance_metrics.items():
                if metric not in extracted or extracted[metric] == 0:
                    value, found, loc = smart_extract_value(df, search_terms)
                    if value != 0:
                        extracted[metric] = value
                        print(f"    [OK] {metric}: ${value:,.0f} (found: '{found}' at {loc})")
    
    # Cash Flow Metrics
    print("\n[3/3] Cash Flow...")
    if identified_tables['cash_flow']:
        for sheet_name in identified_tables['cash_flow']:
            print(f"\n  Analyzing sheet: {sheet_name}")
            df = excel_file.parse(sheet_name, header=None)
            
            cashflow_metrics = {
                'operating_cash_flow': ['cash provided by operating', 'operating cash flow', 'cash from operating', 'net cash provided by operating'],
                'capital_expenditures': ['payments for acquisition', 'capital expenditure', 'purchases of property', 'capex'],
                'free_cash_flow': ['free cash flow'],
            }
            
            for metric, search_terms in cashflow_metrics.items():
                if metric not in extracted or extracted[metric] == 0:
                    value, found, loc = smart_extract_value(df, search_terms)
                    if value != 0:
                        extracted[metric] = value
                        print(f"    [OK] {metric}: ${value:,.0f} (found: '{found}' at {loc})")
    
    return extracted

def update_validation_template(extracted: Dict, template_file: str = "validation_truth_AAPL.json"):
    """
    Step 5: Update validation template with extracted data
    """
    print("\n" + "="*80)
    print("UPDATING VALIDATION TEMPLATE")
    print("="*80)
    
    # Load template
    with open(template_file, 'r') as f:
        template = json.load(f)
    
    # Update income statement
    for key, value in extracted.items():
        if key in template['income_statement']:
            template['income_statement'][key] = value
        elif key in template['balance_sheet']:
            template['balance_sheet'][key] = value
        elif key in template['cash_flow']:
            template['cash_flow'][key] = value
    
    # Calculate ratios manually
    revenue = extracted.get('total_revenue', 0)
    gross_profit = extracted.get('gross_profit', 0)
    operating_income = extracted.get('operating_income', 0)
    net_income = extracted.get('net_income', 0)
    total_assets = extracted.get('total_assets', 0)
    total_liabilities = extracted.get('total_liabilities', 0)
    total_equity = extracted.get('total_equity', 0)
    current_assets = extracted.get('total_current_assets', 0)
    current_liabilities = extracted.get('total_current_liabilities', 0)
    ocf = extracted.get('operating_cash_flow', 0)
    capex = extracted.get('capital_expenditures', 0)
    
    if revenue > 0:
        template['calculated_ratios']['gross_margin'] = gross_profit / revenue
        template['calculated_ratios']['operating_margin'] = operating_income / revenue
        template['calculated_ratios']['net_margin'] = net_income / revenue
    
    if total_equity > 0:
        template['calculated_ratios']['roe'] = net_income / total_equity
        template['calculated_ratios']['debt_to_equity'] = total_liabilities / total_equity
    
    if total_assets > 0:
        template['calculated_ratios']['roa'] = net_income / total_assets
    
    if current_liabilities > 0:
        template['calculated_ratios']['current_ratio'] = current_assets / current_liabilities
    
    template['calculated_ratios']['free_cash_flow'] = ocf + capex  # capex is negative
    
    # Save updated template
    output_file = template_file.replace('.json', '_FILLED.json')
    with open(output_file, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"\n[OK] Template updated: {output_file}")
    
    # Print summary
    print("\nExtracted Values Summary:")
    print("-" * 80)
    for key, value in extracted.items():
        if value != 0:
            print(f"  {key:30s}: ${value:>20,.0f}")
    
    print("\n" + "="*80)
    print("CALCULATED RATIOS")
    print("="*80)
    for key, value in template['calculated_ratios'].items():
        if value is not None and value != 0:
            if isinstance(value, (int, float)):
                if 'margin' in key.lower() or 'ratio' in key.lower() or key in ['roe', 'roa', 'debt_to_equity']:
                    print(f"  {key:30s}: {value:>20.4f}")
                else:
                    print(f"  {key:30s}: ${value:>20,.0f}")
    
    return output_file

def main():
    """Main execution"""
    print("\n" + "="*80)
    print("  AAPL EXCEL TO VALIDATION TEMPLATE MAPPER")
    print("="*80)
    
    # Step 1: Analyze structure
    excel_file = analyze_excel_structure()
    
    if excel_file is None:
        print("\n[FAIL] Cannot proceed without Excel file.")
        return None, None
    
    # Step 2: Identify tables
    identified = find_financial_tables(excel_file)
    
    # Step 3 & 4: Extract metrics
    extracted = extract_all_metrics(excel_file, identified)
    
    # Step 5: Update template
    output_file = update_validation_template(extracted)
    
    print("\n" + "="*80)
    print("  EXTRACTION COMPLETE!")
    print("="*80)
    print(f"\nReview the file: {output_file}")
    print("\nNEXT STEPS:")
    print("  1. Open validation_truth_AAPL_FILLED.json")
    print("  2. Manually verify all values against the PDF (aapl-20240928.pdf)")
    print("  3. If correct, rename to validation_truth_AAPL.json (replace original)")
    print("  4. Run: python validation_master_runner.py AAPL")
    
    return extracted, output_file

if __name__ == "__main__":
    extracted_data, output_file = main()

