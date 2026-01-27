"""
LLM Extractor - Use LLM to extract structured data from text
"""

from typing import Dict, Any, List
import json
from openai import OpenAI

from config import settings


class LLMExtractor:
    """Extract structured information using LLM"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def extract_company_info(
        self, 
        text: str, 
        fields: List[str]
    ) -> Dict[str, Any]:
        """Extract company information from text using LLM"""
        # TODO: Implement LLM extraction
        # - Create prompt with field definitions
        # - Call OpenAI API
        # - Parse JSON response
        # - Return extracted data with confidence
        
        # Build field descriptions
        field_descriptions = {
            "managing_directors": "Names of managing directors (Geschäftsführer)",
            "revenue": "Company revenue/turnover (Umsatz) in EUR",
            "employees": "Number of employees (Anzahl Mitarbeiter)",
            "history": "Brief company history",
            "news": "Recent company news or announcements"
        }
        
        # Create extraction prompt
        prompt = f"""Extract the following information about the company from the text below:

Fields to extract:
{json.dumps({field: field_descriptions.get(field, field) for field in fields}, indent=2)}

Text:
{text[:4000]}  # Limit text length

Return a JSON object with the extracted information. If a field is not found, use null.
Also include a confidence score (0.0-1.0) for each field.

Format:
{{
  "data": {{
    "field_name": "extracted value",
    ...
  }},
  "confidence": {{
    "field_name": 0.8,
    ...
  }}
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data extraction assistant. Extract structured information from text accurately."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"❌ LLM extraction error: {e}")
            return {
                "data": {},
                "confidence": {}
            }
    
    def extract_managing_directors(self, text: str) -> List[str]:
        """Extract managing directors from text"""
        # TODO: Specialized extraction for managing directors
        result = self.extract_company_info(text, ["managing_directors"])
        directors = result.get("data", {}).get("managing_directors", [])
        
        if isinstance(directors, str):
            # Split if comma-separated
            directors = [d.strip() for d in directors.split(",")]
        
        return directors
    
    def extract_company_size(self, text: str) -> Dict[str, Any]:
        """Extract company size (revenue and employees)"""
        # TODO: Specialized extraction for company size
        result = self.extract_company_info(text, ["revenue", "employees"])
        return result.get("data", {})

