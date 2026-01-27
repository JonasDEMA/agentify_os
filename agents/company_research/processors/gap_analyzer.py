"""
Gap Analyzer - Identify missing company data
"""

from typing import List, Dict, Any


class GapAnalyzer:
    """Analyze gaps in company data"""
    
    def __init__(self, required_fields: List[str]):
        self.required_fields = required_fields
    
    def analyze(self, companies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze data gaps"""
        total = len(companies)
        complete = 0
        incomplete = 0
        missing_fields = {}

        for company in companies:
            is_complete = all(
                field in company and company[field] and str(company[field]).strip()
                for field in self.required_fields
            )

            if is_complete:
                complete += 1
            else:
                incomplete += 1

                # Track missing fields
                for field in self.required_fields:
                    if field not in company or not company[field] or not str(company[field]).strip():
                        missing_fields[field] = missing_fields.get(field, 0) + 1

        return {
            "total_companies": total,
            "complete_records": complete,
            "incomplete_records": incomplete,
            "missing_fields": missing_fields,
            "completion_rate": (complete / total * 100) if total > 0 else 0
        }
    
    def get_companies_with_gaps(
        self,
        companies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get list of companies with missing data"""
        companies_with_gaps = []

        for company in companies:
            missing = [
                field for field in self.required_fields
                if field not in company or not company[field] or not str(company[field]).strip()
            ]

            if missing:
                companies_with_gaps.append({
                    "company": company,
                    "missing_fields": missing
                })

        return companies_with_gaps

