"""
Main script to process financial statement documents
"""
import sys
import logging
from pathlib import Path
import pandas as pd
from datetime import datetime
import json

# Add src to path (../src relative to this scripts/ folder)
SRC_DIR = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC_DIR))

from statement_detector import StatementDetector
from table_extractor import AdvancedTableExtractor
from investment_analyzer import InvestmentMetricsExtractor, calculate_derived_metrics
from data_validator import DataValidator
from report_generator import InvestmentReportGenerator
import config

# Setup logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class FinancialStatementProcessor:
    """Main processor for extracting financial statements"""

    def __init__(self):
        self.detector = StatementDetector(config.STATEMENT_KEYWORDS)
        self.extractor = AdvancedTableExtractor(use_llm_fallback=True)
        self.investment_analyzer = InvestmentMetricsExtractor()
        self.validator = DataValidator()
        self.report_generator = None  # Initialized per company
        self.results = {}

    def process_file(self, file_path: Path, company_name: str = None, generate_report: bool = False):
        """
        Process a single financial document

        Args:
            file_path: Path to the document file
            company_name: Company name (optional, will use filename if not provided)
        """
        logger.info(f"Processing file: {file_path}")

        # Extract company name from filename if not provided
        if company_name is None:
            company_name = file_path.stem

        # Read file (supports .txt and .pdf)
        try:
            text = self._read_text(file_path)
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            return False

        # Create output directory
        output_dir = config.PROCESSED_DIR / company_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize report generator
        self.report_generator = InvestmentReportGenerator(output_dir)

        # Process each statement type
        results = {
            'company': company_name,
            'source_file': str(file_path),
            'processed_at': datetime.now().isoformat(),
            'statements': {}
        }
        
        # Store DataFrames for cross-validation and metric calculation
        extracted_statements = {}

        for stmt_type in config.STATEMENT_KEYWORDS.keys():
            logger.info(f"\nExtracting {stmt_type}...")

            # Extract statement section
            section = self.detector.extract_statement_section(text, stmt_type)

            if section is None:
                logger.warning(f"Could not find {stmt_type}")
                results['statements'][stmt_type] = {'status': 'not_found'}
                continue

            # Extract table with LLM fallback
            df = self.extractor.extract_table(
                section,
                statement_type=stmt_type,
                company_name=company_name
            )

            if df is None or df.empty:
                logger.warning(f"Could not extract table for {stmt_type}")
                results['statements'][stmt_type] = {
                    'status': 'extraction_failed',
                    'section_length': len(section)
                }
                continue

            # Store for validation
            extracted_statements[stmt_type] = df

            # Save to CSV
            csv_filename = f"{stmt_type}.csv"
            csv_path = output_dir / csv_filename

            try:
                df.to_csv(csv_path, **config.CSV_SETTINGS)
                logger.info(f"Saved {stmt_type} to {csv_path}")
                logger.info(f"Extracted {len(df)} rows, {len(df.columns)} columns")

                results['statements'][stmt_type] = {
                    'status': 'success',
                    'output_file': str(csv_path),
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist()
                }
            except Exception as e:
                logger.error(f"Failed to save CSV: {e}")
                results['statements'][stmt_type] = {
                    'status': 'save_failed',
                    'error': str(e)
                }

        # ========== NEW: Extract Investment Metrics ==========
        logger.info("\n" + "="*80)
        logger.info("EXTRACTING INVESTMENT METRICS")
        logger.info("="*80)
        
        try:
            investment_metrics = self.investment_analyzer.extract_all_metrics(text, company_name)
            
            # Calculate derived metrics from statements
            derived_metrics = calculate_derived_metrics(extracted_statements, investment_metrics)
            investment_metrics['metrics']['calculated'] = derived_metrics
            
            # Save investment metrics
            metrics_path = output_dir / 'investment_metrics.json'
            with open(metrics_path, 'w') as f:
                # Convert numpy types to native Python types for JSON serialization
                json.dump(investment_metrics, f, indent=2, default=str)
            
            logger.info(f"Saved investment metrics to {metrics_path}")
            results['investment_metrics'] = {
                'status': 'success',
                'output_file': str(metrics_path)
            }
            
            # Print key metrics
            self._print_key_metrics(investment_metrics)
            
        except Exception as e:
            logger.error(f"Failed to extract investment metrics: {e}")
            results['investment_metrics'] = {
                'status': 'failed',
                'error': str(e)
            }

        # ========== NEW: Validate Data ==========
        logger.info("\n" + "="*80)
        logger.info("VALIDATING EXTRACTED DATA")
        logger.info("="*80)
        
        try:
            validation_report = self.validator.validate_all(
                extracted_statements,
                investment_metrics.get('metrics', {})
            )
            
            # Save validation report
            validation_path = output_dir / 'validation_report.json'
            with open(validation_path, 'w') as f:
                # Convert numpy types to native Python types for JSON serialization
                json.dump(validation_report, f, indent=2, default=str)
            
            logger.info(f"Saved validation report to {validation_path}")
            results['validation'] = {
                'status': 'success',
                'output_file': str(validation_path),
                'confidence_score': validation_report['overall_confidence'],
                'issues_count': len(validation_report['issues']),
                'warnings_count': len(validation_report['warnings'])
            }
            
            # Print validation summary
            self._print_validation_summary(validation_report)
            
        except Exception as e:
            logger.error(f"Failed to validate data: {e}")
            results['validation'] = {
                'status': 'failed',
                'error': str(e)
            }

        # Save processing log
        log_path = output_dir / 'extraction_log.json'
        with open(log_path, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"\nProcessing complete. Log saved to {log_path}")

        # ========== NEW: Generate Investment Report ==========
        if generate_report:
            logger.info("\n" + "="*80)
            logger.info("GENERATING INVESTMENT ANALYSIS REPORT")
            logger.info("="*80)
            
            try:
                report_path = self.report_generator.generate_markdown_report(
                    company_name,
                    extracted_statements,
                    investment_metrics,
                    validation_report
                )
                logger.info(f"Generated investment report: {report_path}")
                results['investment_report'] = {
                    'status': 'success',
                    'output_file': str(report_path)
                }
                print(f"\n📄 Investment Report: {report_path}")
            except Exception as e:
                logger.error(f"Failed to generate report: {e}")
                results['investment_report'] = {
                    'status': 'failed',
                    'error': str(e)
                }

        # Print summary
        self._print_summary(results)

        return True

    def _read_text(self, file_path: Path) -> str:
        """Read text content from a .txt or .pdf file.

        For PDFs, uses pdfplumber to extract text page by page.
        """
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            try:
                import pdfplumber
            except ImportError as e:
                raise RuntimeError(
                    "pdfplumber is required to read PDF files. Install it via pip: pip install pdfplumber"
                ) from e

            pages_text = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text() or ""
                    pages_text.append(t)
            return "\n\n".join(pages_text)

        # Default: treat as plain text
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _print_summary(self, results: dict):
        """Print processing summary"""
        print("\n" + "="*80)
        print("EXTRACTION SUMMARY")
        print("="*80)
        print(f"Company: {results['company']}")
        print(f"Processed: {results['processed_at']}")
        print("\nStatements:")

        for stmt_type, info in results['statements'].items():
            status = info.get('status', 'unknown')
            print(f"  {stmt_type:25s}: {status:20s}", end="")

            if status == 'success':
                print(f"  ({info['rows']} rows, {info['columns']} cols)")
            else:
                print()
        
        # Investment metrics summary
        if 'investment_metrics' in results:
            status = results['investment_metrics'].get('status', 'unknown')
            print(f"\nInvestment Metrics: {status}")
        
        # Validation summary
        if 'validation' in results:
            val = results['validation']
            if val.get('status') == 'success':
                confidence = val.get('confidence_score', 0)
                issues = val.get('issues_count', 0)
                warnings = val.get('warnings_count', 0)
                
                print(f"\nData Quality:")
                print(f"  Confidence Score: {confidence:.1f}%")
                print(f"  Issues: {issues}")
                print(f"  Warnings: {warnings}")
                
                # Quality indicator
                if confidence >= 90 and issues == 0:
                    print("  Status: ✅ EXCELLENT - Ready for investment analysis")
                elif confidence >= 80:
                    print("  Status: ✅ GOOD - Minor review recommended")
                elif confidence >= 70:
                    print("  Status: ⚠️ FAIR - Manual review recommended")
                else:
                    print("  Status: ⚠️ POOR - Significant review required")

        print("="*80)
    
    def _print_key_metrics(self, metrics: dict):
        """Print key investment metrics"""
        print("\n" + "-"*80)
        print("KEY INVESTMENT METRICS")
        print("-"*80)
        
        m = metrics.get('metrics', {})
        
        # Share Information
        if 'share_info' in m and m['share_info']:
            print("\n📊 Share Information:")
            si = m['share_info']
            if si.get('outstanding_shares'):
                print(f"  Outstanding Shares: {si['outstanding_shares']:,.0f}")
            if si.get('market_capitalization'):
                mc = si['market_capitalization']
                print(f"  Market Cap: Rs. {mc.get('value', 0):,.0f} {mc.get('unit', '')}")
            if si.get('share_price_range'):
                spr = si['share_price_range']
                print(f"  Share Price Range: Rs. {spr.get('low', 0):.2f} - Rs. {spr.get('high', 0):.2f}")
        
        # EPS
        if 'eps' in m and m['eps']:
            print("\n💰 Earnings Per Share:")
            eps = m['eps']
            if 'basic_eps' in eps:
                print(f"  Basic EPS: Rs. {eps['basic_eps']:.2f}")
            if 'diluted_eps' in eps:
                print(f"  Diluted EPS: Rs. {eps['diluted_eps']:.2f}")
        
        # Dividends
        if 'dividends' in m and m['dividends']:
            print("\n💸 Dividends:")
            div = m['dividends']
            if div.get('total_dividend_per_share'):
                print(f"  Total DPS: Rs. {div['total_dividend_per_share']:.2f}")
            if div.get('dividend_payout_ratio'):
                print(f"  Payout Ratio: {div['dividend_payout_ratio']:.1f}%")
            if div.get('dividend_yield'):
                print(f"  Dividend Yield: {div['dividend_yield']:.2f}%")
        
        # NAV
        if 'nav_per_share' in m and m['nav_per_share']:
            nav = m['nav_per_share']
            if 'value' in nav:
                print(f"\n📈 Net Asset Value per Share: Rs. {nav['value']:.2f}")
        
        # Financial Ratios
        if 'financial_ratios' in m and m['financial_ratios']:
            print("\n📊 Financial Ratios:")
            ratios = m['financial_ratios']
            if 'roe' in ratios:
                print(f"  ROE: {ratios['roe']:.2f}%")
            if 'roa' in ratios:
                print(f"  ROA: {ratios['roa']:.2f}%")
            if 'net_profit_margin' in ratios:
                print(f"  Net Profit Margin: {ratios['net_profit_margin']:.2f}%")
            if 'current_ratio' in ratios:
                print(f"  Current Ratio: {ratios['current_ratio']:.2f}")
            if 'debt_to_equity' in ratios:
                print(f"  Debt to Equity: {ratios['debt_to_equity']:.2f}")
        
        # Calculated Metrics
        if 'calculated' in m and m['calculated']:
            print("\n🔢 Calculated Metrics:")
            calc = m['calculated']
            if 'revenue_growth_pct' in calc:
                growth = calc['revenue_growth_pct']
                arrow = "📈" if growth > 0 else "📉"
                print(f"  Revenue Growth: {arrow} {growth:.2f}%")
            if 'net_profit_margin_pct' in calc:
                print(f"  Net Profit Margin: {calc['net_profit_margin_pct']:.2f}%")
            if 'current_ratio' in calc:
                print(f"  Current Ratio: {calc['current_ratio']:.2f}")
            if 'debt_to_equity' in calc:
                print(f"  Debt to Equity: {calc['debt_to_equity']:.2f}")
        
        # Capital Adequacy (for banks)
        if 'capital_adequacy' in m and m['capital_adequacy']:
            print("\n🏦 Capital Adequacy (Banking):")
            cap = m['capital_adequacy']
            if 'tier1_ratio' in cap:
                print(f"  Tier 1 Ratio: {cap['tier1_ratio']:.2f}%")
            if 'total_car' in cap:
                print(f"  Total CAR: {cap['total_car']:.2f}%")
        
        # Market Info
        if 'market_info' in m and m['market_info']:
            mi = m['market_info']
            if mi.get('pe_ratio'):
                print(f"\n📉 P/E Ratio: {mi['pe_ratio']:.2f}")
            if mi.get('pb_ratio'):
                print(f"📉 P/B Ratio: {mi['pb_ratio']:.2f}")
            if mi.get('stock_exchange'):
                print(f"📍 Listed on: {', '.join(mi['stock_exchange'])}")
        
        print("-"*80)
    
    def _print_validation_summary(self, validation: dict):
        """Print validation summary"""
        print("\n" + "-"*80)
        print("DATA VALIDATION REPORT")
        print("-"*80)
        
        print(f"\n🎯 Overall Confidence: {validation['overall_confidence']:.1f}%")
        
        # Issues
        if validation['issues']:
            print(f"\n🔴 Critical Issues ({len(validation['issues'])}):")
            for issue in validation['issues'][:5]:  # Show first 5
                print(f"  • {issue}")
            if len(validation['issues']) > 5:
                print(f"  ... and {len(validation['issues']) - 5} more")
        
        # Warnings
        if validation['warnings']:
            print(f"\n⚠️ Warnings ({len(validation['warnings'])}):")
            for warning in validation['warnings'][:5]:  # Show first 5
                print(f"  • {warning}")
            if len(validation['warnings']) > 5:
                print(f"  ... and {len(validation['warnings']) - 5} more")
        
        # Statement-specific validations
        print("\n📋 Statement Validations:")
        for stmt_type, val in validation['statement_validations'].items():
            confidence = val.get('confidence_score', 0)
            status = "✅" if val.get('valid', False) else "❌"
            print(f"  {status} {stmt_type:25s}: {confidence:.1f}% confidence")
        
        # Recommendations
        if validation.get('recommendations'):
            print("\n💡 Recommendations:")
            for rec in validation['recommendations']:
                print(f"  {rec}")
        
        print("-"*80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract financial statements from annual reports'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Path to input file (PDF or TXT)'
    )
    parser.add_argument(
        '--company',
        type=str,
        help='Company name (optional)',
        default=None
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate comprehensive investment analysis report (markdown)'
    )

    args = parser.parse_args()

    # Convert to Path object
    input_path = Path(args.input_file)

    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    # Process file
    processor = FinancialStatementProcessor()
    success = processor.process_file(input_path, args.company, args.report)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
