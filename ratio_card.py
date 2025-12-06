# =============================================================================
# RATIO CARD COMPONENT - THE DIFFERENTIATOR
# =============================================================================
# 
# What competitors hide, we reveal:
# - Shows the VALUE
# - Shows the EQUATION
# - Shows the ACTUAL NUMBERS used
# - Provides 3-DEPTH explanations (beginner → intermediate → professional)
#
# Target: Young investors (18-25) + IFAs who need to explain to clients
# =============================================================================

import streamlit as st
from typing import Dict, Any, Optional, Union
import pandas as pd

# =============================================================================
# RATIO DEFINITIONS - The Knowledge Base
# =============================================================================

RATIO_DEFINITIONS = {
    # ===== VALUATION RATIOS =====
    "PE_Ratio": {
        "name": "P/E Ratio",
        "equation": "Price / Earnings Per Share",
        "equation_formula": "Stock Price ÷ EPS",
        "components": ["current_price", "eps"],
        "category": "Valuation",
        "benchmark": {"low": 15, "high": 25},
        "explanations": {
            "beginner": "How many dollars you pay for each $1 of company profit. Lower = cheaper stock.",
            "intermediate": "The Price-to-Earnings ratio shows how much investors are willing to pay per dollar of earnings. A P/E of 20 means investors pay $20 for every $1 of annual profit. Compare to industry peers and historical averages.",
            "professional": "Forward P/E uses expected earnings; trailing P/E uses last 12 months. High P/E may indicate growth expectations or overvaluation. Negative P/E (loss-making company) should be evaluated using P/S or EV/EBITDA instead. Consider PEG ratio (P/E ÷ Growth Rate) for growth-adjusted valuation. Cyclical industries require normalized earnings analysis."
        },
        "interpretation": {
            "low": "Stock may be undervalued OR company has problems",
            "normal": "Fairly valued relative to market average",
            "high": "Investors expect high growth OR stock is overvalued"
        }
    },
    
    "PB_Ratio": {
        "name": "P/B Ratio",
        "equation": "Price / Book Value Per Share",
        "equation_formula": "Stock Price ÷ (Total Equity ÷ Shares Outstanding)",
        "components": ["current_price", "book_value_per_share"],
        "category": "Valuation",
        "benchmark": {"low": 1, "high": 3},
        "explanations": {
            "beginner": "How much you pay for the company's actual assets. Under 1 = paying less than what company owns.",
            "intermediate": "Price-to-Book compares market value to accounting book value. P/B < 1 suggests stock trades below its net asset value. Useful for asset-heavy industries like banks and real estate.",
            "professional": "Book value may differ significantly from fair market value of assets. Intangible-heavy companies (tech, pharma) typically have high P/B due to off-balance-sheet IP value. Tangible Book Value (excluding goodwill) provides cleaner measure for M&A analysis. ROE decomposition: P/B = P/E × ROE."
        },
        "interpretation": {
            "low": "Undervalued or asset impairment concerns",
            "normal": "Market values company at or near book value",
            "high": "Market values intangibles/growth not on books"
        }
    },
    
    "PS_Ratio": {
        "name": "P/S Ratio",
        "equation": "Price / Revenue Per Share",
        "equation_formula": "Market Cap ÷ Total Revenue",
        "components": ["market_cap", "revenue"],
        "category": "Valuation",
        "benchmark": {"low": 1, "high": 5},
        "explanations": {
            "beginner": "How much you pay for each $1 of sales. Works even if company isn't profitable yet.",
            "intermediate": "Price-to-Sales is useful for unprofitable companies or comparing across industries. Lower P/S means cheaper relative to revenue. High-margin businesses deserve higher P/S.",
            "professional": "P/S ignores profitability - a 5% margin business at P/S of 2 is vastly different from a 30% margin business at same P/S. Adjust with EV/Sales for capital structure neutrality. SaaS companies often trade at high P/S (5-15x) due to recurring revenue and margin expansion expectations."
        },
        "interpretation": {
            "low": "Cheap relative to sales; check margins",
            "normal": "Fair value for mature business",
            "high": "Market expects margin expansion or high growth"
        }
    },
    
    "EV_EBITDA": {
        "name": "EV/EBITDA",
        "equation": "Enterprise Value / EBITDA",
        "equation_formula": "(Market Cap + Debt - Cash) ÷ (Operating Income + D&A)",
        "components": ["enterprise_value", "ebitda"],
        "category": "Valuation",
        "benchmark": {"low": 8, "high": 15},
        "explanations": {
            "beginner": "How many years of cash profits would it take to buy the whole company.",
            "intermediate": "Enterprise Value includes debt and excludes cash, giving a cleaner view than P/E for acquisitions. EBITDA approximates cash flow before financing. Lower = cheaper acquisition target.",
            "professional": "Preferred by PE firms and M&A analysts. Normalizes for capital structure differences. Add back stock-based comp for true cash EBITDA. Watch for working capital adjustments in asset-light vs asset-heavy businesses. Maintenance CapEx should be subtracted for true 'owner earnings'."
        },
        "interpretation": {
            "low": "Attractive acquisition target",
            "normal": "Fair transaction value",
            "high": "Premium for quality/growth"
        }
    },
    
    # ===== PROFITABILITY RATIOS =====
    "ROE": {
        "name": "Return on Equity",
        "equation": "Net Income / Shareholders' Equity",
        "equation_formula": "Net Income ÷ Average Shareholders' Equity × 100%",
        "components": ["net_income", "shareholders_equity"],
        "category": "Profitability",
        "benchmark": {"low": 10, "high": 20},
        "explanations": {
            "beginner": "How much profit the company makes with your money. 15% ROE = $15 profit for every $100 invested.",
            "intermediate": "ROE measures management's efficiency at generating returns on shareholders' investment. Higher ROE means better capital allocation. Compare to cost of equity and industry peers.",
            "professional": "Decompose with DuPont: ROE = Net Margin × Asset Turnover × Financial Leverage. High ROE from excessive leverage is risky. Sustainable ROE drives intrinsic value growth. Buffett targets >15% ROE with low debt. Beware: buybacks artificially inflate ROE by reducing equity base."
        },
        "interpretation": {
            "low": "Poor capital efficiency",
            "normal": "Adequate returns",
            "high": "Excellent capital allocation (verify not from excess leverage)"
        }
    },
    
    "ROIC": {
        "name": "Return on Invested Capital",
        "equation": "NOPAT / Invested Capital",
        "equation_formula": "(Operating Income × (1 - Tax Rate)) ÷ (Equity + Debt - Cash)",
        "components": ["operating_income", "tax_rate", "equity", "debt", "cash"],
        "category": "Profitability",
        "benchmark": {"low": 8, "high": 15},
        "explanations": {
            "beginner": "How efficiently the company uses ALL money (yours + borrowed) to make profits.",
            "intermediate": "ROIC measures returns on total capital employed regardless of financing. If ROIC > WACC, company creates value. Best metric for capital allocation decisions.",
            "professional": "The gold standard for value creation analysis. ROIC > WACC = positive EVA (Economic Value Added). Adjust invested capital for operating leases and R&D capitalization. Compare to marginal ROIC on new investments to assess growth quality. Greenblatt's Magic Formula uses ROIC as primary screen."
        },
        "interpretation": {
            "low": "Destroying value if below WACC",
            "normal": "Meeting cost of capital",
            "high": "Creating significant shareholder value"
        }
    },
    
    "Gross_Margin": {
        "name": "Gross Margin",
        "equation": "Gross Profit / Revenue",
        "equation_formula": "(Revenue - Cost of Goods Sold) ÷ Revenue × 100%",
        "components": ["gross_profit", "revenue"],
        "category": "Profitability",
        "benchmark": {"low": 30, "high": 60},
        "explanations": {
            "beginner": "How much of each sale dollar is left after paying for the product itself.",
            "intermediate": "Gross margin shows pricing power and production efficiency. Higher margin = more room for operating expenses and profit. Track trends - declining margins may signal competition.",
            "professional": "Gross margin reflects competitive moat strength. Software (70-90%), Consumer Staples (40-60%), Retail (20-40%), Airlines (10-20%). Segment-level margins reveal true business quality. Watch for inventory accounting changes (FIFO vs LIFO) affecting comparability."
        },
        "interpretation": {
            "low": "Commodity business or intense competition",
            "normal": "Industry-appropriate margins",
            "high": "Strong pricing power / moat"
        }
    },
    
    "Operating_Margin": {
        "name": "Operating Margin",
        "equation": "Operating Income / Revenue",
        "equation_formula": "(Revenue - COGS - Operating Expenses) ÷ Revenue × 100%",
        "components": ["operating_income", "revenue"],
        "category": "Profitability",
        "benchmark": {"low": 10, "high": 25},
        "explanations": {
            "beginner": "How much profit from core business before interest and taxes.",
            "intermediate": "Operating margin shows efficiency of the core business independent of financing. Excludes interest and taxes for cleaner comparison across companies with different capital structures.",
            "professional": "Best proxy for business unit economics. Adjust for non-recurring items (restructuring, litigation). Operating leverage = how margins expand with scale. High fixed costs = high operating leverage. Compare to contribution margin for break-even analysis."
        },
        "interpretation": {
            "low": "Thin margins, operational inefficiency",
            "normal": "Adequate operational profitability",
            "high": "Strong operational efficiency and scale"
        }
    },
    
    "Net_Margin": {
        "name": "Net Profit Margin",
        "equation": "Net Income / Revenue",
        "equation_formula": "Net Income ÷ Total Revenue × 100%",
        "components": ["net_income", "revenue"],
        "category": "Profitability",
        "benchmark": {"low": 5, "high": 20},
        "explanations": {
            "beginner": "The final profit: how much of each sales dollar becomes actual profit.",
            "intermediate": "Net margin is the bottom line percentage. Affected by taxes, interest, and one-time items. Compare year-over-year and to peers. Sustainable margins matter more than peak margins.",
            "professional": "Decompose variance: Gross Margin - OpEx% - Interest% - Tax%. Quality of earnings analysis: recurring vs one-time items. Cash conversion matters - accrual profits need to convert to cash. GAAP vs Non-GAAP reconciliation critical for true picture."
        },
        "interpretation": {
            "low": "Thin profits, reinvestment or competitive pressure",
            "normal": "Healthy profitability",
            "high": "Superior economics, potential moat"
        }
    },
    
    # ===== LEVERAGE RATIOS =====
    "Debt_to_Equity": {
        "name": "Debt to Equity",
        "equation": "Total Debt / Shareholders' Equity",
        "equation_formula": "(Short-term Debt + Long-term Debt) ÷ Total Equity",
        "components": ["total_debt", "shareholders_equity"],
        "category": "Leverage",
        "benchmark": {"low": 0.5, "high": 2.0},
        "explanations": {
            "beginner": "How much the company owes vs how much it owns. Lower = safer.",
            "intermediate": "D/E shows financial leverage. Higher ratio = more risk but potentially higher returns. Industry matters: utilities have high D/E, tech has low. Compare to peers.",
            "professional": "Net Debt (Debt - Cash) gives truer picture. Lease liabilities (IFRS 16) significantly increased reported leverage. Capital-light businesses can run higher D/E safely. Monitor debt maturity schedule and refinancing risk. Interest coverage ratio more important than D/E for credit analysis."
        },
        "interpretation": {
            "low": "Conservative financing, lower risk",
            "normal": "Moderate leverage",
            "high": "Aggressive leverage, higher risk"
        }
    },
    
    "Interest_Coverage": {
        "name": "Interest Coverage",
        "equation": "EBIT / Interest Expense",
        "equation_formula": "Operating Income ÷ Interest Expense",
        "components": ["operating_income", "interest_expense"],
        "category": "Leverage",
        "benchmark": {"low": 3, "high": 10},
        "explanations": {
            "beginner": "How many times the company can pay its loan interest. Higher = safer.",
            "intermediate": "Interest coverage shows ability to service debt. Below 2x is danger zone. Lenders use this for covenant compliance. Falling coverage = rising risk.",
            "professional": "Use EBITDA coverage for capital-intensive businesses. Fixed charge coverage includes leases and preferred dividends. Stress test with normalized EBIT in downturn scenario. Credit rating agencies weight this heavily. Covenant levels typically 2-3x for investment grade."
        },
        "interpretation": {
            "low": "Debt servicing strain, credit risk",
            "normal": "Comfortable debt coverage",
            "high": "Very safe, room for more leverage"
        }
    },
    
    # ===== LIQUIDITY RATIOS =====
    "Current_Ratio": {
        "name": "Current Ratio",
        "equation": "Current Assets / Current Liabilities",
        "equation_formula": "(Cash + Receivables + Inventory) ÷ Current Liabilities",
        "components": ["current_assets", "current_liabilities"],
        "category": "Liquidity",
        "benchmark": {"low": 1.0, "high": 2.0},
        "explanations": {
            "beginner": "Can the company pay its bills due this year? Above 1 = yes.",
            "intermediate": "Current ratio measures short-term solvency. Too low = liquidity risk. Too high = inefficient use of capital. Industry context matters.",
            "professional": "Quality of current assets matters: receivables collectibility, inventory obsolescence risk. Quick ratio (excluding inventory) more conservative. Working capital cycle analysis: DSO + DIO - DPO = cash conversion cycle. Negative working capital (like Amazon) can be strength."
        },
        "interpretation": {
            "low": "Liquidity stress",
            "normal": "Adequate short-term coverage",
            "high": "Very liquid, possibly too conservative"
        }
    },
    
    "Quick_Ratio": {
        "name": "Quick Ratio",
        "equation": "(Current Assets - Inventory) / Current Liabilities",
        "equation_formula": "(Cash + Receivables) ÷ Current Liabilities",
        "components": ["current_assets", "inventory", "current_liabilities"],
        "category": "Liquidity",
        "benchmark": {"low": 0.5, "high": 1.5},
        "explanations": {
            "beginner": "Can the company pay bills without selling inventory? More conservative test.",
            "intermediate": "Quick ratio excludes inventory which may take time to convert to cash. Better for companies with slow-moving inventory. Banking standard is >1.0.",
            "professional": "Also called 'Acid Test'. For retailers, inventory is liquid; for manufacturers, it's not. Prepaid expenses should also be excluded for true acid test. Cash ratio (cash only / current liabilities) is most conservative."
        },
        "interpretation": {
            "low": "Dependent on inventory liquidation",
            "normal": "Can meet obligations without inventory sales",
            "high": "Very strong liquidity position"
        }
    },
    
    # ===== EFFICIENCY RATIOS =====
    "Asset_Turnover": {
        "name": "Asset Turnover",
        "equation": "Revenue / Total Assets",
        "equation_formula": "Annual Revenue ÷ Average Total Assets",
        "components": ["revenue", "total_assets"],
        "category": "Efficiency",
        "benchmark": {"low": 0.5, "high": 2.0},
        "explanations": {
            "beginner": "How efficiently the company uses its assets to generate sales.",
            "intermediate": "Asset turnover shows capital efficiency. High turnover + low margins OR low turnover + high margins can both be profitable. Part of DuPont ROE decomposition.",
            "professional": "Segment by fixed vs current assets for deeper analysis. Capital-light models (franchising) have high turnover. ROIC = Margin × Turnover (simplified). Track trends: declining turnover may indicate over-investment or demand weakness."
        },
        "interpretation": {
            "low": "Asset-heavy model or underutilization",
            "normal": "Typical efficiency for industry",
            "high": "Capital-light or highly efficient"
        }
    },
    
    "Inventory_Turnover": {
        "name": "Inventory Turnover",
        "equation": "COGS / Average Inventory",
        "equation_formula": "Cost of Goods Sold ÷ Average Inventory",
        "components": ["cogs", "inventory"],
        "category": "Efficiency",
        "benchmark": {"low": 4, "high": 12},
        "explanations": {
            "beginner": "How many times inventory is sold and replaced per year. Higher = faster sales.",
            "intermediate": "Inventory turnover indicates demand strength and stock management. Low turnover = capital tied up, obsolescence risk. Days Inventory Outstanding = 365 / Turnover.",
            "professional": "Benchmark against peers - grocery (15x+) vs automotive (6-8x). FIFO vs LIFO affects comparability in inflationary periods. JIT inventory systems target minimal inventory. Watch for channel stuffing (sell-in vs sell-through)."
        },
        "interpretation": {
            "low": "Slow-moving inventory, working capital drag",
            "normal": "Healthy inventory velocity",
            "high": "Strong demand or lean inventory"
        }
    },
    
    "Receivables_Turnover": {
        "name": "Receivables Turnover",
        "equation": "Revenue / Average Accounts Receivable",
        "equation_formula": "Net Credit Sales ÷ Average AR",
        "components": ["revenue", "accounts_receivable"],
        "category": "Efficiency",
        "benchmark": {"low": 6, "high": 12},
        "explanations": {
            "beginner": "How quickly customers pay their bills. Higher = faster collection.",
            "intermediate": "Receivables turnover measures collection efficiency. Days Sales Outstanding (DSO) = 365 / Turnover. Rising DSO may indicate credit quality issues or customer disputes.",
            "professional": "Compare to credit terms offered. Net 30 terms should yield ~12x turnover. Analyze aging schedule: 0-30, 31-60, 61-90, 90+ days. Bad debt expense trends reveal credit management quality. Revenue recognition changes (ASC 606) may impact AR comparability."
        },
        "interpretation": {
            "low": "Slow collection, potential credit issues",
            "normal": "Standard collection cycle",
            "high": "Excellent collection or cash business"
        }
    },
    
    # ===== GROWTH METRICS =====
    "Revenue_Growth": {
        "name": "Revenue Growth",
        "equation": "(Current Revenue - Prior Revenue) / Prior Revenue",
        "equation_formula": "(This Year Revenue - Last Year Revenue) ÷ Last Year Revenue × 100%",
        "components": ["current_revenue", "prior_revenue"],
        "category": "Growth",
        "benchmark": {"low": 5, "high": 20},
        "explanations": {
            "beginner": "How fast sales are growing year over year.",
            "intermediate": "Revenue growth drives valuation for growth stocks. Organic growth (excluding M&A) is higher quality. Compare to GDP growth (2-3%) as baseline.",
            "professional": "Decompose: Volume × Price × Mix. Organic vs inorganic. Same-store vs new store for retail. Rule of 40 for SaaS: Growth% + Margin% should exceed 40. Sustainable growth rate = ROE × (1 - Payout Ratio)."
        },
        "interpretation": {
            "low": "Mature or struggling business",
            "normal": "Steady growth",
            "high": "Rapid expansion, growth stock"
        }
    },
    
    "EPS_Growth": {
        "name": "EPS Growth",
        "equation": "(Current EPS - Prior EPS) / Prior EPS",
        "equation_formula": "(This Year EPS - Last Year EPS) ÷ |Last Year EPS| × 100%",
        "components": ["current_eps", "prior_eps"],
        "category": "Growth",
        "benchmark": {"low": 5, "high": 25},
        "explanations": {
            "beginner": "How fast profits per share are growing. What shareholders ultimately care about.",
            "intermediate": "EPS growth can come from: revenue growth, margin expansion, share buybacks. Quality matters - revenue-driven growth is highest quality. Buyback-driven EPS growth may be financial engineering.",
            "professional": "Diluted EPS accounts for options/converts. Adjusted EPS excludes non-recurring items (verify legitimacy). Long-term EPS growth rate key input for DCF terminal value. PEG ratio = P/E ÷ EPS Growth - PEG < 1 often attractive."
        },
        "interpretation": {
            "low": "Stagnant or declining earnings",
            "normal": "Healthy profit growth",
            "high": "Rapid earnings expansion"
        }
    },
    
    "FCF_Growth": {
        "name": "FCF Growth",
        "equation": "(Current FCF - Prior FCF) / Prior FCF",
        "equation_formula": "(This Year FCF - Last Year FCF) ÷ |Last Year FCF| × 100%",
        "components": ["current_fcf", "prior_fcf"],
        "category": "Growth",
        "benchmark": {"low": 5, "high": 20},
        "explanations": {
            "beginner": "How fast the company's spendable cash profits are growing.",
            "intermediate": "FCF growth matters more than earnings growth because cash can't be manipulated as easily. High FCF growth = ability to invest, pay dividends, or buy back shares.",
            "professional": "Levered vs Unlevered FCF for different purposes. FCF yield (FCF/Market Cap) as valuation metric. Capex normalization required for cyclical businesses. Working capital changes can distort YoY comparisons."
        },
        "interpretation": {
            "low": "Cash generation stagnating",
            "normal": "Healthy cash flow growth",
            "high": "Rapidly expanding cash generation"
        }
    },
    
    # ===== DIVIDEND METRICS =====
    "Dividend_Yield": {
        "name": "Dividend Yield",
        "equation": "Annual Dividend / Stock Price",
        "equation_formula": "Annual Dividend Per Share ÷ Current Stock Price × 100%",
        "components": ["annual_dividend", "current_price"],
        "category": "Dividends",
        "benchmark": {"low": 1, "high": 4},
        "explanations": {
            "beginner": "How much cash you get back each year as percentage of stock price.",
            "intermediate": "Dividend yield is income return component of total return. High yield may indicate value trap (price down due to problems) or stable income stock.",
            "professional": "Yield trap: high yield often precedes dividend cut. Look at payout ratio, FCF coverage, and dividend history. Qualified dividends taxed at capital gains rates. REITs/MLPs have higher yields due to pass-through structure."
        },
        "interpretation": {
            "low": "Growth stock, minimal income",
            "normal": "Balanced growth and income",
            "high": "Income stock or potential yield trap"
        }
    },
    
    "Payout_Ratio": {
        "name": "Payout Ratio",
        "equation": "Dividends Per Share / EPS",
        "equation_formula": "Total Dividends ÷ Net Income × 100%",
        "components": ["total_dividends", "net_income"],
        "category": "Dividends",
        "benchmark": {"low": 20, "high": 60},
        "explanations": {
            "beginner": "What percentage of profits goes to shareholders as dividends.",
            "intermediate": "Payout ratio shows dividend sustainability. Very high payout (>80%) may be unsustainable. Low payout means room for dividend growth or reinvestment.",
            "professional": "Use FCF payout ratio (Div/FCF) for true sustainability. Negative payout = dividend from reserves/debt (red flag). Target payout depends on growth phase: mature companies 40-60%, growth companies 0-20%. REITs must pay 90%+ of income."
        },
        "interpretation": {
            "low": "Retaining earnings for growth",
            "normal": "Balanced dividend policy",
            "high": "Mature business or unsustainable payout"
        }
    },
    
    # ===== ADVANCED VALUATION METRICS (HIGH ROI) =====
    
    "Enterprise_Value": {
        "name": "Enterprise Value",
        "equation": "Market Cap + Total Debt - Cash",
        "equation_formula": "(Share Price × Shares Outstanding) + Total Debt - Cash & Equivalents",
        "components": ["market_cap", "total_debt", "cash"],
        "category": "Valuation",
        "benchmark": {"low": 0, "high": 1e12},  # No real benchmark, it's absolute
        "explanations": {
            "beginner": "The total price to buy the ENTIRE company - what an acquirer would pay. Includes taking on debt, minus cash they'd get.",
            "intermediate": "Enterprise Value represents the theoretical takeover price. Unlike market cap, EV accounts for capital structure. It's the 'true cost' to own the business. EV is used as the numerator for capital-structure-neutral ratios like EV/EBITDA.",
            "professional": "EV = Equity Value + Net Debt + Preferred Stock + Minority Interest - Associates. For LBO analysis, use TEV (Total Enterprise Value). Adjust for operating leases (IFRS 16), pension obligations, and non-operating assets. Negative EV (cash > market cap + debt) signals deep value or going-concern issues."
        },
        "interpretation": {
            "low": "Small company or distressed",
            "normal": "Mid-cap range",
            "high": "Large-cap enterprise"
        }
    },
    
    "WACC": {
        "name": "Weighted Average Cost of Capital",
        "equation": "(E/V × Re) + (D/V × Rd × (1-T))",
        "equation_formula": "(Equity ÷ Total Value × Cost of Equity) + (Debt ÷ Total Value × Cost of Debt × (1 - Tax Rate))",
        "components": ["equity_value", "debt_value", "cost_of_equity", "cost_of_debt", "tax_rate"],
        "category": "Valuation",
        "benchmark": {"low": 6, "high": 12},
        "explanations": {
            "beginner": "The minimum return a company must earn to satisfy all its investors (both shareholders and lenders). Think of it as the company's 'hurdle rate'.",
            "intermediate": "WACC blends the cost of equity (what shareholders expect) and cost of debt (interest rate after tax benefit). It's the discount rate used in DCF analysis. Lower WACC = higher company valuation. Higher WACC = investors see more risk.",
            "professional": "Cost of Equity via CAPM: Rf + β(Rm - Rf). Use unlevered beta and relever for target capital structure. Rd = YTM on existing bonds or synthetic rating approach. Marginal vs effective tax rate debate. Country risk premium for EM. Size premium for small caps. WACC should reflect marginal cost of capital for new projects, not historical average."
        },
        "interpretation": {
            "low": "Low-risk, stable business (utilities)",
            "normal": "Typical corporate cost of capital",
            "high": "High-risk or high-leverage business"
        }
    },
    
    "Cost_of_Equity": {
        "name": "Cost of Equity (CAPM)",
        "equation": "Rf + β × (Rm - Rf)",
        "equation_formula": "Risk-Free Rate + Beta × (Market Return - Risk-Free Rate)",
        "components": ["risk_free_rate", "beta", "market_risk_premium"],
        "category": "Valuation",
        "benchmark": {"low": 7, "high": 14},
        "explanations": {
            "beginner": "The return shareholders expect for investing in this stock instead of a 'safe' investment like government bonds.",
            "intermediate": "Cost of Equity is calculated using CAPM. Risk-free rate (usually 10Y Treasury) plus a premium for taking stock risk. Beta measures how much the stock moves with the market. Higher beta = higher required return.",
            "professional": "CAPM limitations: single-factor model ignores size, value, momentum. Fama-French 3/5 factor or APT provide alternatives. Historical vs implied equity risk premium (currently 5-7%). Adjust beta: Bloomberg adjusts toward 1, or use industry unlevered beta. For private companies, add illiquidity premium (2-4%)."
        },
        "interpretation": {
            "low": "Low-beta, defensive stock",
            "normal": "Market-average risk",
            "high": "High-beta, volatile stock"
        }
    },
    
    "PEG_Ratio": {
        "name": "PEG Ratio",
        "equation": "P/E Ratio / EPS Growth Rate",
        "equation_formula": "(Stock Price ÷ EPS) ÷ Annual EPS Growth %",
        "components": ["pe_ratio", "eps_growth_rate"],
        "category": "Valuation",
        "benchmark": {"low": 0.5, "high": 2.0},
        "explanations": {
            "beginner": "Tells you if the P/E ratio is justified by growth. PEG under 1 = you're paying less for each unit of growth.",
            "intermediate": "PEG normalizes P/E by growth rate. A stock with P/E of 30 and 30% growth (PEG=1) may be cheaper than P/E of 15 with 5% growth (PEG=3). Peter Lynch popularized PEG < 1 as a buy signal.",
            "professional": "Use forward earnings growth, not trailing. GARP investors target PEG 0.5-1.5. PEG breaks down for: declining earnings, cyclicals, or very high growth (>50% distorts). Alternative: PEG with FCF growth. For mature companies, low PEG may signal value trap if growth is decelerating."
        },
        "interpretation": {
            "low": "Potentially undervalued relative to growth",
            "normal": "Fair value for growth",
            "high": "Overvalued or growth expectations too low"
        }
    },
    
    "FCF_Yield": {
        "name": "Free Cash Flow Yield",
        "equation": "Free Cash Flow / Market Cap",
        "equation_formula": "(Operating Cash Flow - CapEx) ÷ Market Cap × 100%",
        "components": ["free_cash_flow", "market_cap"],
        "category": "Valuation",
        "benchmark": {"low": 3, "high": 8},
        "explanations": {
            "beginner": "The percentage of cash the company generates relative to its stock price. Higher = more cash for dividends, buybacks, or growth.",
            "intermediate": "FCF Yield is like a 'cash earnings yield'. Unlike P/E, it's based on actual cash, not accounting profits. High FCF yield + low payout = room for dividend increases or buybacks.",
            "professional": "Use levered FCF yield (to equity) for equity-based decisions, unlevered for EV-based. Normalize CapEx for maintenance vs growth. Compare to bond yields: FCF yield > 10Y Treasury is attractive. Greenblatt's Magic Formula uses earnings yield (EBIT/EV), similar concept."
        },
        "interpretation": {
            "low": "Low cash return, growth stock or overvalued",
            "normal": "Reasonable cash yield",
            "high": "High cash generation, potential value play"
        }
    },
    
    "Forward_PE": {
        "name": "Forward P/E",
        "equation": "Price / Forward EPS",
        "equation_formula": "Current Stock Price ÷ Estimated Next 12 Month EPS",
        "components": ["current_price", "forward_eps"],
        "category": "Valuation",
        "benchmark": {"low": 12, "high": 25},
        "explanations": {
            "beginner": "What you pay today for each dollar the company is EXPECTED to earn next year. Uses analyst estimates, not past results.",
            "intermediate": "Forward P/E reflects market expectations of future earnings. Generally lower than trailing P/E if earnings are growing. Compare to trailing P/E: large gap suggests either optimism or pessimism about future.",
            "professional": "Consensus estimates can be biased (analyst herding). Use forward P/E for: companies with one-time charges, turnarounds, or rapid growth. For earnings revision analysis, track forward PE changes over time. NTM vs next fiscal year P/E can differ significantly near year-end."
        },
        "interpretation": {
            "low": "Cheap on future earnings or bearish estimates",
            "normal": "Fair value relative to expected earnings",
            "high": "Expensive or high growth expectations"
        }
    },
    
    "EV_to_FCF": {
        "name": "EV/FCF",
        "equation": "Enterprise Value / Free Cash Flow",
        "equation_formula": "(Market Cap + Debt - Cash) ÷ (Operating CF - CapEx)",
        "components": ["enterprise_value", "free_cash_flow"],
        "category": "Valuation",
        "benchmark": {"low": 10, "high": 25},
        "explanations": {
            "beginner": "How many years of cash flow it would take to pay off the entire company value. Lower = cheaper.",
            "intermediate": "EV/FCF is preferred over P/E for capital-intensive businesses. It's capital-structure neutral and uses actual cash, not accounting profits. Value investors often seek EV/FCF < 15.",
            "professional": "Use unlevered FCF (before interest) with EV for consistency. Normalize FCF for working capital swings and one-time CapEx. For M&A, acquirers pay attention to EV/FCF as it represents payback period. Compare to EV/EBITDA: if EV/FCF >> EV/EBITDA, high CapEx or working capital drain."
        },
        "interpretation": {
            "low": "Attractive cash flow valuation",
            "normal": "Reasonable enterprise cash multiple",
            "high": "Expensive or low FCF generation"
        }
    },
    
    "Intrinsic_Value": {
        "name": "DCF Intrinsic Value",
        "equation": "Sum of Discounted Future Cash Flows + Terminal Value",
        "equation_formula": "Σ FCFt ÷ (1 + WACC)^t + (FCFn × (1+g)) ÷ (WACC - g) ÷ (1 + WACC)^n",
        "components": ["projected_fcf", "wacc", "terminal_growth", "projection_years"],
        "category": "Valuation",
        "benchmark": {"low": 0, "high": 1e12},
        "explanations": {
            "beginner": "The 'true value' of a company based on all the cash it will generate in the future, brought back to today's dollars. If stock price is below this, it might be undervalued.",
            "intermediate": "DCF sums the present value of projected free cash flows plus a terminal value (value beyond projection period). Key inputs: growth rates, WACC, and terminal multiple or perpetuity growth. Small input changes create large value swings - sensitivity analysis is critical.",
            "professional": "Two-stage or three-stage models for high-growth companies. Terminal value often 60-80% of total - be conservative with perpetuity growth (≤ GDP growth, ~2-3%). Cross-check with exit multiple method. Adjust for: stock-based comp, operating leases, NOLs, and non-operating assets. Monte Carlo simulation for range of outcomes."
        },
        "interpretation": {
            "low": "Small or distressed company value",
            "normal": "N/A - compare to market cap",
            "high": "Large enterprise value"
        }
    },
    
    "Margin_of_Safety": {
        "name": "Margin of Safety",
        "equation": "(Intrinsic Value - Market Price) / Intrinsic Value",
        "equation_formula": "(DCF Value - Current Stock Price) ÷ DCF Value × 100%",
        "components": ["intrinsic_value", "current_price"],
        "category": "Valuation",
        "benchmark": {"low": 15, "high": 50},
        "explanations": {
            "beginner": "The 'discount' you're getting if you buy below what you think the company is worth. Bigger discount = safer investment.",
            "intermediate": "Benjamin Graham's concept: only buy when price is significantly below intrinsic value. This protects against estimation errors and unforeseen events. Value investors typically want 20-30% margin of safety.",
            "professional": "Margin of Safety should reflect: confidence in DCF inputs, business quality, and market volatility. Buffett: 'I want to pay 60 cents for a dollar.' Wide-moat businesses may warrant lower MoS (15-20%) while speculative situations need 40%+. Consider probability-weighted scenarios for range-based MoS."
        },
        "interpretation": {
            "low": "Small buffer - risky at current price",
            "normal": "Reasonable buffer for value investors",
            "high": "Large discount - potentially attractive"
        }
    },
    
    # ===== DEEP DIVE PROFITABILITY & CASH FLOW (HIGH ROI) =====
    
    "EBITDA_Margin": {
        "name": "EBITDA Margin",
        "equation": "EBITDA / Revenue",
        "equation_formula": "(Operating Income + Depreciation + Amortization) ÷ Revenue × 100%",
        "components": ["ebitda", "revenue"],
        "category": "Profitability",
        "benchmark": {"low": 10, "high": 25},
        "explanations": {
            "beginner": "How much of each sales dollar becomes operating cash before accounting adjustments. Higher = more profitable core business.",
            "intermediate": "EBITDA margin strips out non-cash charges (depreciation, amortization) to show operational profitability. Useful for comparing companies with different capital structures or age of assets.",
            "professional": "EBITDA is a proxy for operating cash flow but ignores CapEx requirements. Capital-intensive businesses (airlines, telecom) may have good EBITDA margins but poor FCF. For SaaS: Rule of 40 = Growth% + EBITDA Margin%. Adjusted EBITDA adds back stock-based comp - scrutinize these adjustments carefully."
        },
        "interpretation": {
            "low": "Thin operational margins",
            "normal": "Healthy operational profitability",
            "high": "Strong cash generation from operations"
        }
    },
    
    "FCF_Margin": {
        "name": "Free Cash Flow Margin",
        "equation": "Free Cash Flow / Revenue",
        "equation_formula": "(Operating Cash Flow - CapEx) ÷ Revenue × 100%",
        "components": ["free_cash_flow", "revenue"],
        "category": "Profitability",
        "benchmark": {"low": 5, "high": 20},
        "explanations": {
            "beginner": "What percentage of sales actually becomes cash the company can use freely - for dividends, buybacks, or growth.",
            "intermediate": "FCF margin is the ultimate profitability metric. Unlike net margin, it's actual cash, not accounting profits. High FCF margin = quality business. Track trends: declining FCF margin may indicate rising CapEx needs or working capital issues.",
            "professional": "FCF margin should be analyzed with revenue growth: high-growth companies reinvest FCF (low margin but acceptable). Mature companies should have FCF margin approaching net margin. Sector benchmarks: SaaS 15-25%, Consumer Staples 8-15%, Industrials 5-12%. Normalize for lumpy CapEx in capital-intensive industries."
        },
        "interpretation": {
            "low": "Heavy reinvestment or poor conversion",
            "normal": "Healthy cash conversion",
            "high": "Excellent free cash flow generation"
        }
    },
    
    "FCF_Conversion": {
        "name": "FCF Conversion Rate",
        "equation": "Free Cash Flow / Net Income",
        "equation_formula": "(Operating CF - CapEx) ÷ Net Income × 100%",
        "components": ["free_cash_flow", "net_income"],
        "category": "Profitability",
        "benchmark": {"low": 80, "high": 120},
        "explanations": {
            "beginner": "How much of reported profit actually becomes real cash. Over 100% = company generates more cash than reported profits.",
            "intermediate": "FCF conversion shows earnings quality. Consistently above 100% indicates conservative accounting. Below 80% may signal aggressive revenue recognition or high CapEx needs. Warren Buffett looks for this metric.",
            "professional": "Decompose: OCF/NI × FCF/OCF. High D&A relative to CapEx inflates conversion (asset-light models). Watch for: working capital manipulation (channel stuffing), one-time CapEx vs maintenance CapEx. Sustainable FCF conversion typically 90-110%. Below 70% for multiple years is a red flag."
        },
        "interpretation": {
            "low": "Poor earnings quality or high CapEx",
            "normal": "Healthy cash conversion",
            "high": "Superior earnings quality"
        }
    },
    
    "OCF_to_Debt": {
        "name": "OCF to Debt Ratio",
        "equation": "Operating Cash Flow / Total Debt",
        "equation_formula": "Operating Cash Flow ÷ (Short-term + Long-term Debt) × 100%",
        "components": ["operating_cash_flow", "total_debt"],
        "category": "Leverage",
        "benchmark": {"low": 20, "high": 50},
        "explanations": {
            "beginner": "How quickly the company could pay off all its debt using just its operating cash. Higher = safer.",
            "intermediate": "OCF/Debt measures debt serviceability from operations alone. Above 40% indicates strong coverage. Below 20% suggests reliance on refinancing or asset sales to service debt.",
            "professional": "More reliable than income-based coverage ratios (interest coverage). Credit analysts use this for long-term debt sustainability. Compare to debt maturity schedule: if 30% of debt matures next year but OCF/Debt is only 25%, refinancing risk exists. Cyclical companies need higher ratios as OCF volatility increases."
        },
        "interpretation": {
            "low": "High debt burden relative to cash generation",
            "normal": "Manageable debt levels",
            "high": "Strong debt coverage from operations"
        }
    },
    
    "DuPont_ROE": {
        "name": "DuPont ROE Decomposition",
        "equation": "Net Margin × Asset Turnover × Equity Multiplier",
        "equation_formula": "(Net Income ÷ Revenue) × (Revenue ÷ Assets) × (Assets ÷ Equity)",
        "components": ["net_income", "revenue", "total_assets", "shareholders_equity"],
        "category": "Profitability",
        "benchmark": {"low": 10, "high": 20},
        "explanations": {
            "beginner": "Breaks down ROE into three parts: profit margin (how much you keep), efficiency (how hard assets work), and leverage (how much you borrow).",
            "intermediate": "DuPont analysis reveals the DRIVERS of ROE. Same 15% ROE can come from: high margins (Apple), high turnover (Walmart), or high leverage (banks). Each has different risk profile.",
            "professional": "5-factor DuPont: Tax Burden × Interest Burden × EBIT Margin × Asset Turnover × Leverage. Identifies if ROE improvement comes from operations (sustainable) or financial engineering (risky). Track component trends: declining margin offset by rising leverage = deteriorating quality. Compare components to peers to identify competitive advantages."
        },
        "interpretation": {
            "low": "Weak returns on equity",
            "normal": "Adequate return on equity",
            "high": "Strong returns - verify source via decomposition"
        }
    },
    
    "Revenue_per_Employee": {
        "name": "Revenue per Employee",
        "equation": "Total Revenue / Number of Employees",
        "equation_formula": "Annual Revenue ÷ Full-time Employees",
        "components": ["revenue", "employee_count"],
        "category": "Efficiency",
        "benchmark": {"low": 200000, "high": 500000},
        "explanations": {
            "beginner": "How much revenue each employee generates on average. Higher = more efficient workforce.",
            "intermediate": "Revenue per employee measures labor productivity. Tech companies often have $500K+, while labor-intensive retail may have $150K. Rising trend indicates improving efficiency or successful automation.",
            "professional": "Normalize for industry: capital-intensive businesses (refineries) have high rev/employee but low margins. Compare to compensation costs for true efficiency. Rising revenue/employee with flat headcount = operating leverage. For acquisitions, compare to integration synergy targets. FTE vs contractor adjustments may be needed."
        },
        "interpretation": {
            "low": "Labor-intensive model or inefficiency",
            "normal": "Industry-appropriate productivity",
            "high": "Highly efficient or capital-intensive"
        }
    },
    
    "Operating_Leverage": {
        "name": "Operating Leverage",
        "equation": "% Change in Operating Income / % Change in Revenue",
        "equation_formula": "(Operating Income Growth %) ÷ (Revenue Growth %)",
        "components": ["operating_income_growth", "revenue_growth"],
        "category": "Profitability",
        "benchmark": {"low": 1.0, "high": 2.5},
        "explanations": {
            "beginner": "How much faster profits grow compared to sales. Leverage of 2 means if sales grow 10%, profits grow 20%.",
            "intermediate": "High operating leverage = high fixed costs. Great in good times (profits surge with small revenue increase) but dangerous in downturns (profits collapse quickly). Software companies typically have high operating leverage.",
            "professional": "Operating leverage = Contribution Margin / Operating Income. Near breakeven, operating leverage approaches infinity. Airlines and hotels have extreme operating leverage - analyze margin of safety carefully. For M&A, high operating leverage targets benefit more from revenue synergies."
        },
        "interpretation": {
            "low": "Variable cost structure, limited upside",
            "normal": "Balanced cost structure",
            "high": "High fixed costs, amplified profit swings"
        }
    },
    
    "Cash_Conversion_Cycle": {
        "name": "Cash Conversion Cycle",
        "equation": "DIO + DSO - DPO",
        "equation_formula": "Days Inventory Outstanding + Days Sales Outstanding - Days Payables Outstanding",
        "components": ["days_inventory", "days_receivable", "days_payable"],
        "category": "Efficiency",
        "benchmark": {"low": 0, "high": 60},
        "explanations": {
            "beginner": "How many days it takes to turn inventory purchases into cash from customers. Lower = faster cash collection = less working capital needed.",
            "intermediate": "CCC measures working capital efficiency. Negative CCC (like Amazon, Dell) means suppliers fund operations - a powerful advantage. Rising CCC indicates deteriorating efficiency or competitive weakness.",
            "professional": "Decompose: DIO = (Inventory/COGS) × 365; DSO = (AR/Revenue) × 365; DPO = (AP/COGS) × 365. Benchmark each component vs peers. Extended payment terms to suppliers (high DPO) may indicate market power or liquidity stress. For seasonal businesses, use average balances. JIT inventory management targets DIO < 15 days."
        },
        "interpretation": {
            "low": "Excellent working capital efficiency (negative is ideal)",
            "normal": "Standard cash cycle",
            "high": "Capital tied up in operations"
        }
    },
    
    "Capex_to_Revenue": {
        "name": "CapEx Intensity",
        "equation": "Capital Expenditures / Revenue",
        "equation_formula": "Annual CapEx ÷ Annual Revenue × 100%",
        "components": ["capex", "revenue"],
        "category": "Efficiency",
        "benchmark": {"low": 3, "high": 15},
        "explanations": {
            "beginner": "How much of sales the company must reinvest in equipment and buildings just to keep operating. Lower = more cash left over for investors.",
            "intermediate": "CapEx intensity indicates capital requirements of the business model. Asset-light businesses (software, consulting) have 1-3%, while utilities and telecom may be 15-25%. Compare to depreciation for maintenance vs growth CapEx.",
            "professional": "Maintenance CapEx ≈ Depreciation for mature companies. Growth CapEx = Total CapEx - Depreciation. For FCF analysis, distinguish between the two. Rising CapEx/Revenue may indicate capacity expansion (bullish) or aging assets requiring replacement (bearish). R&D capitalization in tech affects comparability."
        },
        "interpretation": {
            "low": "Asset-light, high cash conversion",
            "normal": "Moderate capital requirements",
            "high": "Capital-intensive, heavy reinvestment"
        }
    },
    
    # ===== RISK METRICS (HIGH ROI FOR INVESTORS) =====
    
    "Beta": {
        "name": "Beta (Market Sensitivity)",
        "equation": "Cov(Stock, Market) / Var(Market)",
        "equation_formula": "Covariance(Stock Returns, Market Returns) ÷ Variance(Market Returns)",
        "components": ["stock_returns", "market_returns"],
        "category": "Risk",
        "benchmark": {"low": 0.8, "high": 1.5},
        "explanations": {
            "beginner": "How much the stock moves compared to the overall market. Beta of 1.5 means if market goes up 10%, stock typically goes up 15%.",
            "intermediate": "Beta measures systematic (market) risk that can't be diversified away. High beta = more volatile and risky. Utilities typically have beta < 0.7, tech stocks often > 1.3. Used in CAPM to calculate required return.",
            "professional": "Use 5-year monthly returns vs S&P 500 for standard beta. Adjust for mean reversion: Adjusted Beta = (2/3 × Raw Beta) + (1/3 × 1.0). Levered vs unlevered beta for comparable analysis: βu = βL / (1 + (1-T) × D/E). Industry beta may be more reliable for private companies. Beta instability during market stress limits predictive power."
        },
        "interpretation": {
            "low": "Defensive, less volatile than market",
            "normal": "Market-average volatility",
            "high": "Aggressive, amplified market moves"
        }
    },
    
    "Alpha": {
        "name": "Alpha (Excess Return)",
        "equation": "Actual Return - Expected Return (CAPM)",
        "equation_formula": "Stock Return - [Rf + β × (Market Return - Rf)]",
        "components": ["stock_return", "risk_free_rate", "beta", "market_return"],
        "category": "Risk",
        "benchmark": {"low": -2, "high": 5},
        "explanations": {
            "beginner": "The extra return above what you'd expect given the risk. Positive alpha = beating the market on a risk-adjusted basis.",
            "intermediate": "Alpha measures manager skill or stock-specific performance beyond market moves. Consistently positive alpha is rare and valuable. Negative alpha means underperformance after adjusting for beta.",
            "professional": "Jensen's Alpha from CAPM regression. For more accurate alpha, use Fama-French 3-factor or 5-factor model to control for size, value, momentum, profitability, and investment factors. Alpha persistence is debated - academic research shows most alpha is luck, not skill. Transaction costs and taxes erode gross alpha."
        },
        "interpretation": {
            "low": "Underperformance vs risk-adjusted expectation",
            "normal": "Returns consistent with risk taken",
            "high": "Outperformance - skill or anomaly"
        }
    },
    
    "Sharpe_Ratio": {
        "name": "Sharpe Ratio",
        "equation": "(Return - Risk-Free Rate) / Standard Deviation",
        "equation_formula": "(Portfolio Return - Treasury Bill Rate) ÷ Volatility (Std Dev)",
        "components": ["portfolio_return", "risk_free_rate", "standard_deviation"],
        "category": "Risk",
        "benchmark": {"low": 0.5, "high": 1.5},
        "explanations": {
            "beginner": "How much extra return you get for each unit of risk. Higher = better. Sharpe of 1.0 means you get 1% extra return for each 1% of volatility.",
            "intermediate": "Sharpe ratio enables comparing investments with different risk levels. S&P 500 long-term Sharpe is ~0.4. Above 1.0 is good, above 2.0 is excellent. Below 0 means risk-free rate beats the investment.",
            "professional": "Assumes normal distribution of returns (problematic for assets with skew or fat tails). Sortino ratio uses downside deviation only. Calmar ratio uses max drawdown. For hedge funds, monthly Sharpe × √12 gives annualized. Beware: leverage can inflate Sharpe if max drawdown is ignored."
        },
        "interpretation": {
            "low": "Poor risk-adjusted returns",
            "normal": "Reasonable risk-adjusted returns",
            "high": "Excellent risk-adjusted returns"
        }
    },
    
    "Volatility": {
        "name": "Volatility (Standard Deviation)",
        "equation": "Standard Deviation of Returns",
        "equation_formula": "√[Σ(Return - Mean Return)² ÷ (n-1)] × √252 for annualized",
        "components": ["daily_returns"],
        "category": "Risk",
        "benchmark": {"low": 15, "high": 40},
        "explanations": {
            "beginner": "How much the stock price bounces around. Higher volatility = bigger swings up and down. Expressed as annual percentage.",
            "intermediate": "Volatility measures total risk (both up and down). S&P 500 averages ~15% annual volatility. Individual stocks typically 25-50%. Options pricing depends heavily on volatility (VIX for market).",
            "professional": "Historical vs implied volatility: IV from options pricing reflects forward-looking expectations. Realized volatility can be calculated from daily, weekly, or monthly returns (different results). GARCH models capture volatility clustering. Parkinson and Garman-Klass use high/low prices for more efficient estimation."
        },
        "interpretation": {
            "low": "Stable, lower risk",
            "normal": "Average stock volatility",
            "high": "Highly volatile, higher risk"
        }
    },
    
    "Max_Drawdown": {
        "name": "Maximum Drawdown",
        "equation": "(Trough - Peak) / Peak",
        "equation_formula": "(Lowest Value - Previous Highest Value) ÷ Previous Highest Value × 100%",
        "components": ["peak_value", "trough_value"],
        "category": "Risk",
        "benchmark": {"low": 20, "high": 50},
        "explanations": {
            "beginner": "The biggest drop from peak to bottom. A stock that went from $100 to $60 had a 40% drawdown. Shows worst-case pain you might experience.",
            "intermediate": "Max drawdown is the most realistic risk measure for investors. S&P 500 has had 50%+ drawdowns (2008-09, 2000-02). Recovery time matters: 50% loss needs 100% gain to break even.",
            "professional": "Use max drawdown for position sizing and risk management. Calmar ratio = CAGR / Max Drawdown. Consider: time to recovery, drawdown duration, and underwater period. For portfolios, analyze drawdown contribution by asset. Conditional drawdown (average of worst X%) may be more robust than single max."
        },
        "interpretation": {
            "low": "Resilient, limited downside",
            "normal": "Typical equity drawdown risk",
            "high": "Severe peak-to-trough losses"
        }
    },
    
    "VaR": {
        "name": "Value at Risk (95%)",
        "equation": "95th Percentile of Loss Distribution",
        "equation_formula": "Return at 5th percentile of historical returns × Portfolio Value",
        "components": ["confidence_level", "time_horizon", "portfolio_value"],
        "category": "Risk",
        "benchmark": {"low": 2, "high": 5},
        "explanations": {
            "beginner": "The maximum you could lose on 95% of days. 5% VaR of 3% means on most days, you won't lose more than 3%, but 5% of days could be worse.",
            "intermediate": "VaR quantifies tail risk. 95% VaR ignores the worst 5% of days. Banks use VaR for capital requirements. Limitations: doesn't say HOW BAD the 5% worst days are.",
            "professional": "Historical VaR (percentile), Parametric VaR (assumes normal), Monte Carlo VaR (simulation). CVaR (Conditional VaR / Expected Shortfall) measures average loss beyond VaR - required by Basel III. VaR is not subadditive and can underestimate diversification benefits. Stress testing complements VaR for tail risk."
        },
        "interpretation": {
            "low": "Limited daily loss potential",
            "normal": "Typical stock risk exposure",
            "high": "Significant daily loss potential"
        }
    },
    
    "R_Squared": {
        "name": "R-Squared",
        "equation": "Explained Variance / Total Variance",
        "equation_formula": "1 - (Σ(Actual - Predicted)² ÷ Σ(Actual - Mean)²)",
        "components": ["stock_returns", "market_returns"],
        "category": "Risk",
        "benchmark": {"low": 0.3, "high": 0.8},
        "explanations": {
            "beginner": "How much of the stock's movement is explained by the market. R² of 0.80 means 80% of moves follow the market, 20% is stock-specific.",
            "intermediate": "R-squared shows diversification potential. Low R² = more idiosyncratic risk that can be diversified away. High R² = stock moves mostly with market. Index funds have R² near 1.0.",
            "professional": "R² = Beta² × (σm/σs)². Low R² makes beta estimates unreliable. For fund evaluation, high R² means returns explained by market exposure (passive), low R² suggests active management or alternative strategies. Adjust R² for degrees of freedom when comparing models with different factors."
        },
        "interpretation": {
            "low": "Stock-specific factors dominate",
            "normal": "Mix of market and specific drivers",
            "high": "Returns closely track market"
        }
    },
    
    "Information_Ratio": {
        "name": "Information Ratio",
        "equation": "Alpha / Tracking Error",
        "equation_formula": "(Portfolio Return - Benchmark Return) ÷ Std Dev of Excess Returns",
        "components": ["portfolio_return", "benchmark_return", "tracking_error"],
        "category": "Risk",
        "benchmark": {"low": 0.3, "high": 0.7},
        "explanations": {
            "beginner": "How consistently a fund beats its benchmark for each unit of extra risk taken. Higher = more skilled management.",
            "intermediate": "Information Ratio measures active management skill. IR of 0.5 is good, 1.0 is excellent. Unlike Sharpe, IR uses benchmark (not risk-free rate) and tracking error (not total volatility).",
            "professional": "IR = IC × √(Breadth) per fundamental law of active management. IC = correlation of forecasts to outcomes. Breadth = number of independent bets. High IR from concentrated positions is riskier than from many small bets. IR > 0.5 sustained over 5+ years is rare. Beware of survivorship bias in fund IR data."
        },
        "interpretation": {
            "low": "Weak active management",
            "normal": "Competent active management",
            "high": "Skilled consistent outperformance"
        }
    },
}

