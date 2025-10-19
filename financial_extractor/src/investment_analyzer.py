"""
Investment Analysis Module - Extracts key metrics and ratios for investment decisions
"""
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class InvestmentMetricsExtractor:
    """Extracts key investment metrics from financial reports"""
    
    def __init__(self):
        self.metrics = {}
        
    def extract_all_metrics(self, text: str, company_name: str) -> Dict[str, Any]:
        """
        Extract comprehensive investment metrics from annual report
        
        Args:
            text: Full document text
            company_name: Company name
            
        Returns:
            Dictionary containing all extracted metrics
        """
        logger.info("Extracting investment metrics...")
        
        results = {
            'company': company_name,
            'extraction_date': datetime.now().isoformat(),
            'metrics': {}
        }
        
        # 1. Share Information
        results['metrics']['share_info'] = self._extract_share_info(text)
        
        # 2. Earnings Per Share (EPS)
        results['metrics']['eps'] = self._extract_eps(text)
        
        # 3. Dividends Information
        results['metrics']['dividends'] = self._extract_dividends(text)
        
        # 4. Net Asset Value (NAV) per share
        results['metrics']['nav_per_share'] = self._extract_nav_per_share(text)
        
        # 5. Market Information
        results['metrics']['market_info'] = self._extract_market_info(text)
        
        # 6. Capital Adequacy (for banks)
        results['metrics']['capital_adequacy'] = self._extract_capital_adequacy(text)
        
        # 7. Key Financial Ratios
        results['metrics']['financial_ratios'] = self._extract_financial_ratios(text)
        
        # 8. Management & Governance
        results['metrics']['governance'] = self._extract_governance_info(text)
        
        # 9. Risk Factors
        results['metrics']['risk_factors'] = self._extract_risk_factors(text)
        
        # 10. Future Outlook
        results['metrics']['outlook'] = self._extract_outlook(text)
        
        # 11. Segment Performance
        results['metrics']['segment_analysis'] = self._extract_segment_performance(text)
        
        # 12. Related Party Transactions
        results['metrics']['related_party'] = self._extract_related_party(text)
        
        return results
    
    def _extract_share_info(self, text: str) -> Dict:
        """Extract share-related information"""
        info = {
            'outstanding_shares': None,
            'authorized_shares': None,
            'market_capitalization': None,
            'share_price_range': {},
            'float': None
        }
        
        # Outstanding shares patterns
        patterns = [
            r'(?:number of|outstanding)\s+(?:ordinary\s+)?shares[:\s]+(?:Rs\.?\s*)?([0-9,]+(?:\.[0-9]+)?)\s*(?:million|mn|m\b)?',
            r'issued\s+and\s+fully\s+paid\s+(?:ordinary\s+)?shares[:\s]+([0-9,]+)',
            r'shares\s+in\s+issue[:\s]+([0-9,]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['outstanding_shares'] = self._parse_number(match.group(1))
                break
        
        # Market cap
        cap_match = re.search(
            r'market\s+capitalization[:\s]+Rs\.?\s*([0-9,]+(?:\.[0-9]+)?)\s*(million|billion|mn|bn)?',
            text, re.IGNORECASE
        )
        if cap_match:
            info['market_capitalization'] = {
                'value': self._parse_number(cap_match.group(1)),
                'unit': cap_match.group(2) if cap_match.lastindex >= 2 else 'Rs'
            }
        
        # Share price range
        price_pattern = r'(?:share\s+price|market\s+price)[:\s]+.*?(?:high|highest)[:\s]+Rs\.?\s*([0-9,.]+).*?(?:low|lowest)[:\s]+Rs\.?\s*([0-9,.]+)'
        price_match = re.search(price_pattern, text, re.IGNORECASE | re.DOTALL)
        if price_match:
            info['share_price_range'] = {
                'high': self._parse_number(price_match.group(1)),
                'low': self._parse_number(price_match.group(2))
            }
        
        logger.info(f"Extracted share info: {info}")
        return info
    
    def _extract_eps(self, text: str) -> Dict:
        """Extract Earnings Per Share data"""
        eps_data = {}
        
        # Basic EPS
        patterns = [
            r'(?:basic\s+)?earnings\s+per\s+share[:\s]+Rs\.?\s*([0-9,.]+)',
            r'EPS[:\s]+Rs\.?\s*([0-9,.]+)',
            r'per\s+share\s+data.*?earnings[:\s]+Rs\.?\s*([0-9,.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                eps_data['basic_eps'] = self._parse_number(match.group(1))
                break
        
        # Diluted EPS
        diluted_match = re.search(
            r'diluted\s+earnings\s+per\s+share[:\s]+Rs\.?\s*([0-9,.]+)',
            text, re.IGNORECASE
        )
        if diluted_match:
            eps_data['diluted_eps'] = self._parse_number(diluted_match.group(1))
        
        logger.info(f"Extracted EPS: {eps_data}")
        return eps_data
    
    def _extract_dividends(self, text: str) -> Dict:
        """Extract dividend information"""
        div_data = {
            'dividends_declared': [],
            'total_dividend_per_share': None,
            'dividend_payout_ratio': None,
            'dividend_yield': None
        }
        
        # Dividend per share
        dps_patterns = [
            r'(?:total\s+)?dividend(?:\s+per\s+share)?[:\s]+Rs\.?\s*([0-9,.]+)',
            r'(?:interim|final)\s+dividend[:\s]+Rs\.?\s*([0-9,.]+)\s*per\s+share',
        ]
        
        for pattern in dps_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                div_value = self._parse_number(match.group(1))
                div_data['dividends_declared'].append(div_value)
        
        if div_data['dividends_declared']:
            div_data['total_dividend_per_share'] = sum(div_data['dividends_declared'])
        
        # Dividend payout ratio
        payout_match = re.search(
            r'(?:dividend\s+)?payout\s+ratio[:\s]+([0-9,.]+)\s*%',
            text, re.IGNORECASE
        )
        if payout_match:
            div_data['dividend_payout_ratio'] = self._parse_number(payout_match.group(1))
        
        # Dividend yield
        yield_match = re.search(
            r'dividend\s+yield[:\s]+([0-9,.]+)\s*%',
            text, re.IGNORECASE
        )
        if yield_match:
            div_data['dividend_yield'] = self._parse_number(yield_match.group(1))
        
        logger.info(f"Extracted dividends: {div_data}")
        return div_data
    
    def _extract_nav_per_share(self, text: str) -> Dict:
        """Extract Net Asset Value per share"""
        nav_data = {}
        
        patterns = [
            r'(?:net\s+asset\s+value|NAV)\s+per\s+share[:\s]+Rs\.?\s*([0-9,.]+)',
            r'book\s+value\s+per\s+share[:\s]+Rs\.?\s*([0-9,.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                nav_data['value'] = self._parse_number(match.group(1))
                break
        
        logger.info(f"Extracted NAV: {nav_data}")
        return nav_data
    
    def _extract_market_info(self, text: str) -> Dict:
        """Extract market-related information"""
        market_data = {
            'market_capitalization': None,
            'pe_ratio': None,
            'pb_ratio': None,
            'stock_exchange': []
        }
        
        # P/E Ratio
        pe_patterns = [
            r'(?:price\s+to\s+earnings|P/E)\s+ratio[:\s]+([0-9,.]+)',
            r'PE\s+ratio[:\s]+([0-9,.]+)',
        ]
        for pattern in pe_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                market_data['pe_ratio'] = self._parse_number(match.group(1))
                break
        
        # P/B Ratio
        pb_match = re.search(
            r'(?:price\s+to\s+book|P/B)\s+ratio[:\s]+([0-9,.]+)',
            text, re.IGNORECASE
        )
        if pb_match:
            market_data['pb_ratio'] = self._parse_number(pb_match.group(1))
        
        # Stock exchange listing
        exchanges = ['CSE', 'Colombo Stock Exchange', 'LSE', 'NYSE', 'NASDAQ']
        for exchange in exchanges:
            if re.search(rf'\b{exchange}\b', text, re.IGNORECASE):
                market_data['stock_exchange'].append(exchange)
        
        logger.info(f"Extracted market info: {market_data}")
        return market_data
    
    def _extract_capital_adequacy(self, text: str) -> Dict:
        """Extract capital adequacy ratios (banking sector)"""
        capital_data = {}
        
        # Tier 1 / Core capital
        tier1_match = re.search(
            r'(?:tier\s+1|core\s+capital)\s+ratio[:\s]+([0-9,.]+)\s*%',
            text, re.IGNORECASE
        )
        if tier1_match:
            capital_data['tier1_ratio'] = self._parse_number(tier1_match.group(1))
        
        # Total capital adequacy
        total_match = re.search(
            r'(?:total\s+)?capital\s+adequacy\s+ratio[:\s]+([0-9,.]+)\s*%',
            text, re.IGNORECASE
        )
        if total_match:
            capital_data['total_car'] = self._parse_number(total_match.group(1))
        
        logger.info(f"Extracted capital adequacy: {capital_data}")
        return capital_data
    
    def _extract_financial_ratios(self, text: str) -> Dict:
        """Extract key financial ratios"""
        ratios = {}
        
        # ROE - Return on Equity
        roe_match = re.search(
            r'return\s+on\s+equity[:\s]+([0-9,.]+)\s*%',
            text, re.IGNORECASE
        )
        if roe_match:
            ratios['roe'] = self._parse_number(roe_match.group(1))
        
        # ROA - Return on Assets
        roa_match = re.search(
            r'return\s+on\s+assets[:\s]+([0-9,.]+)\s*%',
            text, re.IGNORECASE
        )
        if roa_match:
            ratios['roa'] = self._parse_number(roa_match.group(1))
        
        # Profit Margin
        margin_match = re.search(
            r'(?:net\s+)?profit\s+margin[:\s]+([0-9,.]+)\s*%',
            text, re.IGNORECASE
        )
        if margin_match:
            ratios['net_profit_margin'] = self._parse_number(margin_match.group(1))
        
        # Current Ratio
        current_match = re.search(
            r'current\s+ratio[:\s]+([0-9,.]+)',
            text, re.IGNORECASE
        )
        if current_match:
            ratios['current_ratio'] = self._parse_number(current_match.group(1))
        
        # Debt to Equity
        de_match = re.search(
            r'debt\s+to\s+equity[:\s]+([0-9,.]+)',
            text, re.IGNORECASE
        )
        if de_match:
            ratios['debt_to_equity'] = self._parse_number(de_match.group(1))
        
        logger.info(f"Extracted financial ratios: {ratios}")
        return ratios
    
    def _extract_governance_info(self, text: str) -> Dict:
        """Extract corporate governance information"""
        gov_data = {
            'board_size': None,
            'independent_directors': None,
            'audit_committee': False,
            'risk_committee': False
        }
        
        # Board composition
        board_match = re.search(
            r'board\s+(?:of\s+directors\s+)?(?:comprises|consists of)[:\s]+([0-9]+)',
            text, re.IGNORECASE
        )
        if board_match:
            gov_data['board_size'] = int(board_match.group(1))
        
        # Independent directors
        ind_match = re.search(
            r'([0-9]+)\s+independent\s+(?:non-executive\s+)?directors',
            text, re.IGNORECASE
        )
        if ind_match:
            gov_data['independent_directors'] = int(ind_match.group(1))
        
        # Committees
        if re.search(r'audit\s+committee', text, re.IGNORECASE):
            gov_data['audit_committee'] = True
        
        if re.search(r'risk\s+(?:management\s+)?committee', text, re.IGNORECASE):
            gov_data['risk_committee'] = True
        
        logger.info(f"Extracted governance info: {gov_data}")
        return gov_data
    
    def _extract_risk_factors(self, text: str) -> List[str]:
        """Extract identified risk factors"""
        risks = []
        
        # Find risk section
        risk_section = re.search(
            r'(?:principal\s+)?risk(?:\s+factors)?[:\s]+(.*?)(?:\n\n|\Z)',
            text, re.IGNORECASE | re.DOTALL
        )
        
        if risk_section:
            # Extract bullet points or numbered items
            risk_text = risk_section.group(1)
            risk_items = re.findall(
                r'(?:^|\n)\s*(?:[\d\-•]|\([a-z]\))\s*(.+?)(?=\n\s*(?:[\d\-•]|\([a-z]\))|\Z)',
                risk_text, re.DOTALL
            )
            risks = [r.strip()[:200] for r in risk_items if len(r.strip()) > 20]
        
        logger.info(f"Extracted {len(risks)} risk factors")
        return risks[:10]  # Top 10 risks
    
    def _extract_outlook(self, text: str) -> Dict:
        """Extract future outlook and projections"""
        outlook = {
            'section_found': False,
            'summary': None
        }
        
        # Find outlook/future prospects section
        outlook_patterns = [
            r'(?:future\s+)?outlook[:\s]+((?:.+?\n){3,10})',
            r'future\s+prospects[:\s]+((?:.+?\n){3,10})',
            r'forward\s+looking[:\s]+((?:.+?\n){3,10})',
        ]
        
        for pattern in outlook_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                outlook['section_found'] = True
                outlook['summary'] = match.group(1).strip()[:500]
                break
        
        logger.info(f"Extracted outlook: {outlook['section_found']}")
        return outlook
    
    def _extract_segment_performance(self, text: str) -> Dict:
        """Extract business segment performance"""
        segments = {}
        
        # Look for segment reporting section
        seg_match = re.search(
            r'segment\s+(?:information|analysis|performance)',
            text, re.IGNORECASE
        )
        
        if seg_match:
            segments['found'] = True
            # Extract segment names mentioned
            segments['segments'] = re.findall(
                r'(?:^|\n)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+segment',
                text[seg_match.start():seg_match.start()+2000],
                re.MULTILINE
            )
        
        logger.info(f"Extracted segment info: {segments}")
        return segments
    
    def _extract_related_party(self, text: str) -> Dict:
        """Extract related party transaction information"""
        related = {
            'disclosed': False,
            'note_reference': None
        }
        
        rp_match = re.search(
            r'related\s+party\s+(?:transactions|disclosures)(?:\s+\(note\s+([0-9]+)\))?',
            text, re.IGNORECASE
        )
        
        if rp_match:
            related['disclosed'] = True
            if rp_match.lastindex >= 1 and rp_match.group(1):
                related['note_reference'] = int(rp_match.group(1))
        
        logger.info(f"Related party transactions: {related}")
        return related
    
    def _parse_number(self, text: str) -> float:
        """Parse numeric string, handling commas and decimals"""
        if not text:
            return None
        try:
            # Remove commas and convert to float
            clean_text = text.replace(',', '')
            return float(clean_text)
        except ValueError:
            logger.warning(f"Could not parse number: {text}")
            return None


def calculate_derived_metrics(statements_data: Dict[str, pd.DataFrame], 
                              investment_metrics: Dict) -> Dict:
    """
    Calculate additional metrics from extracted financial statements
    
    Args:
        statements_data: Dictionary of statement type -> DataFrame
        investment_metrics: Already extracted metrics
        
    Returns:
        Dictionary of calculated metrics
    """
    calculated = {}
    
    try:
        # Get latest year data from income statement
        if 'income_statement' in statements_data:
            inc_stmt = statements_data['income_statement']
            if not inc_stmt.empty and len(inc_stmt.columns) >= 2:
                latest_col = inc_stmt.columns[1]  # First numeric column
                
                # Revenue growth
                if len(inc_stmt.columns) >= 3:
                    revenue_row = inc_stmt[inc_stmt.iloc[:, 0].str.contains('revenue|income', case=False, na=False)]
                    if not revenue_row.empty:
                        current = pd.to_numeric(revenue_row.iloc[0, 1], errors='coerce')
                        previous = pd.to_numeric(revenue_row.iloc[0, 2], errors='coerce')
                        if current and previous and previous != 0:
                            calculated['revenue_growth_pct'] = ((current - previous) / previous) * 100
                
                # Net profit margin
                revenue_row = inc_stmt[inc_stmt.iloc[:, 0].str.contains('revenue|income', case=False, na=False)]
                profit_row = inc_stmt[inc_stmt.iloc[:, 0].str.contains('net profit|profit for', case=False, na=False)]
                
                if not revenue_row.empty and not profit_row.empty:
                    revenue = pd.to_numeric(revenue_row.iloc[0, 1], errors='coerce')
                    profit = pd.to_numeric(profit_row.iloc[0, 1], errors='coerce')
                    if revenue and profit and revenue != 0:
                        calculated['net_profit_margin_pct'] = (profit / revenue) * 100
        
        # Get data from balance sheet
        if 'balance_sheet' in statements_data:
            bal_sheet = statements_data['balance_sheet']
            if not bal_sheet.empty and len(bal_sheet.columns) >= 2:
                
                # Current ratio
                current_assets = bal_sheet[bal_sheet.iloc[:, 0].str.contains('current assets', case=False, na=False)]
                current_liab = bal_sheet[bal_sheet.iloc[:, 0].str.contains('current liabilities', case=False, na=False)]
                
                if not current_assets.empty and not current_liab.empty:
                    assets = pd.to_numeric(current_assets.iloc[0, 1], errors='coerce')
                    liab = pd.to_numeric(current_liab.iloc[0, 1], errors='coerce')
                    if assets and liab and liab != 0:
                        calculated['current_ratio'] = assets / liab
                
                # Debt to equity
                equity = bal_sheet[bal_sheet.iloc[:, 0].str.contains('total equity|shareholders', case=False, na=False)]
                debt = bal_sheet[bal_sheet.iloc[:, 0].str.contains('total liabilities|borrowings', case=False, na=False)]
                
                if not equity.empty and not debt.empty:
                    eq_val = pd.to_numeric(equity.iloc[0, 1], errors='coerce')
                    debt_val = pd.to_numeric(debt.iloc[0, 1], errors='coerce')
                    if eq_val and debt_val and eq_val != 0:
                        calculated['debt_to_equity'] = debt_val / eq_val
        
        logger.info(f"Calculated derived metrics: {calculated}")
        
    except Exception as e:
        logger.error(f"Error calculating derived metrics: {e}")
    
    return calculated
