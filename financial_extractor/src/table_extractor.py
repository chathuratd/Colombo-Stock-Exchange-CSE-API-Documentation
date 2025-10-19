"""
Extracts tabular data from financial statement text
"""
import re
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class TableExtractor:
    """Extracts structured table data from text"""

    def __init__(self):
        self.numeric_pattern = re.compile(r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b')
        self.year_pattern = re.compile(r'\b(19|20)\d{2}\b')
        self.negative_pattern = re.compile(r'\(([\d,\.]+)\)')

    def extract_table(
        self, 
        text: str,
        min_numeric_cols: int = 2
    ) -> Optional[pd.DataFrame]:
        """
        Extract table from text block

        Args:
            text: Text containing table
            min_numeric_cols: Minimum number of numeric columns to consider a valid table

        Returns:
            DataFrame with extracted table or None
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        if not lines:
            return None

        # Find header row (usually contains years)
        header_idx = self._find_header_row(lines)

        if header_idx is None:
            logger.warning("Could not find table header row")
            return None

        # Extract headers
        headers = self._extract_headers(lines[header_idx])

        # Extract data rows
        data_rows = []
        for line in lines[header_idx + 1:]:
            row = self._extract_row(line, len(headers))
            if row:
                data_rows.append(row)

        if not data_rows:
            logger.warning("No data rows found")
            return None

        # Create DataFrame
        try:
            df = pd.DataFrame(data_rows, columns=headers)

            # Clean numeric columns
            df = self._clean_dataframe(df)

            return df
        except Exception as e:
            logger.error(f"Error creating DataFrame: {e}")
            return None

    def _find_header_row(self, lines: List[str]) -> Optional[int]:
        """Find the row that contains column headers (usually years)"""
        for i, line in enumerate(lines):
            # Look for lines with multiple years or 'Rs', 'USD', etc.
            year_matches = self.year_pattern.findall(line)
            if len(year_matches) >= 2:
                return i
            # Or look for currency indicators
            if re.search(r'\b(Rs|USD|EUR|GBP)\b', line, re.IGNORECASE):
                return i

        # Fallback: use first line with multiple numeric values
        for i, line in enumerate(lines):
            if len(self.numeric_pattern.findall(line)) >= 2:
                return max(0, i - 1)  # Header is usually line before data

        return None

    def _extract_headers(self, header_line: str) -> List[str]:
        """Extract column headers from header line"""
        # Split by multiple spaces or tabs
        parts = re.split(r'\s{2,}|\t', header_line)
        headers = [p.strip() for p in parts if p.strip()]

        # First column is usually description
        if not headers:
            headers = ['Description']
        elif not any(keyword in headers[0].lower() 
                    for keyword in ['item', 'description', 'particulars']):
            headers = ['Description'] + headers

        return headers

    def _extract_row(self, line: str, num_cols: int) -> Optional[List]:
        """Extract a single data row"""
        # Split line into parts
        parts = re.split(r'\s{2,}|\t', line)
        parts = [p.strip() for p in parts if p.strip()]

        if len(parts) < 2:  # Need at least label + 1 value
            return None

        # First part is usually the row label
        row_label = parts[0]

        # Rest are numeric values
        values = []
        for part in parts[1:]:
            values.append(self._parse_number(part))

        # Pad with None if needed
        while len(values) < num_cols - 1:
            values.append(None)

        return [row_label] + values[:num_cols - 1]

    def _parse_number(self, text: str) -> Optional[float]:
        """Parse number from text, handling negatives and formatting"""
        # Handle negative numbers in parentheses
        neg_match = self.negative_pattern.match(text)
        if neg_match:
            text = '-' + neg_match.group(1)

        # Remove thousand separators
        text = text.replace(',', '')

        # Try to convert to float
        try:
            return float(text)
        except ValueError:
            return None

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate DataFrame"""
        # Convert numeric columns
        for col in df.columns[1:]:  # Skip first column (labels)
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Remove completely empty rows
        df = df.dropna(how='all', subset=df.columns[1:])

        # Remove duplicate column names
        df.columns = [f"{col}_{i}" if list(df.columns[:i]).count(col) > 0 
                     else col for i, col in enumerate(df.columns)]

        return df


# Advanced extractor with better pattern matching
class AdvancedTableExtractor(TableExtractor):
    """Enhanced table extractor with better structure recognition"""

    def __init__(self, use_llm_fallback: bool = True):
        """
        Initialize advanced extractor
        
        Args:
            use_llm_fallback: Whether to use LLM extraction as fallback (requires Perplexity API)
        """
        super().__init__()
        self.use_llm_fallback = use_llm_fallback
        self._llm_extractor = None

    def extract_table(self, text: str, statement_type: str = None, company_name: str = None) -> Optional[pd.DataFrame]:
        """Extract tables from text that may have multi-line rows (PDF-extracted)."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        if not lines:
            return None

        # Try robust multi-line parser first
        try:
            df = self._parse_multiline_table(lines)
            if df is not None and not df.empty:
                logger.info("Rule-based extraction successful")
                return df
        except Exception as e:
            logger.debug(f"Multiline parse failed, falling back. Error: {e}")

        # Try base extractor
        try:
            df = super().extract_table(text)
            if df is not None and not df.empty:
                logger.info("Base extractor successful")
                return df
        except Exception as e:
            logger.debug(f"Base extraction failed. Error: {e}")

        # Fallback to LLM extraction if enabled
        if self.use_llm_fallback and statement_type:
            logger.info("Attempting LLM-powered extraction...")
            return self._extract_with_llm(text, statement_type, company_name)

        return None

    def _extract_with_llm(self, text: str, statement_type: str, company_name: Optional[str]) -> Optional[pd.DataFrame]:
        """Use LLM to extract table when rule-based methods fail"""
        try:
            # Lazy load LLM extractor
            if self._llm_extractor is None:
                from llm_extractor import LLMTableExtractor
                self._llm_extractor = LLMTableExtractor()
            
            df = self._llm_extractor.extract_with_retry(
                text=text,
                statement_type=statement_type,
                company_context=company_name,
                max_retries=2
            )
            
            if df is not None and not df.empty:
                logger.info(f"✓ LLM extraction successful: {len(df)} rows extracted")
                return df
            else:
                logger.warning("LLM extraction returned no data")
                return None
                
        except ImportError:
            logger.warning("LLM extractor not available (missing dependencies)")
            return None
        except Exception as e:
            logger.error(f"LLM extraction error: {e}")
            return None

    def _detect_table_lines(self, lines: List[str]) -> List[str]:
        """Detect which lines belong to the table"""
        table_lines = []
        in_table = False

        for line in lines:
            # Check if line looks like table row
            has_numbers = len(self.numeric_pattern.findall(line)) >= 1
            has_label = len(line.split()) >= 2

            if has_numbers and has_label:
                in_table = True
                table_lines.append(line)
            elif in_table and not has_numbers:
                # Might be continuation or end of table
                if len(line) < 100:  # Short line = likely end
                    break
                table_lines.append(line)

        return table_lines

    def _parse_structured_table(self, lines: List[str]) -> pd.DataFrame:
        """Parse table with detected structure"""
        # Similar to parent but with more robust parsing
        return super().extract_table('\n'.join(lines))

    # -------------- New robust parsing helpers --------------
    def _parse_multiline_table(self, lines: List[str]) -> Optional[pd.DataFrame]:
        """Parse a table where each cell may be on its own line (common in PDF text).

        Strategy:
        - Find a header line containing multiple years (e.g., 2024 2023 2024 2023)
        - Infer headers: Bank/Group if present near the header, else generic by years
        - For each label (textual line), collect the following numeric tokens (including '-' and (123))
          until we have expected number of value columns; emit a row.
        """
        hdr = self._find_multiline_header(lines)
        if hdr is None:
            return None
        header_idx, year_list, entities = hdr
        value_cols = max(2, min(6, len(year_list)))

        headers = self._infer_headers(lines, header_idx, year_list, entities, value_cols)

        data_rows: List[List[Optional[float]]] = []

        i = header_idx + 1
        n = len(lines)
        while i < n:
            line = lines[i]
            if self._is_noise_line(line):
                i += 1
                continue

            # Identify a label line (contains letters and not just currency/unit words)
            if self._looks_like_label(line):
                label_parts = [line]
                j = i + 1
                # Accumulate wrapped label lines (until we hit a numeric token line)
                while j < n and not self._is_value_token_line(lines[j]) and not self._looks_like_label_terminator(lines[j]):
                    if not self._is_noise_line(lines[j]):
                        label_parts.append(lines[j])
                    j += 1

                label = self._sanitize_label(' '.join(label_parts))

                # Collect value tokens after the label
                values: List[Optional[float]] = []
                k = j
                while k < n and len(values) < value_cols:
                    val_line = lines[k]
                    if self._is_value_token_line(val_line):
                        values.append(self._parse_token_to_number(val_line))
                        k += 1
                        continue
                    # If we hit a new label before collecting enough values, break row
                    if self._looks_like_label(val_line):
                        break
                    # Skip noise/units/notes lines
                    if self._is_noise_line(val_line):
                        k += 1
                        continue
                    # Non-numeric but not a new label -> likely end of table segment
                    break

                # Only add rows with at least one numeric value
                if any(v is not None for v in values):
                    # Pad values to expected length
                    while len(values) < value_cols:
                        values.append(None)
                    data_rows.append([label] + values[:value_cols])

                # Advance
                i = max(k, j, i + 1)
                continue

            i += 1

        if not data_rows:
            return None
        df = pd.DataFrame(data_rows, columns=headers)
        # Clean numeric columns (skip first column)
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        # Drop rows with all NaNs in numeric part
        df = df.dropna(how='all', subset=df.columns[1:])
        return df

    def _infer_headers(self, lines: List[str], header_idx: int, year_list: List[str], entities: List[str], value_cols: int) -> List[str]:
        """Infer headers using nearby context (Bank/Group) and found year list."""
        headers = ['Line Item']
        if entities and year_list:
            if len(entities) >= 2 and len(year_list) >= 4 and value_cols >= 4:
                headers += [f"{entities[0]}_{year_list[0]}", f"{entities[0]}_{year_list[1]}",
                            f"{entities[1]}_{year_list[2]}", f"{entities[1]}_{year_list[3]}"]
            else:
                # Use first entity with the first N years
                headers += [f"{entities[0]}_{y}" for y in year_list[:value_cols]]
        elif year_list:
            headers += year_list[:value_cols]
        else:
            headers += [f"Col{i+1}" for i in range(value_cols)]
        return headers

    def _find_multiline_header(self, lines: List[str]) -> Optional[Tuple[int, List[str], List[str]]]:
        """Find header as a sequence of consecutive year-only lines; also detect Bank/Group entities.

        Returns (start_index_of_years, year_list, entities)
        """
        def is_year_line(s: str) -> Optional[str]:
            m = re.fullmatch(r'(19|20)\d{2}', s.strip())
            return m.group(0) if m else None

        n = len(lines)
        best = None
        for i in range(n - 1):
            years = []
            j = i
            while j < n:
                y = is_year_line(lines[j])
                if y:
                    years.append(y)
                    j += 1
                    continue
                break
            if len(years) >= 2:
                # Detect entities in the 5 lines preceding i
                ctx_lines = ' '.join(lines[max(0, i - 5):i]).lower()
                entities: List[str] = []
                if 'bank' in ctx_lines:
                    entities.append('Bank')
                if 'group' in ctx_lines:
                    entities.append('Group')
                best = (i, years, entities)
                break
        return best

    def _is_value_token_line(self, line: str) -> bool:
        """A line that holds a single value token like a number, (-), or (123)."""
        token = line.strip()
        # Accept hyphen variants and single tokens
        if token in {'-', '–', '—'}:
            return True
        # A single number element
        if self.numeric_pattern.fullmatch(token):
            return True
        # Negative in parentheses
        if self.negative_pattern.fullmatch(token):
            return True
        return False

    def _parse_token_to_number(self, token: str) -> Optional[float]:
        token = token.strip()
        if token in {'-', '–', '—'}:
            return None
        # Delegate to existing parser
        return self._parse_number(token)

    def _looks_like_label(self, line: str) -> bool:
        # Consider a label if the line has alphabetic characters and is not a unit/currency
        has_alpha = re.search(r'[A-Za-z]', line) is not None
        if not has_alpha:
            return False
        low = line.lower()
        noise_keys = ['rs 000', 'note', 'for the year ended', 'h a t t o n', 'annual report', 'plc', 'page', 'statement of', 'comprehensive', 'income in us dollars']
        return not any(k in low for k in noise_keys)

    def _looks_like_label_terminator(self, line: str) -> bool:
        """Lines that clearly indicate end of a label block (headings, section breaks)."""
        low = line.lower()
        return any(k in low for k in ['h at t o n', 'annual report', 'hatton national bank', 'page '])

    def _is_noise_line(self, line: str) -> bool:
        low = line.lower()
        if not line.strip():
            return True
        return any(k in low for k in [
            'rs 000', 'note', 'bank', 'group', 'for the year ended', 'hatton national bank',
            '| annual report', 'page', 'plc |', 'annua l report', 'lkr', 'rs mn'
        ])

    def _sanitize_label(self, label: str) -> str:
        """Clean up label text by collapsing whitespace and removing trailing separators."""
        # Remove excessive internal spaces
        label = re.sub(r'\s+', ' ', label).strip()
        # Remove leading bullet/numbering dashes or colons
        label = re.sub(r'^[\-•\d\.\)\s]+', '', label)
        return label


if __name__ == "__main__":
    # Test the extractor
    sample_table = """
    Statement of Financial Position
    As at 31 December 2024

                                    2024        2023
                                    Rs 000      Rs 000
    ASSETS
    Cash and cash equivalents      52,113      63,356
    Loans and advances          1,078,106   1,063,675
    Total assets                2,149,966   2,078,538

    LIABILITIES
    Deposits                    1,723,272   1,715,484
    Borrowings                     19,190      19,740
    """

    extractor = TableExtractor()
    df = extractor.extract_table(sample_table)

    if df is not None:
        print("Extracted Table:")
        print(df.to_string())
    else:
        print("Failed to extract table")
