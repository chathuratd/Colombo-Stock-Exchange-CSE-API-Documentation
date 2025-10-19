# 📊 Investment Metrics Extraction Map

## What Gets Extracted from Financial Reports

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FINANCIAL REPORT (PDF/TXT)                       │
│                                                                     │
│  [Annual Report 2024]                                              │
│  - Financial Statements                                            │
│  - Notes to Accounts                                               │
│  - Management Commentary                                           │
│  - Corporate Governance                                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────────┐
         │   FINANCIAL EXTRACTOR PROCESSING           │
         └────────────────────────────────────────────┘
                              │
                              ▼
    ┌─────────────┬──────────────┬────────────┬────────────────┐
    │             │              │            │                │
    ▼             ▼              ▼            ▼                ▼
┌────────┐  ┌────────────┐  ┌────────┐  ┌───────────┐  ┌──────────┐
│BALANCE │  │  INCOME    │  │  CASH  │  │  EQUITY   │  │INVESTMENT│
│ SHEET  │  │ STATEMENT  │  │  FLOW  │  │ STATEMENT │  │ METRICS  │
└────────┘  └────────────┘  └────────┘  └───────────┘  └──────────┘
```

## 📋 Extracted Financial Statements

### 1. Balance Sheet
```
Assets (Rs '000)                  2024        2023        2022
─────────────────────────────────────────────────────────────
Cash & Bank Balances            123,456     110,234      98,765
Investments                     450,000     420,000     380,000
Loans & Advances              5,600,000   5,200,000   4,800,000
...
TOTAL ASSETS                  8,500,000   7,800,000   7,200,000

Liabilities
─────────────────────────────────────────────────────────────
Deposits                      6,200,000   5,800,000   5,400,000
Borrowings                      450,000     380,000     350,000
...
TOTAL LIABILITIES             7,200,000   6,600,000   6,100,000

Equity
─────────────────────────────────────────────────────────────
Share Capital                   120,000     120,000     120,000
Reserves                      1,180,000   1,080,000     980,000
TOTAL EQUITY                  1,300,000   1,200,000   1,100,000
```

### 2. Income Statement
```
Items (Rs '000)                   2024        2023        2022
─────────────────────────────────────────────────────────────
Interest Income                 680,000     620,000     560,000
Interest Expense               (280,000)   (260,000)   (240,000)
Net Interest Income             400,000     360,000     320,000
...
Profit Before Tax               185,000     168,000     152,000
Tax                            (55,000)    (50,000)    (45,000)
NET PROFIT                      130,000     118,000     107,000
```

### 3. Cash Flow Statement
```
Activities (Rs '000)              2024        2023        2022
─────────────────────────────────────────────────────────────
Operating Activities
Net Profit                      130,000     118,000     107,000
Adjustments                      25,000      22,000      18,000
...
Net Cash from Operations        165,000     152,000     135,000

Investing Activities           (125,000)   (110,000)    (95,000)
Financing Activities            (15,000)    (18,000)    (20,000)

NET CHANGE IN CASH               25,000      24,000      20,000
```

### 4. Equity Statement
```
Items (Rs '000)                   2024        2023        2022
─────────────────────────────────────────────────────────────
Opening Balance               1,200,000   1,100,000   1,020,000
Net Profit                      130,000     118,000     107,000
Dividends Paid                 (30,000)    (18,000)    (27,000)
CLOSING BALANCE               1,300,000   1,200,000   1,100,000
```

## 💰 Investment Metrics Extracted

### 📊 SHARE INFORMATION
```json
{
  "outstanding_shares": 1200000000,
  "market_capitalization": {
    "value": 450000,
    "unit": "million"
  },
  "share_price_range": {
    "high": 420.00,
    "low": 350.00
  }
}
```

### 💵 EARNINGS METRICS
```json
{
  "eps": {
    "basic_eps": 28.50,
    "diluted_eps": 28.20
  }
}
```

### 💸 DIVIDEND INFORMATION
```json
{
  "dividends": {
    "dividends_declared": [8.00, 4.00],
    "total_dividend_per_share": 12.00,
    "dividend_payout_ratio": 42.1,
    "dividend_yield": 3.2
  }
}
```

### 📈 VALUATION METRICS
```json
{
  "nav_per_share": {
    "value": 185.50
  },
  "market_info": {
    "pe_ratio": 14.75,
    "pb_ratio": 2.15
  }
}
```

### 📊 PROFITABILITY RATIOS
```json
{
  "financial_ratios": {
    "roe": 15.8,
    "roa": 1.9,
    "net_profit_margin": 18.2
  }
}
```

### 💧 LIQUIDITY RATIOS
```json
{
  "current_ratio": 1.45,
  "quick_ratio": 1.20
}
```

### ⚖️ LEVERAGE RATIOS
```json
{
  "debt_to_equity": 0.85,
  "debt_to_assets": 0.42
}
```

### 🏦 BANKING METRICS
```json
{
  "capital_adequacy": {
    "tier1_ratio": 14.2,
    "total_car": 16.8
  }
}
```

### 📈 GROWTH METRICS
```json
{
  "calculated": {
    "revenue_growth_pct": 12.5,
    "profit_growth_pct": 10.2,
    "asset_growth_pct": 8.9
  }
}
```

### 👔 GOVERNANCE & RISK
```json
{
  "governance": {
    "board_size": 10,
    "independent_directors": 5,
    "audit_committee": true,
    "risk_committee": true
  },
  "risk_factors": [
    "Credit risk from lending activities",
    "Market risk from investment portfolio",
    "Operational risk from system failures"
  ]
}
```

### 🔮 FUTURE OUTLOOK
```json
{
  "outlook": {
    "section_found": true,
    "summary": "The bank expects continued growth..."
  }
}
```

## 🎯 Data Validation Output

### Confidence Score
```
🎯 Overall Confidence: 92.5%
```

### Statement-Level Scores
```
✅ balance_sheet      : 95.0% confidence
✅ income_statement   : 100.0% confidence
✅ cash_flow          : 90.0% confidence
✅ equity_statement   : 85.0% confidence
```

### Issues & Warnings
```
🔴 Critical Issues: 0
⚠️ Warnings: 2
  - Column 'As at 31 Mar 2024' lacks clear year identifier
  - 5.2% missing values in 2023 column
```

### Validation Checks
```
✅ Column Structure: PASSED
✅ Year Headers: PASSED
✅ Numeric Data: PASSED
✅ Balance Sheet Balancing: PASSED
   Assets (8,500,000) = Liabilities+Equity (8,500,000)
   Difference: 0.0%
✅ Statement-Specific: PASSED
✅ Cross-Statement: PASSED
```

## 📄 Investment Analysis Report

### Report Structure
```
# Investment Analysis Report
## ABC Bank

### 📊 Executive Summary
- Quick Facts Table
- Key Metrics at a Glance

### 🎯 Data Quality Assessment
- Confidence Score: 92.5%
- Issues: 0
- Warnings: 2
- Status: ✅ EXCELLENT

### 💰 Key Investment Metrics
#### Earnings
- Basic EPS: Rs. 28.50
- ROE: 15.8%

#### Dividends
- Total DPS: Rs. 12.00
- Yield: 3.2%

#### Valuation
- P/E Ratio: 14.75
- P/B Ratio: 2.15

### 📈 Financial Performance Analysis
- Profitability Ratios
- Revenue Growth: 📈 12.5%
- Margin Analysis

### 💎 Valuation Analysis
- P/E Interpretation: Fair valuation
- P/B Assessment: Reasonable

### ⚠️ Risk Assessment
- Financial Risks
- Disclosed Risk Factors
- Liquidity Concerns

### 🏥 Financial Health Indicators
- Liquidity: ✅ Healthy (CR: 1.45)
- Leverage: ✅ Conservative (D/E: 0.85)

### 🚀 Growth Analysis
- Revenue Growth Trend
- Management Outlook

### 🎯 Investment Considerations
#### Strengths
- ✅ Strong ROE (15.8%)
- ✅ Healthy revenue growth
- ✅ Attractive dividend yield

#### Concerns
- ⚠️ Minor data quality warnings

### 📋 Detailed Financial Statements
[Full tables with all extracted data]

### 📎 Appendix
- Extraction metadata
- Quality scores by statement
```

## 🔄 Complete Data Flow

```
INPUT: Financial Report
    │
    ├─→ Statement Detector
    │       │
    │       ├─→ Balance Sheet → CSV
    │       ├─→ Income Statement → CSV
    │       ├─→ Cash Flow → CSV
    │       └─→ Equity Statement → CSV
    │
    ├─→ Investment Analyzer
    │       │
    │       └─→ investment_metrics.json
    │           ├─ Share Info
    │           ├─ EPS
    │           ├─ Dividends
    │           ├─ Ratios
    │           ├─ Governance
    │           └─ Outlook
    │
    ├─→ Data Validator
    │       │
    │       └─→ validation_report.json
    │           ├─ Confidence Score
    │           ├─ Issues
    │           ├─ Warnings
    │           └─ Recommendations
    │
    └─→ Report Generator (--report flag)
            │
            └─→ Investment_Analysis.md
                ├─ Executive Summary
                ├─ Metrics Analysis
                ├─ Risk Assessment
                └─ Recommendations
```

## 💡 Usage Quick Reference

### Basic Extraction
```powershell
python scripts\process_single.py report.pdf --company "ABC"
```
**Output:** 4 CSVs + metrics.json + validation.json

### With Report
```powershell
python scripts\process_single.py report.pdf --company "ABC" --report
```
**Output:** Above + Investment_Analysis.md

### Check Quality
```powershell
# Open validation_report.json
# Look for: overall_confidence score
# Goal: >90% for excellent quality
```

### Analyze Metrics
```powershell
# Open investment_metrics.json
# Review: EPS, Dividends, Ratios
# Compare: With historical data
```

---

**Legend:**
- ✅ Success / Good
- ⚠️ Warning / Review needed
- ❌ Error / Failed
- 📈 Growing / Positive
- 📉 Declining / Negative
- 🔴 Critical issue
- 🟡 Minor issue
- 🟢 All good
