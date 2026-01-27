import os
import json
from typing import Dict, List, Optional
import openai
from openai import OpenAI


class AIReviewError(Exception):
    """Custom exception for AI review processing errors."""


class AIReviewer:
    """Performs AI-based code reviews using OpenAI's API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AIReviewer with the OpenAI client.
        
        Args:
            api_key: Optional OpenAI API key. If not provided, uses OPENAI_API_KEY environment variable.
        
        Raises:
            ValueError: If no API key is provided and environment variable is not set.
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable.")
        self.client = OpenAI(api_key=api_key, timeout=30.0)
    
    def review_code(self, code_diff: str) -> Dict[str, str | List[str]]:
        """Analyzes the provided code diff and generates a review.
        
        Args:
            code_diff: A string representing the code diff to review.
        
        Returns:
            Dictionary containing 'summary', 'suggestions', and 'severity' keys.
        """
        try:
            prompt = self._build_prompt(code_diff)
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1000
            )
            return self._parse_response(response.choices[0].message.content)
        except Exception as e:
            return {
                "summary": f"AI review failed: {str(e)}",
                "suggestions": [],
                "severity": "INFO"
            }
    
    def _build_prompt(self, code_diff: str) -> str:
        return f"""Analyze this code diff and provide:
1. Brief summary of issues
2. Specific improvement suggestions
3. Overall severity (CRITICAL/HIGH/MEDIUM/LOW/INFO)
Format response as JSON with keys: summary, suggestions (list), severity.
Code Diff:
{code_diff}"""
    
    def _parse_response(self, response: str) -> Dict[str, str | List[str]]:
        try:
            data = json.loads(response)
            valid_severity = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}
            
            if not all(key in data for key in ("summary", "suggestions", "severity")):
                raise ValueError("Missing required keys in AI response")
            
            if data["severity"] not in valid_severity:
                raise ValueError(f"Invalid severity value: {data['severity']}")
            
            return {
                "summary": data["summary"],
                "suggestions": data["suggestions"],
                "severity": data["severity"]
            }
        except json.JSONDecodeError:
            raise AIReviewError("Failed to decode AI response")
        except ValueError as e:
            raise AIReviewError(f"Invalid response format: {str(e)}")
