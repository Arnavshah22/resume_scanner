#!/usr/bin/env python3
"""
Simple Summary Generator for Resume Analysis
Generates a local, rules-based summary without any external API calls
"""

from typing import Dict

class AISummaryGenerator:
    """Generate local analysis summaries without any external API"""
    
    def __init__(self):
        pass
    
    def generate_summary(self, 
                        resume_text: str,
                        job_description: str,
                        score_breakdown: Dict,
                        candidate_info: Dict) -> str:
        """Generate a local analysis summary (fallback only)"""
        return self._generate_fallback_summary(score_breakdown)
    
    def _generate_fallback_summary(self, score_breakdown: Dict) -> str:
        """Generate a fallback summary when AI is not available"""
        final_score = score_breakdown.get('final_score', 0)
        skill_score = score_breakdown.get('skill_score', 0)
        experience_score = score_breakdown.get('experience_score', 0)
        
        if final_score >= 80:
            return f"Excellent candidate match with {final_score}% overall score. Strong technical skills ({skill_score}%) and relevant experience ({experience_score}%) make this candidate highly suitable for the position."
        elif final_score >= 60:
            return f"Good candidate match with {final_score}% overall score. Candidate shows potential with moderate skill alignment ({skill_score}%) and experience fit ({experience_score}%). Consider for interview with some training needs."
        elif final_score >= 40:
            return f"Moderate candidate match with {final_score}% overall score. Some skill gaps ({skill_score}%) and experience concerns ({experience_score}%) suggest this candidate may need additional development or training."
        else:
            return f"Poor candidate match with {final_score}% overall score. Significant skill gaps ({skill_score}%) and experience mismatch ({experience_score}%) indicate this candidate may not be suitable for this position."

# Global instance
def get_summary_generator() -> AISummaryGenerator:
    """Get singleton instance of AI Summary Generator"""
    return AISummaryGenerator() 