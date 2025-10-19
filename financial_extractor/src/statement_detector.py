"""
Detects financial statements within text documents
"""
import re
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class StatementDetector:
    """Detects and locates financial statements in text"""

    def __init__(self, keywords: Dict[str, List[str]]):
        """
        Initialize detector with statement keywords

        Args:
            keywords: Dictionary mapping statement types to keyword patterns
        """
        self.keywords = keywords
        self.compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for efficient matching"""
        compiled = {}
        for stmt_type, patterns in self.keywords.items():
            compiled[stmt_type] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                for pattern in patterns
            ]
        return compiled

    def detect_statements(self, text: str) -> Dict[str, List[Tuple[int, int, str]]]:
        """
        Detect all financial statements in text

        Args:
            text: Document text to search

        Returns:
            Dictionary mapping statement types to list of (start_pos, end_pos, matched_text)
        """
        results = {}

        for stmt_type, patterns in self.compiled_patterns.items():
            matches = []
            for pattern in patterns:
                for match in pattern.finditer(text):
                    matches.append((
                        match.start(),
                        match.end(),
                        match.group()
                    ))

            if matches:
                results[stmt_type] = sorted(matches, key=lambda x: x[0])
                logger.info(f"Found {len(matches)} occurrences of {stmt_type}")

        return results

    def extract_statement_section(
        self, 
        text: str, 
        stmt_type: str,
        context_lines: int = 500
    ) -> Optional[str]:
        """
        Extract the full section of a statement including table data

        Args:
            text: Document text
            stmt_type: Type of statement to extract
            context_lines: Number of lines to include after statement header

        Returns:
            Extracted statement text or None if not found
        """
        detections = self.detect_statements(text)

        if stmt_type not in detections or not detections[stmt_type]:
            logger.warning(f"Statement type '{stmt_type}' not found")
            return None

        # Choose the most likely occurrence based on nearby context (avoid Contents page)
        start_pos = self._choose_best_occurrence(text, detections[stmt_type])

        # Find the end of the statement section
        # Look for the next statement or a certain number of lines
        lines = text[start_pos:].split('\n')

        # Take lines until we hit another statement or reach context_lines
        end_line = min(context_lines, len(lines))

        # Check if another statement starts within the context
        for i, line in enumerate(lines[1:end_line], start=1):
            for other_type, other_patterns in self.compiled_patterns.items():
                if other_type != stmt_type:
                    for pattern in other_patterns:
                        if pattern.search(line):
                            end_line = i
                            break

        extracted_text = '\n'.join(lines[:end_line])
        logger.info(f"Extracted {len(extracted_text)} characters for {stmt_type}")

        return extracted_text

    def _choose_best_occurrence(self, text: str, matches: List[Tuple[int, int, str]]) -> int:
        """Pick the occurrence whose following context looks like a table section.

        Heuristics: count of year tokens, presence of 'Rs 000', 'For the year ended', 'Bank', 'Group'
        in the next ~1500 characters. Prefer higher score; tie-breaker: later in document.
        """
        best_score = -1
        best_pos = matches[0][0]
        for start, end, _ in matches:
            window = text[start:start + 2000]
            # Features
            year_hits = len(re.findall(r'\b(19|20)\d{2}\b', window))
            markers = 0
            for kw in ['Rs 000', 'For the year ended', 'Bank', 'Group', 'Note']:
                if kw.lower() in window.lower():
                    markers += 1
            score = year_hits + 2 * markers
            # Prefer later sections slightly to avoid contents pages
            score += start / max(1, len(text))
            if score > best_score:
                best_score = score
                best_pos = start
        return best_pos

    def get_statement_boundaries(
        self, 
        text: str
    ) -> Dict[str, Tuple[int, int]]:
        """
        Get start and end positions for all statements

        Args:
            text: Document text

        Returns:
            Dictionary mapping statement types to (start_pos, end_pos) tuples
        """
        detections = self.detect_statements(text)
        boundaries = {}

        # Sort all detections by position
        all_positions = []
        for stmt_type, matches in detections.items():
            if matches:
                all_positions.append((matches[0][0], stmt_type))

        all_positions.sort()

        # Assign boundaries
        for i, (start_pos, stmt_type) in enumerate(all_positions):
            if i < len(all_positions) - 1:
                end_pos = all_positions[i + 1][0]
            else:
                end_pos = len(text)

            boundaries[stmt_type] = (start_pos, end_pos)

        return boundaries


# Example usage
if __name__ == "__main__":
    from config import STATEMENT_KEYWORDS

    detector = StatementDetector(STATEMENT_KEYWORDS)

    # Test with sample text
    sample_text = """
    FINANCIAL STATEMENTS

    Statement of Financial Position
    As at 31 December 2024

    Assets                          2024        2023
    Cash                         100,000      90,000
    Inventory                    200,000     180,000

    Income Statement
    For the year ended 31 December 2024

    Revenue                      500,000     450,000
    Expenses                     300,000     280,000
    """

    results = detector.detect_statements(sample_text)
    print(f"Detected statements: {list(results.keys())}")

    balance_sheet = detector.extract_statement_section(
        sample_text, 
        "balance_sheet"
    )
    print(f"\nExtracted Balance Sheet:\n{balance_sheet}")
