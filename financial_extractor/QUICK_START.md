# 🚀 Quick Start - Investment Analysis

## One-Command Extraction

```powershell
python scripts\process_single.py <report.pdf> --company "CompanyName" --report
```

## What You Get

```
data/processed/CompanyName/
├── balance_sheet.csv                    # Asset, Liability, Equity data
├── income_statement.csv                 # Revenue, Expenses, Profit
├── cash_flow.csv                        # Cash movements
├── equity_statement.csv                 # Equity changes
├── investment_metrics.json              # 40+ metrics ⭐
├── validation_report.json               # Data quality ⭐
└── CompanyName_Investment_Analysis.md   # Full report ⭐
```

## Key Metrics Extracted

### Share Market Essentials
- ✅ EPS (Earnings Per Share)
- ✅ NAV per Share
- ✅ Dividend per Share
- ✅ Dividend Yield
- ✅ P/E Ratio
- ✅ P/B Ratio

### Financial Health
- ✅ ROE (Return on Equity)
- ✅ ROA (Return on Assets)
- ✅ Current Ratio
- ✅ Debt-to-Equity
- ✅ Profit Margin
- ✅ Revenue Growth

## Check Data Quality

```json
// Open: validation_report.json
{
  "overall_confidence": 92.5,  // ✅ >90% = Excellent
  "issues": [],                // 🔴 Critical errors
  "warnings": [],              // ⚠️ Minor concerns
  "recommendations": [
    "✅ Data quality is excellent. Safe to proceed with analysis."
  ]
}
```

## Quality Thresholds

| Confidence | Status | Action |
|-----------|--------|--------|
| 90-100% | ✅ EXCELLENT | Use with confidence |
| 80-89% | ✅ GOOD | Minor check |
| 70-79% | ⚠️ FAIR | Review needed |
| <70% | ⚠️ POOR | Manual verification |

## Investment Decision Checklist

### 1. Extract Data
```powershell
python scripts\process_single.py report.pdf --company "ABC" --report
```

### 2. Check Confidence Score
```
✅ >90% → Ready to analyze
⚠️ <90% → Verify key metrics
```

### 3. Review Key Metrics

**For Banking Stocks:**
- [ ] Capital Adequacy >11%
- [ ] ROE >15%
- [ ] P/E vs industry average
- [ ] Dividend yield >3%
- [ ] NPL ratio <3%

**For Other Stocks:**
- [ ] EPS growing
- [ ] P/E reasonable
- [ ] ROE >15%
- [ ] Debt-to-Equity <1
- [ ] Consistent dividends

### 4. Read Analysis Report
```markdown
Open: CompanyName_Investment_Analysis.md
Review:
- Executive Summary
- Strengths & Concerns
- Risk Assessment
```

### 5. Make Decision
- [ ] Compare with peers
- [ ] Verify source document
- [ ] Consider market conditions
- [ ] Assess risks
- [ ] Decide: BUY / HOLD / SELL

## Example Commands

### Single Company Analysis
```powershell
python scripts\process_single.py hnb-annual.pdf --company "HNB" --report
```

### Quick Check (No Report)
```powershell
python scripts\process_single.py dfcc-q1.pdf --company "DFCC"
```

### From Text File
```powershell
python scripts\process_single.py report.txt --company "ABC" --report
```

## Output Files Explained

### CSVs (4 files)
**Format:** Rows = Line items, Columns = Years
**Use:** Import to Excel, Python, R for analysis

### investment_metrics.json
**Contains:** 40+ calculated metrics
**Use:** Programming, dashboards, comparison

### validation_report.json
**Contains:** Quality scores, issues, warnings
**Use:** Reliability assessment

### Investment_Analysis.md
**Contains:** Complete analysis report
**Use:** Reading, presentations, documentation

## Common Metrics Interpretation

### EPS (Earnings Per Share)
- **Growing trend** → 📈 Good
- **Compare with peers** → Relative value
- **Higher is better** → More profitable

### P/E Ratio
- **<10** → Potentially undervalued
- **10-20** → Fair valuation
- **>30** → Potentially overvalued
- **Compare with industry** → Context matters

### ROE (Return on Equity)
- **>20%** → Excellent
- **15-20%** → Very good
- **10-15%** → Good
- **<10%** → Concerning

### Dividend Yield
- **>5%** → High yield
- **3-5%** → Good
- **<3%** → Low (but may reinvest)

### Debt-to-Equity
- **<0.5** → Very conservative
- **0.5-1.0** → Moderate
- **1.0-2.0** → Leveraged
- **>2.0** → Highly leveraged

## Validation Checks

### ✅ Balance Sheet Must Balance
```
Assets = Liabilities + Equity (±1%)
```

### ✅ Net Profit Consistency
```
Income Statement = Cash Flow Starting Point
```

### ✅ Equity Matching
```
Balance Sheet Total Equity = Equity Statement Closing
```

### ✅ Data Completeness
```
>80% cells filled with valid data
```

## Troubleshooting

### Low Confidence (<80%)
**Causes:**
- Balance sheet doesn't balance
- Missing data
- Extraction errors

**Solution:**
1. Check validation_report.json
2. Review specific warnings
3. Verify with source document
4. Manual adjustment if needed

### Missing Metrics
**Causes:**
- Not disclosed in report
- Different terminology
- In footnotes/appendices

**Solution:**
1. Check investment_metrics.json
2. Review original document
3. Look in management commentary

### Extraction Failures
**Causes:**
- Poor PDF quality
- Scanned images
- Non-standard format

**Solution:**
1. Try converting to text first
2. Use higher quality PDF
3. Check extraction_log.json

## Cost & Performance

### API Usage
- **Perplexity AI:** ~$0.01-0.05 per full report
- **4 API calls:** One per statement type
- **Free tier available:** Check Perplexity website

### Processing Time
- **Statement extraction:** ~1 minute
- **Metrics extraction:** <1 second
- **Validation:** <1 second
- **Report generation:** <1 second
- **Total:** ~1-2 minutes per company

## Best Practices

### ✅ DO
- Always check confidence score first
- Review validation warnings
- Compare with published summaries
- Use multiple years for trends
- Cross-reference with stock exchange data
- Read management commentary
- Consider industry context

### ❌ DON'T
- Rely solely on extracted data
- Ignore low confidence scores (<80%)
- Skip validation report
- Use as only investment criterion
- Ignore critical issues
- Compare different sectors directly
- Make decisions without due diligence

## Support Files

- **INVESTMENT_ANALYSIS_GUIDE.md** → Complete guide
- **EXTRACTION_MAP.md** → Visual reference
- **ANSWER_TO_YOUR_QUESTION.md** → Feature explanation
- **README.md** → Setup & installation

## Quick Reference

### Installation
```powershell
pip install -r requirements_sample.txt
```

### Setup
```powershell
# Create .env file
echo PERPLEXITY_API_KEY=your_key_here > .env
```

### Run
```powershell
python scripts\process_single.py <file> --company "<name>" --report
```

### Check Results
```powershell
# Open output directory
cd data\processed\<CompanyName>

# View metrics
type investment_metrics.json

# View quality
type validation_report.json

# Read report
type <CompanyName>_Investment_Analysis.md
```

---

**Need Help?**
1. Check validation_report.json for errors
2. Review extraction_log.json for details
3. Read INVESTMENT_ANALYSIS_GUIDE.md
4. Check example outputs in data/processed/

**Happy Investing! 📈**
