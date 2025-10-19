"""
Investment Analysis Report Generator
Creates comprehensive PDF/HTML reports for investment decision-making
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import pandas as pd


class InvestmentReportGenerator:
    """Generates comprehensive investment analysis reports"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        
    def generate_markdown_report(self, 
                                 company_name: str,
                                 statements: Dict[str, pd.DataFrame],
                                 metrics: Dict[str, Any],
                                 validation: Dict[str, Any]) -> Path:
        """
        Generate a comprehensive markdown investment report
        
        Args:
            company_name: Company name
            statements: Extracted financial statements
            metrics: Investment metrics
            validation: Validation report
            
        Returns:
            Path to generated report
        """
        report_path = self.output_dir / f"{company_name}_Investment_Analysis.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# Investment Analysis Report\n\n")
            f.write(f"## {company_name}\n\n")
            f.write(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"---\n\n")
            
            # Executive Summary
            f.write("## 📊 Executive Summary\n\n")
            self._write_executive_summary(f, metrics, validation)
            
            # Data Quality
            f.write("\n## 🎯 Data Quality Assessment\n\n")
            self._write_quality_assessment(f, validation)
            
            # Key Investment Metrics
            f.write("\n## 💰 Key Investment Metrics\n\n")
            self._write_investment_metrics(f, metrics)
            
            # Financial Performance
            f.write("\n## 📈 Financial Performance Analysis\n\n")
            self._write_performance_analysis(f, statements, metrics)
            
            # Valuation Metrics
            f.write("\n## 💎 Valuation Analysis\n\n")
            self._write_valuation_analysis(f, metrics)
            
            # Risk Assessment
            f.write("\n## ⚠️ Risk Assessment\n\n")
            self._write_risk_assessment(f, metrics, validation)
            
            # Financial Health
            f.write("\n## 🏥 Financial Health Indicators\n\n")
            self._write_financial_health(f, statements, metrics)
            
            # Growth Analysis
            f.write("\n## 🚀 Growth Analysis\n\n")
            self._write_growth_analysis(f, statements, metrics)
            
            # Investment Recommendation
            f.write("\n## 🎯 Investment Considerations\n\n")
            self._write_investment_considerations(f, metrics, validation)
            
            # Detailed Statements
            f.write("\n## 📋 Detailed Financial Statements\n\n")
            self._write_detailed_statements(f, statements)
            
            # Appendix
            f.write("\n## 📎 Appendix\n\n")
            self._write_appendix(f, metrics, validation)
            
            # Disclaimer
            f.write("\n---\n\n")
            f.write("**Disclaimer:** This report is generated automatically and should not be the sole "
                   "basis for investment decisions. Always conduct thorough due diligence and consult "
                   "with financial advisors.\n")
        
        return report_path
    
    def _write_executive_summary(self, f, metrics: Dict, validation: Dict):
        """Write executive summary section"""
        m = metrics.get('metrics', {})
        
        # Quick facts
        f.write("### Quick Facts\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        
        # EPS
        if 'eps' in m and m['eps'].get('basic_eps'):
            f.write(f"| **Basic EPS** | Rs. {m['eps']['basic_eps']:.2f} |\n")
        
        # NAV
        if 'nav_per_share' in m and m['nav_per_share'].get('value'):
            f.write(f"| **NAV per Share** | Rs. {m['nav_per_share']['value']:.2f} |\n")
        
        # Dividend
        if 'dividends' in m and m['dividends'].get('total_dividend_per_share'):
            f.write(f"| **Total Dividend per Share** | Rs. {m['dividends']['total_dividend_per_share']:.2f} |\n")
        
        # P/E Ratio
        if 'market_info' in m and m['market_info'].get('pe_ratio'):
            f.write(f"| **P/E Ratio** | {m['market_info']['pe_ratio']:.2f} |\n")
        
        # Data Quality
        confidence = validation.get('overall_confidence', 0)
        f.write(f"| **Data Confidence** | {confidence:.1f}% |\n\n")
    
    def _write_quality_assessment(self, f, validation: Dict):
        """Write data quality assessment"""
        confidence = validation.get('overall_confidence', 0)
        
        # Quality badge
        if confidence >= 90:
            badge = "🟢 EXCELLENT"
        elif confidence >= 80:
            badge = "🟡 GOOD"
        elif confidence >= 70:
            badge = "🟠 FAIR"
        else:
            badge = "🔴 POOR"
        
        f.write(f"**Overall Data Quality:** {badge} ({confidence:.1f}%)\n\n")
        
        # Issues and warnings
        issues = validation.get('issues', [])
        warnings = validation.get('warnings', [])
        
        if issues:
            f.write(f"**⚠️ Critical Issues:** {len(issues)}\n\n")
            for issue in issues:
                f.write(f"- {issue}\n")
            f.write("\n")
        
        if warnings:
            f.write(f"**⚠️ Warnings:** {len(warnings)}\n\n")
            for warning in warnings[:10]:  # Top 10
                f.write(f"- {warning}\n")
            if len(warnings) > 10:
                f.write(f"- ... and {len(warnings) - 10} more warnings\n")
            f.write("\n")
        
        # Recommendations
        if validation.get('recommendations'):
            f.write("**Recommendations:**\n\n")
            for rec in validation['recommendations']:
                f.write(f"- {rec}\n")
            f.write("\n")
    
    def _write_investment_metrics(self, f, metrics: Dict):
        """Write key investment metrics"""
        m = metrics.get('metrics', {})
        
        # Earnings
        if 'eps' in m and m['eps']:
            f.write("### 📈 Earnings\n\n")
            eps = m['eps']
            if 'basic_eps' in eps:
                f.write(f"- **Basic EPS:** Rs. {eps['basic_eps']:.2f}\n")
            if 'diluted_eps' in eps:
                f.write(f"- **Diluted EPS:** Rs. {eps['diluted_eps']:.2f}\n")
            f.write("\n")
        
        # Dividends
        if 'dividends' in m and m['dividends']:
            f.write("### 💸 Dividend Information\n\n")
            div = m['dividends']
            if div.get('total_dividend_per_share'):
                f.write(f"- **Total DPS:** Rs. {div['total_dividend_per_share']:.2f}\n")
            if div.get('dividend_payout_ratio'):
                f.write(f"- **Payout Ratio:** {div['dividend_payout_ratio']:.1f}%\n")
            if div.get('dividend_yield'):
                f.write(f"- **Dividend Yield:** {div['dividend_yield']:.2f}%\n")
            f.write("\n")
        
        # Book Value
        if 'nav_per_share' in m and m['nav_per_share'].get('value'):
            f.write("### 📚 Book Value\n\n")
            f.write(f"- **NAV per Share:** Rs. {m['nav_per_share']['value']:.2f}\n\n")
    
    def _write_performance_analysis(self, f, statements: Dict, metrics: Dict):
        """Write financial performance analysis"""
        m = metrics.get('metrics', {})
        
        # Profitability
        f.write("### 💹 Profitability Ratios\n\n")
        f.write("| Ratio | Value | Interpretation |\n")
        f.write("|-------|-------|----------------|\n")
        
        ratios = m.get('financial_ratios', {})
        calc = m.get('calculated', {})
        
        if ratios.get('roe') or calc.get('roe'):
            roe = ratios.get('roe') or calc.get('roe')
            interp = "Excellent" if roe > 15 else "Good" if roe > 10 else "Average" if roe > 5 else "Poor"
            f.write(f"| Return on Equity (ROE) | {roe:.2f}% | {interp} |\n")
        
        if ratios.get('roa') or calc.get('roa'):
            roa = ratios.get('roa') or calc.get('roa')
            interp = "Excellent" if roa > 5 else "Good" if roa > 2 else "Average" if roa > 1 else "Poor"
            f.write(f"| Return on Assets (ROA) | {roa:.2f}% | {interp} |\n")
        
        if ratios.get('net_profit_margin') or calc.get('net_profit_margin_pct'):
            npm = ratios.get('net_profit_margin') or calc.get('net_profit_margin_pct')
            interp = "Excellent" if npm > 20 else "Good" if npm > 10 else "Average" if npm > 5 else "Concerning"
            f.write(f"| Net Profit Margin | {npm:.2f}% | {interp} |\n")
        
        f.write("\n")
        
        # Revenue Growth
        if calc.get('revenue_growth_pct'):
            f.write("### 📊 Revenue Growth\n\n")
            growth = calc['revenue_growth_pct']
            trend = "📈 Growing" if growth > 0 else "📉 Declining"
            f.write(f"**Year-over-Year Growth:** {trend} {abs(growth):.2f}%\n\n")
            
            if growth > 20:
                f.write("*Strong growth momentum*\n\n")
            elif growth > 10:
                f.write("*Healthy growth*\n\n")
            elif growth > 0:
                f.write("*Moderate growth*\n\n")
            else:
                f.write("*⚠️ Declining revenue - investigate causes*\n\n")
    
    def _write_valuation_analysis(self, f, metrics: Dict):
        """Write valuation analysis"""
        m = metrics.get('metrics', {})
        
        market = m.get('market_info', {})
        
        pe = market.get('pe_ratio')
        if pe is not None and pe > 0:
            f.write(f"**Price-to-Earnings (P/E) Ratio:** {pe:.2f}\n\n")
            
            if pe < 10:
                f.write("- *Potentially undervalued* (P/E < 10)\n")
            elif pe < 20:
                f.write("- *Fair valuation* (P/E 10-20)\n")
            elif pe < 30:
                f.write("- *Slightly expensive* (P/E 20-30)\n")
            else:
                f.write("- *⚠️ Potentially overvalued* (P/E > 30)\n")
            f.write("\n")
        
        pb = market.get('pb_ratio')
        if pb is not None and pb > 0:
            f.write(f"**Price-to-Book (P/B) Ratio:** {pb:.2f}\n\n")
            
            if pb < 1:
                f.write("- *Trading below book value* (P/B < 1)\n")
            elif pb < 3:
                f.write("- *Reasonable valuation* (P/B 1-3)\n")
            else:
                f.write("- *Premium valuation* (P/B > 3)\n")
            f.write("\n")
    
    def _write_risk_assessment(self, f, metrics: Dict, validation: Dict):
        """Write risk assessment"""
        m = metrics.get('metrics', {})
        
        # Data quality risk
        confidence = validation.get('overall_confidence', 0)
        if confidence < 80:
            f.write("⚠️ **Data Quality Risk:** Low confidence in extracted data. Manual verification recommended.\n\n")
        
        # Financial risks
        ratios = m.get('financial_ratios', {})
        calc = m.get('calculated', {})
        
        risks = []
        
        # Leverage risk
        de = ratios.get('debt_to_equity') or calc.get('debt_to_equity')
        if de and de > 2:
            risks.append(f"**High Leverage:** Debt-to-Equity ratio of {de:.2f} indicates significant financial leverage")
        
        # Liquidity risk
        cr = ratios.get('current_ratio') or calc.get('current_ratio')
        if cr and cr < 1:
            risks.append(f"**Liquidity Concern:** Current ratio of {cr:.2f} suggests potential short-term liquidity issues")
        
        # Profitability risk
        if calc.get('revenue_growth_pct', 0) < 0:
            risks.append(f"**Declining Revenue:** Negative revenue growth of {calc['revenue_growth_pct']:.2f}%")
        
        # Extract reported risks
        if 'risk_factors' in m and m['risk_factors']:
            f.write("### Disclosed Risk Factors\n\n")
            for i, risk in enumerate(m['risk_factors'][:5], 1):
                f.write(f"{i}. {risk}\n")
            f.write("\n")
        
        if risks:
            f.write("### Identified Risks\n\n")
            for risk in risks:
                f.write(f"- ⚠️ {risk}\n")
            f.write("\n")
        else:
            f.write("✅ No major financial risks identified from available data.\n\n")
    
    def _write_financial_health(self, f, statements: Dict, metrics: Dict):
        """Write financial health indicators"""
        m = metrics.get('metrics', {})
        ratios = m.get('financial_ratios', {})
        calc = m.get('calculated', {})
        
        # Liquidity
        f.write("### 💧 Liquidity\n\n")
        cr = ratios.get('current_ratio') or calc.get('current_ratio')
        if cr:
            status = "✅ Healthy" if cr > 1.5 else "⚠️ Adequate" if cr > 1 else "🔴 Concerning"
            f.write(f"**Current Ratio:** {cr:.2f} - {status}\n\n")
        
        # Leverage
        f.write("### ⚖️ Leverage\n\n")
        de = ratios.get('debt_to_equity') or calc.get('debt_to_equity')
        if de:
            status = "✅ Conservative" if de < 1 else "⚠️ Moderate" if de < 2 else "🔴 High"
            f.write(f"**Debt-to-Equity:** {de:.2f} - {status}\n\n")
        
        # Capital Adequacy (for banks)
        if 'capital_adequacy' in m and m['capital_adequacy']:
            f.write("### 🏦 Capital Adequacy (Banking)\n\n")
            cap = m['capital_adequacy']
            if 'total_car' in cap:
                car = cap['total_car']
                status = "✅ Strong" if car > 15 else "⚠️ Adequate" if car > 10 else "🔴 Weak"
                f.write(f"**Total CAR:** {car:.2f}% - {status}\n\n")
    
    def _write_growth_analysis(self, f, statements: Dict, metrics: Dict):
        """Write growth analysis"""
        m = metrics.get('metrics', {})
        calc = m.get('calculated', {})
        
        if calc.get('revenue_growth_pct'):
            growth = calc['revenue_growth_pct']
            f.write(f"**Revenue Growth:** {growth:+.2f}%\n\n")
            
            if abs(growth) > 20:
                f.write("*Significant change - investigate drivers*\n\n")
        
        # Future outlook
        if 'outlook' in m and m['outlook'].get('section_found'):
            f.write("### 🔮 Management Outlook\n\n")
            summary = m['outlook'].get('summary', 'Not available')
            f.write(f"{summary}\n\n")
    
    def _write_investment_considerations(self, f, metrics: Dict, validation: Dict):
        """Write investment considerations"""
        m = metrics.get('metrics', {})
        
        f.write("### Strengths\n\n")
        strengths = self._identify_strengths(m)
        for strength in strengths:
            f.write(f"- ✅ {strength}\n")
        
        f.write("\n### Concerns\n\n")
        concerns = self._identify_concerns(m, validation)
        for concern in concerns:
            f.write(f"- ⚠️ {concern}\n")
        
        f.write("\n### Key Considerations\n\n")
        f.write("- Verify all extracted data with original documents\n")
        f.write("- Compare metrics with industry peers\n")
        f.write("- Review management commentary and future outlook\n")
        f.write("- Consider macroeconomic factors\n")
        f.write("- Assess company's competitive position\n\n")
    
    def _identify_strengths(self, metrics: Dict) -> list:
        """Identify company strengths"""
        strengths = []
        
        ratios = metrics.get('financial_ratios', {})
        calc = metrics.get('calculated', {})
        
        if ratios.get('roe', 0) > 15 or calc.get('roe', 0) > 15:
            strengths.append("Strong Return on Equity (>15%)")
        
        if calc.get('revenue_growth_pct', 0) > 10:
            strengths.append(f"Strong revenue growth ({calc['revenue_growth_pct']:.1f}%)")
        
        if calc.get('current_ratio', 0) > 2:
            strengths.append("Strong liquidity position")
        
        de = ratios.get('debt_to_equity') or calc.get('debt_to_equity', 0)
        if de < 0.5:
            strengths.append("Conservative debt levels")
        
        div = metrics.get('dividends', {})
        if div.get('dividend_yield', 0) > 3:
            strengths.append(f"Attractive dividend yield ({div['dividend_yield']:.2f}%)")
        
        return strengths or ["Review financial statements for strengths"]
    
    def _identify_concerns(self, metrics: Dict, validation: Dict) -> list:
        """Identify concerns"""
        concerns = []
        
        ratios = metrics.get('financial_ratios', {})
        calc = metrics.get('calculated', {})
        
        if validation.get('overall_confidence', 100) < 80:
            concerns.append("Data quality concerns - manual verification needed")
        
        if calc.get('revenue_growth_pct', 0) < 0:
            concerns.append("Declining revenue")
        
        if calc.get('current_ratio', 999) < 1:
            concerns.append("Potential liquidity issues")
        
        de = ratios.get('debt_to_equity') or calc.get('debt_to_equity', 0)
        if de > 2:
            concerns.append(f"High debt-to-equity ratio ({de:.2f})")
        
        return concerns or ["No major concerns identified"]
    
    def _write_detailed_statements(self, f, statements: Dict):
        """Write detailed financial statements"""
        for stmt_type, df in statements.items():
            if df is None or df.empty:
                continue
            
            f.write(f"### {stmt_type.replace('_', ' ').title()}\n\n")
            f.write(df.to_markdown(index=False))
            f.write("\n\n")
    
    def _write_appendix(self, f, metrics: Dict, validation: Dict):
        """Write appendix with additional information"""
        f.write("### Extraction Metadata\n\n")
        f.write(f"- **Extraction Date:** {metrics.get('extraction_date', 'N/A')}\n")
        f.write(f"- **Data Confidence:** {validation.get('overall_confidence', 0):.1f}%\n")
        f.write(f"- **Issues Found:** {len(validation.get('issues', []))}\n")
        f.write(f"- **Warnings:** {len(validation.get('warnings', []))}\n\n")
        
        f.write("### Statement Quality\n\n")
        for stmt_type, val in validation.get('statement_validations', {}).items():
            conf = val.get('confidence_score', 0)
            f.write(f"- **{stmt_type}:** {conf:.1f}% confidence\n")
        f.write("\n")
