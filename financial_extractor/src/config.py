"""
Configuration file for financial statement extractor
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
TEMPLATES_DIR = DATA_DIR / "templates"

# Create directories if they don't exist
for dir_path in [RAW_DIR, PROCESSED_DIR, TEMPLATES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Financial statement keywords
STATEMENT_KEYWORDS = {
    "balance_sheet": [
        r"statement of financial position",
        r"balance sheet",
        r"statement of assets",
    ],
    "income_statement": [
        r"income statement",
        r"statement of profit or loss",
        r"profit and loss statement",
        r"statement of comprehensive income",
    ],
    "cash_flow": [
        r"cash flow statement",
        r"statement of cash flows",
        r"cash flows from operating",
    ],
    "equity_statement": [
        r"statement of changes in equity",
        r"statement of shareholders[\']? equity",
        r"statement of retained earnings",
    ],
}

# Table detection patterns
TABLE_PATTERNS = {
    "numeric_column": r"\d{1,3}(?:,\d{3})*(?:\.\d+)?",  # Matches numbers like 1,234.56
    "year_header": r"20\d{2}|\d{4}",  # Matches years
    "currency": r"(?:Rs|USD|EUR|GBP)[\s\.]?(?:\d|Mn|Bn|Million|Billion)?",
}

# Data cleaning rules
CLEANUP_PATTERNS = {
    "remove_chars": r"[\(\)\[\]]",  # Remove parentheses and brackets
    "thousand_separator": r",",
    "negative_indicator": r"\(([\d,\.]+)\)",  # (123.45) means negative
}

# Export settings
CSV_SETTINGS = {
    "encoding": "utf-8",
    "index": False,
    "float_format": "%.2f",
}

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