# =============================================================================
# RATIO CARD COMPONENT
# =============================================================================

def render_ratio_card(
    ratio_key: str,
    value: Union[float, int, None],
    components_dict: Optional[Dict[str, Any]] = None,
    depth: str = "beginner",
    show_equation: bool = True,
    compact: bool = False
):
    """
    Render a single ratio card with equation display and multi-depth explanations.
    
    Args:
        ratio_key: Key from RATIO_DEFINITIONS (e.g., "PE_Ratio")
        value: The calculated ratio value
        components_dict: Dict of component values used in calculation
        depth: "beginner", "intermediate", or "professional"
        show_equation: Whether to show the equation breakdown
        compact: If True, renders a smaller inline version
    """
    
    if ratio_key not in RATIO_DEFINITIONS:
        st.warning(f"Unknown ratio: {ratio_key}")
        return
    
    definition = RATIO_DEFINITIONS[ratio_key]
    
    # Format value
    if value is None:
        formatted_value = "N/A"
        value_color = "#6b7280"  # Gray
    else:
        # Determine if it's a percentage or ratio
        if "Margin" in ratio_key or "ROE" in ratio_key or "ROIC" in ratio_key or "Growth" in ratio_key or "Yield" in ratio_key:
            # It's a percentage
            if abs(value) < 5:  # Likely decimal format (0.15 = 15%)
                formatted_value = f"{value * 100:.1f}%"
                value_numeric = value * 100
            else:
                formatted_value = f"{value:.1f}%"
                value_numeric = value
        elif "Ratio" in ratio_key or "to_" in ratio_key or "Turnover" in ratio_key or "Coverage" in ratio_key:
            formatted_value = f"{value:.2f}x"
            value_numeric = value
        else:
            formatted_value = f"{value:.2f}"
            value_numeric = value
        
        # Determine color based on benchmarks
        benchmark = definition.get("benchmark", {})
        low = benchmark.get("low", 0)
        high = benchmark.get("high", 100)
        
        # For some ratios, higher is better; for others, lower is better
        inverse_ratios = ["PE_Ratio", "PB_Ratio", "PS_Ratio", "EV_EBITDA", "Debt_to_Equity", "Payout_Ratio"]
        
        if ratio_key in inverse_ratios:
            if value_numeric < low:
                value_color = "#22c55e"  # Green (good)
            elif value_numeric > high:
                value_color = "#ef4444"  # Red (bad)
            else:
                value_color = "#60a5fa"  # Blue (neutral)
        else:
            if value_numeric > high:
                value_color = "#22c55e"  # Green (good)
            elif value_numeric < low:
                value_color = "#ef4444"  # Red (bad)
            else:
                value_color = "#60a5fa"  # Blue (neutral)
    
    # Compact mode
    if compact:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1a1a2e, #0f0f1a); border-radius: 8px; padding: 12px; margin: 4px 0; border-left: 3px solid {value_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #9ca3af; font-size: 0.85rem;">{definition['name']}</span>
                <span style="color: {value_color}; font-weight: 600; font-size: 1.1rem;">{formatted_value}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Full card mode
    card_html = f"""
    <div style="background: linear-gradient(145deg, #1a1a2e, #0f0f1a); border-radius: 12px; padding: 20px; margin: 10px 0; border: 1px solid #2d2d44;">
        <!-- Header -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <span style="color: #9ca3af; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">{definition['category']}</span>
                <h3 style="color: #e2e8f0; margin: 4px 0 0 0; font-size: 1.1rem;">{definition['name']}</h3>
            </div>
            <div style="text-align: right;">
                <div style="color: {value_color}; font-size: 1.8rem; font-weight: 700;">{formatted_value}</div>
            </div>
        </div>
    """
    
    # Equation display
    if show_equation and value is not None:
        card_html += f"""
        <!-- Equation Box -->
        <div style="background: #0f172a; border-radius: 8px; padding: 12px; margin: 12px 0; border: 1px solid #334155;">
            <div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 6px;">FORMULA</div>
            <div style="color: #60a5fa; font-family: 'SF Mono', 'Roboto Mono', monospace; font-size: 0.9rem;">
                {definition['equation_formula']}
            </div>
        """
        
        # Show actual component values if provided
        if components_dict:
            component_values = []
            for comp in definition.get("components", []):
                if comp in components_dict:
                    comp_val = components_dict[comp]
                    if comp_val is not None:
                        # Format component value
                        if abs(comp_val) >= 1e9:
                            comp_formatted = f"${comp_val/1e9:.2f}B"
                        elif abs(comp_val) >= 1e6:
                            comp_formatted = f"${comp_val/1e6:.2f}M"
                        elif abs(comp_val) >= 1000:
                            comp_formatted = f"${comp_val:,.0f}"
                        elif abs(comp_val) < 1:
                            comp_formatted = f"{comp_val:.4f}"
                        else:
                            comp_formatted = f"{comp_val:.2f}"
                        
                        comp_name = comp.replace("_", " ").title()
                        component_values.append(f"<span style='color: #9ca3af;'>{comp_name}:</span> <span style='color: #f0f0f0;'>{comp_formatted}</span>")
            
            if component_values:
                card_html += f"""
                <div style="margin-top: 8px; font-size: 0.8rem; border-top: 1px solid #334155; padding-top: 8px;">
                    {' | '.join(component_values)}
                </div>
                """
        
        card_html += "</div>"
    
    # Explanation based on depth
    explanation = definition["explanations"].get(depth, definition["explanations"]["beginner"])
    
    card_html += f"""
        <!-- Explanation -->
        <div style="color: #a0aec0; font-size: 0.85rem; line-height: 1.5; margin-top: 12px;">
            {explanation}
        </div>
    """
    
    # Interpretation
    if value is not None:
        benchmark = definition.get("benchmark", {})
        low = benchmark.get("low", 0)
        high = benchmark.get("high", 100)
        interpretation = definition.get("interpretation", {})
        
        # Determine interpretation
        if value_numeric < low:
            interp_key = "low"
            interp_icon = "↓"
        elif value_numeric > high:
            interp_key = "high"
            interp_icon = "↑"
        else:
            interp_key = "normal"
            interp_icon = "→"
        
        interp_text = interpretation.get(interp_key, "")
        if interp_text:
            card_html += f"""
            <div style="margin-top: 12px; padding: 10px; background: rgba(96, 165, 250, 0.1); border-radius: 6px; border-left: 3px solid {value_color};">
                <span style="color: {value_color}; font-weight: 600;">{interp_icon} {interp_text}</span>
            </div>
            """
    
    card_html += "</div>"
    
    st.markdown(card_html, unsafe_allow_html=True)


