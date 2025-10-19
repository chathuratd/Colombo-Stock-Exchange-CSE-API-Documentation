"""
Data Validation Module - Ensures accuracy of extracted financial data
"""
import logging
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates extracted financial statement data for accuracy and consistency"""
    
    def __init__(self):
        self.validation_results = []
        
    def validate_all(self, statements: Dict[str, pd.DataFrame], 
                    metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive validation of all extracted data
        
        Args:
            statements: Dictionary of statement type -> DataFrame
            metrics: Extracted investment metrics
            
        Returns:
            Validation report with issues and confidence scores
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_confidence': 0.0,
            'issues': [],
            'warnings': [],
            'statement_validations': {},
            'metrics_validation': {}
        }
        
        # Validate each statement
        for stmt_type, df in statements.items():
            stmt_validation = self._validate_statement(df, stmt_type)
            report['statement_validations'][stmt_type] = stmt_validation
            
            # Collect issues
            report['issues'].extend(stmt_validation.get('errors', []))
            report['warnings'].extend(stmt_validation.get('warnings', []))
        
        # Cross-validation between statements
        cross_val = self._cross_validate_statements(statements)
        report['cross_validation'] = cross_val
        report['issues'].extend(cross_val.get('errors', []))
        report['warnings'].extend(cross_val.get('warnings', []))
        
        # Validate investment metrics
        metrics_val = self._validate_metrics(metrics, statements)
        report['metrics_validation'] = metrics_val
        report['warnings'].extend(metrics_val.get('warnings', []))
        
        # Calculate overall confidence score
        report['overall_confidence'] = self._calculate_confidence(report)
        
        # Add recommendations
        report['recommendations'] = self._generate_recommendations(report)
        
        logger.info(f"Validation complete. Confidence: {report['overall_confidence']:.1f}%")
        logger.info(f"Issues: {len(report['issues'])}, Warnings: {len(report['warnings'])}")
        
        return report
    
    def _validate_statement(self, df: pd.DataFrame, stmt_type: str) -> Dict:
        """Validate individual financial statement"""
        validation = {
            'valid': True,
            'confidence_score': 100.0,
            'errors': [],
            'warnings': [],
            'checks': {}
        }
        
        if df is None or df.empty:
            validation['valid'] = False
            validation['errors'].append(f"{stmt_type}: DataFrame is empty")
            validation['confidence_score'] = 0.0
            return validation
        
        # Check 1: Column structure
        col_check = self._check_column_structure(df, stmt_type)
        validation['checks']['column_structure'] = col_check
        if not col_check['passed']:
            validation['warnings'].extend(col_check['issues'])
            validation['confidence_score'] -= 10
        
        # Check 2: Year headers
        year_check = self._check_year_headers(df)
        validation['checks']['year_headers'] = year_check
        if not year_check['passed']:
            validation['warnings'].extend(year_check['issues'])
            validation['confidence_score'] -= 15
        
        # Check 3: Numeric data validity
        numeric_check = self._check_numeric_data(df)
        validation['checks']['numeric_data'] = numeric_check
        if not numeric_check['passed']:
            validation['errors'].extend(numeric_check['issues'])
            validation['confidence_score'] -= 20
        
        # Check 4: Balance sheet balancing
        if stmt_type == 'balance_sheet':
            balance_check = self._check_balance_sheet_balance(df)
            validation['checks']['balance'] = balance_check
            if not balance_check['passed']:
                validation['errors'].extend(balance_check['issues'])
                validation['confidence_score'] -= 30
        
        # Check 5: Statement-specific validations
        specific_check = self._check_statement_specific(df, stmt_type)
        validation['checks']['statement_specific'] = specific_check
        if not specific_check['passed']:
            validation['warnings'].extend(specific_check['issues'])
            validation['confidence_score'] -= 10
        
        # Check 6: Data completeness
        completeness = self._check_completeness(df)
        validation['checks']['completeness'] = completeness
        if completeness['score'] < 80:
            validation['warnings'].append(
                f"{stmt_type}: Data completeness {completeness['score']:.1f}% (threshold: 80%)"
            )
            validation['confidence_score'] -= (80 - completeness['score']) / 2
        
        validation['valid'] = len(validation['errors']) == 0
        validation['confidence_score'] = max(0, validation['confidence_score'])
        
        return validation
    
    def _check_column_structure(self, df: pd.DataFrame, stmt_type: str) -> Dict:
        """Check if DataFrame has expected column structure"""
        result = {'passed': True, 'issues': []}
        
        # Should have at least 2 columns (label + at least 1 year)
        if len(df.columns) < 2:
            result['passed'] = False
            result['issues'].append(
                f"{stmt_type}: Expected at least 2 columns, found {len(df.columns)}"
            )
        
        # First column should contain text labels
        if df.iloc[:, 0].dtype not in ['object', 'string']:
            result['passed'] = False
            result['issues'].append(
                f"{stmt_type}: First column should contain labels (found type: {df.iloc[:, 0].dtype})"
            )
        
        # Other columns should be numeric or convertible
        for col_idx in range(1, len(df.columns)):
            try:
                pd.to_numeric(df.iloc[:, col_idx], errors='coerce')
            except Exception as e:
                result['issues'].append(
                    f"{stmt_type}: Column {col_idx} may not be numeric: {str(e)}"
                )
        
        return result
    
    def _check_year_headers(self, df: pd.DataFrame) -> Dict:
        """Verify that column headers contain valid years"""
        result = {'passed': True, 'issues': [], 'years_found': []}
        
        current_year = datetime.now().year
        
        for col in df.columns[1:]:  # Skip first column (labels)
            col_str = str(col)
            
            # Look for 4-digit year
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', col_str)
            
            if year_match:
                year = int(year_match.group(0))
                result['years_found'].append(year)
                
                # Validate year is reasonable
                if year < 1950 or year > current_year + 1:
                    result['passed'] = False
                    result['issues'].append(
                        f"Column '{col}' contains invalid year: {year}"
                    )
            else:
                result['issues'].append(
                    f"Column '{col}' does not contain a clear year identifier"
                )
        
        # Check for year sequence
        if len(result['years_found']) >= 2:
            years_sorted = sorted(result['years_found'], reverse=True)
            if result['years_found'] != years_sorted:
                result['issues'].append(
                    f"Years may not be in descending order: {result['years_found']}"
                )
        
        return result
    
    def _check_numeric_data(self, df: pd.DataFrame) -> Dict:
        """Validate numeric data quality"""
        result = {'passed': True, 'issues': []}
        
        for col_idx in range(1, len(df.columns)):
            col_data = pd.to_numeric(df.iloc[:, col_idx], errors='coerce')
            
            # Check for excessive NaN values
            nan_pct = (col_data.isna().sum() / len(col_data)) * 100
            if nan_pct > 30:
                result['issues'].append(
                    f"Column {df.columns[col_idx]}: {nan_pct:.1f}% missing values"
                )
            
            # Check for unrealistic values (all zeros or all same value)
            non_zero = col_data[col_data != 0]
            if len(non_zero) == 0:
                result['issues'].append(
                    f"Column {df.columns[col_idx]}: All values are zero"
                )
            elif non_zero.nunique() == 1 and len(non_zero) > 3:
                result['issues'].append(
                    f"Column {df.columns[col_idx]}: All non-zero values are identical"
                )
        
        if result['issues']:
            result['passed'] = False
        
        return result
    
    def _check_balance_sheet_balance(self, df: pd.DataFrame) -> Dict:
        """Check if Assets = Liabilities + Equity"""
        result = {'passed': True, 'issues': [], 'balances': []}
        
        # Find total assets row
        assets_row = df[df.iloc[:, 0].str.contains(
            'total assets', case=False, na=False
        )]
        
        # Find total equity row
        equity_row = df[df.iloc[:, 0].str.contains(
            'total equity|shareholders.*equity|total.*equity.*shareholders',
            case=False, na=False, regex=True
        )]
        
        # Find total liabilities + equity (or liabilities and equity)
        liab_equity_row = df[df.iloc[:, 0].str.contains(
            'total.*liabilities.*equity|total.*equity.*liabilities',
            case=False, na=False, regex=True
        )]
        
        if assets_row.empty:
            result['issues'].append("Balance Sheet: 'Total Assets' row not found")
            result['passed'] = False
            return result
        
        if liab_equity_row.empty and equity_row.empty:
            result['issues'].append(
                "Balance Sheet: Neither 'Total Liabilities + Equity' nor 'Total Equity' found"
            )
            result['passed'] = False
            return result
        
        # Check balance for each year column
        for col_idx in range(1, len(df.columns)):
            try:
                assets_val = pd.to_numeric(assets_row.iloc[0, col_idx], errors='coerce')
                
                # Try to find matching liabilities + equity total
                if not liab_equity_row.empty:
                    liab_equity_val = pd.to_numeric(liab_equity_row.iloc[0, col_idx], errors='coerce')
                else:
                    # Try to calculate from separate rows
                    total_liab = df[df.iloc[:, 0].str.contains('total liabilities', case=False, na=False)]
                    if not total_liab.empty and not equity_row.empty:
                        liab_val = pd.to_numeric(total_liab.iloc[0, col_idx], errors='coerce')
                        equity_val = pd.to_numeric(equity_row.iloc[0, col_idx], errors='coerce')
                        liab_equity_val = liab_val + equity_val if liab_val and equity_val else None
                    else:
                        liab_equity_val = None
                
                if assets_val and liab_equity_val:
                    # Allow 1% tolerance for rounding
                    diff_pct = abs(assets_val - liab_equity_val) / assets_val * 100
                    
                    result['balances'].append({
                        'column': df.columns[col_idx],
                        'assets': assets_val,
                        'liabilities_equity': liab_equity_val,
                        'difference_pct': diff_pct,
                        'balanced': diff_pct < 1.0
                    })
                    
                    if diff_pct >= 1.0:
                        result['passed'] = False
                        result['issues'].append(
                            f"Balance Sheet ({df.columns[col_idx]}): Assets ({assets_val:,.0f}) != "
                            f"Liabilities+Equity ({liab_equity_val:,.0f}) - Diff: {diff_pct:.2f}%"
                        )
            
            except Exception as e:
                result['issues'].append(
                    f"Balance Sheet: Error checking balance for {df.columns[col_idx]}: {str(e)}"
                )
        
        return result
    
    def _check_statement_specific(self, df: pd.DataFrame, stmt_type: str) -> Dict:
        """Statement-specific validation rules"""
        result = {'passed': True, 'issues': []}
        
        if stmt_type == 'income_statement':
            # Should have revenue/income
            if not df.iloc[:, 0].str.contains('revenue|income', case=False, na=False).any():
                result['issues'].append("Income Statement: No 'Revenue' or 'Income' line found")
                result['passed'] = False
            
            # Should have profit/loss
            if not df.iloc[:, 0].str.contains('profit|loss', case=False, na=False).any():
                result['issues'].append("Income Statement: No 'Profit' or 'Loss' line found")
                result['passed'] = False
        
        elif stmt_type == 'balance_sheet':
            # Should have assets
            if not df.iloc[:, 0].str.contains('assets', case=False, na=False).any():
                result['issues'].append("Balance Sheet: No 'Assets' section found")
                result['passed'] = False
            
            # Should have liabilities or equity
            has_liab = df.iloc[:, 0].str.contains('liabilities', case=False, na=False).any()
            has_equity = df.iloc[:, 0].str.contains('equity', case=False, na=False).any()
            if not (has_liab or has_equity):
                result['issues'].append("Balance Sheet: No 'Liabilities' or 'Equity' found")
                result['passed'] = False
        
        elif stmt_type == 'cash_flow':
            # Should have operating activities
            if not df.iloc[:, 0].str.contains('operating', case=False, na=False).any():
                result['issues'].append("Cash Flow: No 'Operating Activities' section found")
                result['passed'] = False
        
        return result
    
    def _check_completeness(self, df: pd.DataFrame) -> Dict:
        """Check data completeness (percentage of non-null values)"""
        total_cells = df.size
        non_null_cells = df.count().sum()
        
        completeness_pct = (non_null_cells / total_cells) * 100 if total_cells > 0 else 0
        
        return {
            'score': completeness_pct,
            'total_cells': total_cells,
            'filled_cells': non_null_cells
        }
    
    def _cross_validate_statements(self, statements: Dict[str, pd.DataFrame]) -> Dict:
        """Cross-validate data between different statements"""
        result = {'passed': True, 'errors': [], 'warnings': []}
        
        # Check 1: Net profit should appear in both income statement and cash flow
        if 'income_statement' in statements and 'cash_flow' in statements:
            inc = statements['income_statement']
            cf = statements['cash_flow']
            
            if not inc.empty and not cf.empty and len(inc.columns) >= 2:
                # Find net profit in income statement
                profit_row_inc = inc[inc.iloc[:, 0].str.contains(
                    'net profit|profit for', case=False, na=False
                )]
                
                # Find net profit in cash flow (usually first line)
                profit_row_cf = cf[cf.iloc[:, 0].str.contains(
                    'net profit|profit for|profit before', case=False, na=False
                )]
                
                if not profit_row_inc.empty and not profit_row_cf.empty:
                    # Compare values (first numeric column)
                    profit_inc = pd.to_numeric(profit_row_inc.iloc[0, 1], errors='coerce')
                    profit_cf = pd.to_numeric(profit_row_cf.iloc[0, 1], errors='coerce')
                    
                    if profit_inc and profit_cf:
                        diff_pct = abs(profit_inc - profit_cf) / profit_inc * 100
                        if diff_pct > 5:  # 5% tolerance
                            result['warnings'].append(
                                f"Net profit mismatch: Income Statement ({profit_inc:,.0f}) vs "
                                f"Cash Flow ({profit_cf:,.0f}) - Diff: {diff_pct:.1f}%"
                            )
        
        # Check 2: Total equity should match between balance sheet and equity statement
        if 'balance_sheet' in statements and 'equity_statement' in statements:
            bal = statements['balance_sheet']
            eq = statements['equity_statement']
            
            if not bal.empty and not eq.empty and len(bal.columns) >= 2:
                equity_row_bal = bal[bal.iloc[:, 0].str.contains(
                    'total equity', case=False, na=False
                )]
                
                # In equity statement, look for closing balance
                equity_row_eq = eq[eq.iloc[:, 0].str.contains(
                    'balance.*end|closing balance|at.*end', case=False, na=False, regex=True
                )]
                
                if not equity_row_bal.empty and not equity_row_eq.empty:
                    equity_bal = pd.to_numeric(equity_row_bal.iloc[0, 1], errors='coerce')
                    equity_eq = pd.to_numeric(equity_row_eq.iloc[0, 1], errors='coerce')
                    
                    if equity_bal and equity_eq:
                        diff_pct = abs(equity_bal - equity_eq) / equity_bal * 100
                        if diff_pct > 2:  # 2% tolerance
                            result['warnings'].append(
                                f"Total equity mismatch: Balance Sheet ({equity_bal:,.0f}) vs "
                                f"Equity Statement ({equity_eq:,.0f}) - Diff: {diff_pct:.1f}%"
                            )
        
        return result
    
    def _validate_metrics(self, metrics: Dict[str, Any], 
                         statements: Dict[str, pd.DataFrame]) -> Dict:
        """Validate extracted investment metrics"""
        result = {'passed': True, 'warnings': []}
        
        # Check EPS calculation if we have net profit and shares
        if 'eps' in metrics and 'share_info' in metrics:
            eps_data = metrics.get('eps', {})
            share_data = metrics.get('share_info', {})
            
            if 'basic_eps' in eps_data and 'outstanding_shares' in share_data:
                if 'income_statement' in statements:
                    inc = statements['income_statement']
                    if not inc.empty and len(inc.columns) >= 2:
                        profit_row = inc[inc.iloc[:, 0].str.contains(
                            'profit.*shareholders|profit for.*year', case=False, na=False, regex=True
                        )]
                        
                        if not profit_row.empty:
                            profit = pd.to_numeric(profit_row.iloc[0, 1], errors='coerce')
                            shares = share_data['outstanding_shares']
                            eps_reported = eps_data['basic_eps']
                            
                            if profit and shares and eps_reported:
                                # Calculate EPS (profit is usually in thousands or millions)
                                # Assume profit is in same unit as stated
                                eps_calculated = profit / shares
                                
                                diff_pct = abs(eps_calculated - eps_reported) / eps_reported * 100
                                if diff_pct > 10:  # 10% tolerance
                                    result['warnings'].append(
                                        f"EPS validation: Reported {eps_reported:.2f} vs "
                                        f"Calculated {eps_calculated:.2f} - Check units"
                                    )
        
        # Validate ratio ranges
        ratios = metrics.get('financial_ratios', {})
        
        if 'roe' in ratios:
            roe = ratios['roe']
            if roe < -100 or roe > 200:
                result['warnings'].append(f"ROE of {roe:.1f}% seems unrealistic")
        
        if 'current_ratio' in ratios:
            cr = ratios['current_ratio']
            if cr < 0 or cr > 100:
                result['warnings'].append(f"Current Ratio of {cr:.2f} seems unrealistic")
        
        return result
    
    def _calculate_confidence(self, report: Dict) -> float:
        """Calculate overall confidence score"""
        # Start with 100%
        confidence = 100.0
        
        # Deduct for critical errors
        confidence -= len(report['issues']) * 15
        
        # Deduct for warnings
        confidence -= len(report['warnings']) * 5
        
        # Average statement confidence scores
        stmt_scores = [
            v.get('confidence_score', 0) 
            for v in report['statement_validations'].values()
        ]
        if stmt_scores:
            avg_stmt_confidence = sum(stmt_scores) / len(stmt_scores)
            confidence = (confidence + avg_stmt_confidence) / 2
        
        return max(0, min(100, confidence))
    
    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generate actionable recommendations based on validation results"""
        recommendations = []
        
        # Low confidence
        if report['overall_confidence'] < 70:
            recommendations.append(
                "⚠️ Confidence score is below 70%. Manual review strongly recommended."
            )
        
        # Critical issues
        if report['issues']:
            recommendations.append(
                f"🔴 {len(report['issues'])} critical issue(s) found. "
                "Review and correct before using for investment decisions."
            )
        
        # Balance sheet not balanced
        for stmt_type, validation in report['statement_validations'].items():
            if stmt_type == 'balance_sheet':
                balance_check = validation.get('checks', {}).get('balance', {})
                if not balance_check.get('passed', True):
                    recommendations.append(
                        "🔴 Balance Sheet does not balance. Verify extraction accuracy."
                    )
        
        # Missing key statements
        if len(report['statement_validations']) < 3:
            recommendations.append(
                "⚠️ Some financial statements are missing. Consider manual extraction."
            )
        
        # High warning count
        if len(report['warnings']) > 5:
            recommendations.append(
                f"⚠️ {len(report['warnings'])} warnings detected. Review for data quality issues."
            )
        
        # Good quality
        if report['overall_confidence'] >= 90 and not report['issues']:
            recommendations.append(
                "✅ Data quality is excellent. Safe to proceed with analysis."
            )
        elif report['overall_confidence'] >= 80:
            recommendations.append(
                "✅ Data quality is good. Minor manual verification recommended."
            )
        
        return recommendations
