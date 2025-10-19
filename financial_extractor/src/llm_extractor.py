"""
LLM-powered table extractor using Perplexity API as intelligent fallback
"""
import os
import json
import logging
from typing import Optional, Dict, Any
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class LLMTableExtractor:
    """Uses Perplexity AI to extract tables from financial statement text"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM extractor with Perplexity API

        Args:
            api_key: Perplexity API key (if not provided, reads from environment)
        """
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment or parameters")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.perplexity.ai"
        )
        
        # Use Perplexity's Sonar model for structured extraction
        self.model = "sonar"
        
    def extract_table(
        self, 
        text: str, 
        statement_type: str,
        company_context: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Extract table from text using LLM with structured prompting

        Args:
            text: Text section containing the statement
            statement_type: Type of statement (balance_sheet, income_statement, etc.)
            company_context: Optional company name for context

        Returns:
            DataFrame with extracted table or None
        """
        try:
            logger.info(f"Using LLM extraction for {statement_type}")
            
            # Build context-aware prompt
            prompt = self._build_extraction_prompt(text, statement_type, company_context)
            
            # Call Perplexity API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for precise extraction
                max_tokens=4000
            )
            
            # Parse response
            content = response.choices[0].message.content
            logger.debug(f"LLM response length: {len(content)} chars")
            
            # Extract structured data from response
            df = self._parse_llm_response(content, statement_type)
            
            if df is not None and not df.empty:
                logger.info(f"LLM extracted {len(df)} rows, {len(df.columns)} columns")
                return df
            else:
                logger.warning("LLM extraction produced empty result")
                return None
                
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return None

    def _get_system_prompt(self) -> str:
        """System prompt defining the LLM's role"""
        return """You are an expert financial data extraction assistant specializing in parsing annual reports and financial statements. Your task is to:

1. Identify and extract tabular financial data from text
2. Preserve exact numerical values and formatting
3. Recognize column headers (years, entities like Bank/Group)
4. Handle multi-line row labels and wrapped text
5. Output structured data in JSON format

Rules:
- Never hallucinate or infer missing values
- Mark missing/unavailable values as null
- Handle negative numbers in parentheses: (123) = -123
- Treat dashes (-) as null values
- Preserve all row labels exactly as they appear
- Identify all year columns and entity groupings (Bank vs Group)"""

    def _build_extraction_prompt(
        self, 
        text: str, 
        statement_type: str,
        company_context: Optional[str]
    ) -> str:
        """Build extraction prompt with context"""
        
        # Map statement types to descriptive names
        statement_names = {
            'balance_sheet': 'Statement of Financial Position / Balance Sheet',
            'income_statement': 'Income Statement / Statement of Profit or Loss',
            'cash_flow': 'Cash Flow Statement / Statement of Cash Flows',
            'equity_statement': 'Statement of Changes in Equity / Shareholders\' Equity'
        }
        
        statement_name = statement_names.get(statement_type, statement_type)
        company_str = f" for {company_context}" if company_context else ""
        
        prompt = f"""Extract the {statement_name}{company_str} from the following text.

The text may have:
- Headers split across multiple lines
- Each value on its own line (PDF extraction artifact)
- Bank and Group columns (separate entity reporting)
- Multiple year comparisons (e.g., 2024 vs 2023)
- Row labels that span multiple lines
- Negative numbers in parentheses
- Dashes (-) for missing values
- Currency units like "Rs 000" or "Rs Mn"

OUTPUT FORMAT:
Return a JSON object with this exact structure:
{{
    "headers": ["Line Item", "Bank_2024", "Bank_2023", "Group_2024", "Group_2023"],
    "rows": [
        {{
            "Line Item": "Revenue",
            "Bank_2024": 500000,
            "Bank_2023": 450000,
            "Group_2024": 520000,
            "Group_2023": 470000
        }},
        ...
    ]
}}

Important:
- Use null for missing/unavailable values
- Convert (123) to -123
- Convert - to null
- Remove commas from numbers
- Preserve exact row labels
- Infer column headers from context (Bank/Group, years)

TEXT TO EXTRACT:
{text[:12000]}

Respond ONLY with the JSON object, no other text."""

        return prompt

    def _parse_llm_response(self, content: str, statement_type: str) -> Optional[pd.DataFrame]:
        """Parse LLM JSON response into DataFrame"""
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_str = content.strip()
            
            # Remove markdown code fences if present
            if json_str.startswith('```'):
                lines = json_str.split('\n')
                # Remove first and last lines (```json and ```)
                json_str = '\n'.join(lines[1:-1]) if len(lines) > 2 else json_str
                json_str = json_str.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Validate structure
            if 'headers' not in data or 'rows' not in data:
                logger.warning("LLM response missing required fields")
                return None
            
            headers = data['headers']
            rows = data['rows']
            
            if not rows:
                logger.warning("LLM response has no data rows")
                return None
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers)
            
            # Clean numeric columns (skip first column - labels)
            for col in df.columns[1:]:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove rows with all NaN values in numeric columns
            df = df.dropna(how='all', subset=df.columns[1:])
            
            return df
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"Response content: {content[:500]}")
            return None
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return None

    def extract_with_retry(
        self,
        text: str,
        statement_type: str,
        company_context: Optional[str] = None,
        max_retries: int = 2
    ) -> Optional[pd.DataFrame]:
        """
        Extract table with retry logic

        Args:
            text: Text to extract from
            statement_type: Statement type
            company_context: Company name
            max_retries: Maximum retry attempts

        Returns:
            DataFrame or None
        """
        for attempt in range(max_retries):
            try:
                df = self.extract_table(text, statement_type, company_context)
                if df is not None and not df.empty:
                    return df
                logger.warning(f"Attempt {attempt + 1}/{max_retries} produced empty result")
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
        
        logger.error(f"All {max_retries} extraction attempts failed")
        return None


def test_llm_extractor():
    """Test the LLM extractor with sample text"""
    sample_text = """
    INCOME STATEMENT
    Bank
    Group
    2024
    2023
    2024
    2023
    Rs 000
    Rs 000
    Rs 000
    Rs 000
    
    Gross income
    190,869,912
    299,139,347
    228,945,309
    336,638,191
    
    Interest income
    222,690,253
    284,097,697
    240,243,657
    304,578,112
    
    Less : Interest expenses
    126,402,153
    179,755,441
    130,478,678
    186,503,550
    
    Net interest income
    96,288,100
    104,342,256
    109,764,979
    118,074,562
    """
    
    try:
        extractor = LLMTableExtractor()
        df = extractor.extract_table(sample_text, 'income_statement', 'HNB')
        
        if df is not None:
            print("Extraction successful!")
            print(df.to_string())
        else:
            print("Extraction failed")
            
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    test_llm_extractor()