def render_ratio_grid(
    ratios_dict: Dict[str, float],
    components_dict: Optional[Dict[str, Any]] = None,
    depth: str = "beginner",
    category_filter: Optional[str] = None,
    columns: int = 2
):
    """
    Render a grid of ratio cards.
    
    Args:
        ratios_dict: Dict of ratio_key -> value
        components_dict: Dict of component values for equation display
        depth: Explanation depth level
        category_filter: Only show ratios from this category
        columns: Number of columns in grid
    """
    
    # Filter ratios
    available_ratios = [k for k in ratios_dict.keys() if k in RATIO_DEFINITIONS]
    
    if category_filter:
        available_ratios = [
            k for k in available_ratios 
            if RATIO_DEFINITIONS[k].get("category") == category_filter
        ]
    
    if not available_ratios:
        st.info("No ratios available for display")
        return
    
    # Create grid
    cols = st.columns(columns)
    for idx, ratio_key in enumerate(available_ratios):
        with cols[idx % columns]:
            render_ratio_card(
                ratio_key=ratio_key,
                value=ratios_dict.get(ratio_key),
                components_dict=components_dict,
                depth=depth,
                show_equation=True
            )


def render_depth_selector(key: str = "ratio_depth") -> str:
    """
    Render a depth level selector for the user.
    Returns the selected depth level.
    """
    
    depth_options = {
        "beginner": "Beginner (Simple explanations)",
        "intermediate": "Intermediate (Standard analysis)",
        "professional": "Professional (CFA-level depth)"
    }
    
    # Custom CSS for selector
    st.markdown("""
    <style>
    .depth-selector {
        background: linear-gradient(145deg, #1a1a2e, #0f0f1a);
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 16px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    selected = st.radio(
        "Explanation Depth",
        options=list(depth_options.keys()),
        format_func=lambda x: depth_options[x],
        horizontal=True,
        key=key,
        help="Choose how detailed you want the ratio explanations"
    )
    
    return selected


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_ratio_categories() -> list:
    """Get list of unique ratio categories"""
    categories = set()
    for defn in RATIO_DEFINITIONS.values():
        categories.add(defn.get("category", "Other"))
    return sorted(list(categories))


def get_ratios_by_category(category: str) -> list:
    """Get list of ratio keys for a specific category"""
    return [
        key for key, defn in RATIO_DEFINITIONS.items()
        if defn.get("category") == category
    ]


def extract_components_from_financials(financials: Dict) -> Dict[str, Any]:
    """
    Extract component values from financials dict for equation display.
    
    Args:
        financials: The financials dict from extraction
        
    Returns:
        Dict with component values (current_price, eps, revenue, etc.)
    """
    components = {}
    
    # Try to extract from various locations in financials
    
    # Market data
    market_data = financials.get('market_data', {})
    if isinstance(market_data, dict):
        components['current_price'] = market_data.get('current_price')
        components['market_cap'] = market_data.get('market_cap')
        components['enterprise_value'] = market_data.get('enterprise_value')
        components['eps'] = market_data.get('eps')
        components['annual_dividend'] = market_data.get('dividend_rate')
    
    # Ratios DataFrame
    ratios = financials.get('ratios', pd.DataFrame())
    if isinstance(ratios, pd.DataFrame) and not ratios.empty:
        for idx in ratios.index:
            if idx in ['Revenue', 'Total_Revenue']:
                components['revenue'] = ratios.loc[idx].iloc[0]
            elif idx in ['Net_Income', 'Net Income']:
                components['net_income'] = ratios.loc[idx].iloc[0]
            elif idx in ['Gross_Profit', 'Gross Profit']:
                components['gross_profit'] = ratios.loc[idx].iloc[0]
            elif idx in ['Operating_Income', 'Operating Income']:
                components['operating_income'] = ratios.loc[idx].iloc[0]
            elif idx in ['Total_Debt', 'Total Debt']:
                components['total_debt'] = ratios.loc[idx].iloc[0]
            elif idx in ['Total_Equity', "Stockholders' Equity", 'Shareholders Equity']:
                components['shareholders_equity'] = ratios.loc[idx].iloc[0]
            elif idx in ['Current_Assets', 'Current Assets']:
                components['current_assets'] = ratios.loc[idx].iloc[0]
            elif idx in ['Current_Liabilities', 'Current Liabilities']:
                components['current_liabilities'] = ratios.loc[idx].iloc[0]
            elif idx in ['EBITDA']:
                components['ebitda'] = ratios.loc[idx].iloc[0]
    
    # Income statement
    income = financials.get('income_statement', pd.DataFrame())
    if isinstance(income, pd.DataFrame) and not income.empty:
        # Try to get latest values
        try:
            for idx in income.index:
                idx_lower = str(idx).lower()
                if 'total revenue' in idx_lower or idx_lower == 'revenue':
                    if 'revenue' not in components or components['revenue'] is None:
                        components['revenue'] = income.loc[idx].iloc[0]
                elif 'net income' in idx_lower:
                    if 'net_income' not in components or components['net_income'] is None:
                        components['net_income'] = income.loc[idx].iloc[0]
                elif 'gross profit' in idx_lower:
                    if 'gross_profit' not in components or components['gross_profit'] is None:
                        components['gross_profit'] = income.loc[idx].iloc[0]
                elif 'operating income' in idx_lower:
                    if 'operating_income' not in components or components['operating_income'] is None:
                        components['operating_income'] = income.loc[idx].iloc[0]
        except Exception:
            pass
    
    # Balance sheet
    balance = financials.get('balance_sheet', pd.DataFrame())
    if isinstance(balance, pd.DataFrame) and not balance.empty:
        try:
            for idx in balance.index:
                idx_lower = str(idx).lower()
                if 'total asset' in idx_lower:
                    components['total_assets'] = balance.loc[idx].iloc[0]
                elif 'current asset' in idx_lower:
                    if 'current_assets' not in components or components['current_assets'] is None:
                        components['current_assets'] = balance.loc[idx].iloc[0]
                elif 'current liabilit' in idx_lower:
                    if 'current_liabilities' not in components or components['current_liabilities'] is None:
                        components['current_liabilities'] = balance.loc[idx].iloc[0]
                elif 'inventory' in idx_lower:
                    components['inventory'] = balance.loc[idx].iloc[0]
                elif 'total debt' in idx_lower:
                    if 'total_debt' not in components or components['total_debt'] is None:
                        components['total_debt'] = balance.loc[idx].iloc[0]
                elif 'stockholder' in idx_lower or 'shareholder' in idx_lower:
                    if 'shareholders_equity' not in components or components['shareholders_equity'] is None:
                        components['shareholders_equity'] = balance.loc[idx].iloc[0]
        except Exception:
            pass
    
    return components


# =============================================================================
# TEST / DEMO
# =============================================================================

if __name__ == "__main__":
    # Demo mode
    st.set_page_config(page_title="Ratio Card Demo", layout="wide")
    
    st.title("RatioCard Component Demo")
    
    # Depth selector
    depth = render_depth_selector()
    
    st.markdown("---")
    
    # Sample data
    sample_ratios = {
        "PE_Ratio": 22.5,
        "ROE": 0.18,  # 18%
        "Debt_to_Equity": 0.45,
        "Current_Ratio": 1.8,
        "Gross_Margin": 42.5,
        "Revenue_Growth": 12.3,
    }
    
    sample_components = {
        "current_price": 175.50,
        "eps": 7.80,
        "net_income": 94_000_000_000,
        "shareholders_equity": 62_000_000_000,
        "revenue": 385_000_000_000,
    }
    
    # Render grid
    render_ratio_grid(
        ratios_dict=sample_ratios,
        components_dict=sample_components,
        depth=depth,
        columns=2
    )

