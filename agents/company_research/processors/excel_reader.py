"""
Excel Reader - Parse Excel files and extract company data
"""

from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path
import re


class ExcelReader:
    """Read and parse Excel files with company data"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.df = None
        self.column_mapping = {}

    def read(self) -> pd.DataFrame:
        """Read Excel file into DataFrame"""
        file_ext = self.file_path.suffix.lower()

        try:
            if file_ext in ['.xlsx', '.xls']:
                self.df = pd.read_excel(self.file_path)
            elif file_ext == '.csv':
                # Try different encodings
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                    try:
                        self.df = pd.read_csv(self.file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")

            # Auto-detect column mapping
            self.column_mapping = self.get_column_mapping()

            return self.df

        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")

    def extract_companies(self) -> List[Dict[str, Any]]:
        """Extract company data from DataFrame"""
        if self.df is None:
            raise ValueError("No data loaded. Call read() first.")

        companies = []

        for idx, row in self.df.iterrows():
            company = {}

            # Extract mapped fields
            for standard_field, excel_column in self.column_mapping.items():
                if excel_column in self.df.columns:
                    value = row[excel_column]
                    # Convert NaN to None
                    if pd.isna(value):
                        company[standard_field] = None
                    else:
                        company[standard_field] = str(value).strip()

            # Only add if company has at least a name
            if company.get('company_name'):
                companies.append(company)

        return companies

    def get_column_mapping(self) -> Dict[str, str]:
        """Get mapping of standard fields to Excel columns"""
        if self.df is None:
            return {}

        mapping = {}
        columns = [col.lower() for col in self.df.columns]

        # Define patterns for each field
        patterns = {
            'company_name': [
                r'.*\b(name|firma|company|unternehmen)\b.*',
            ],
            'website': [
                r'.*\b(website|url|web|homepage|webseite)\b.*',
            ],
            'managing_directors': [
                r'.*\b(geschäftsführer|ceo|director|vorstand|management|gf)\b.*',
            ],
            'revenue': [
                r'.*\b(umsatz|revenue|turnover|sales)\b.*',
            ],
            'employees': [
                r'.*\b(mitarbeiter|employees|staff|anzahl.*mitarbeiter)\b.*',
            ],
            'history': [
                r'.*\b(history|geschichte|founded|gründung|about)\b.*',
            ],
            'news': [
                r'.*\b(news|neuigkeiten|aktuell)\b.*',
            ],
        }

        # Match columns to standard fields
        for standard_field, pattern_list in patterns.items():
            for i, col in enumerate(columns):
                for pattern in pattern_list:
                    if re.match(pattern, col, re.IGNORECASE):
                        mapping[standard_field] = self.df.columns[i]
                        break
                if standard_field in mapping:
                    break

        return mapping

