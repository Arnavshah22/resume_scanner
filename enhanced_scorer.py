import logging
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer, util
import re
from config import SCORING_WEIGHTS, SCORE_THRESHOLDS, SKILL_KEYWORDS

# Configure logging
logger = logging.getLogger(__name__)

class ResumeScorer:
    """Enhanced resume scorer with industrial-grade features"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = self._load_model()
        self.scoring_weights = SCORING_WEIGHTS
        self.score_thresholds = SCORE_THRESHOLDS
        self.skill_keywords = SKILL_KEYWORDS
        
    def _load_model(self) -> SentenceTransformer:
        """Load the sentence transformer model with error handling"""
        try:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
            return model
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {e}")
            # Fallback to a smaller model
            try:
                logger.info("Trying fallback model: all-MiniLM-L6-v2")
                model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Fallback model loaded successfully")
                return model
            except Exception as e2:
                logger.error(f"Error loading fallback model: {e2}")
                raise RuntimeError("Failed to load any sentence transformer model")
    
    @lru_cache(maxsize=1000)
    def calculate_semantic_score(self, resume_text: str, job_description: str) -> float:
        """Calculate semantic similarity score with caching"""
        try:
            # Check if model is loaded
            if not hasattr(self, 'model') or self.model is None:
                logger.error("Model not loaded, attempting to reload...")
                self.model = self._load_model()
                if self.model is None:
                    logger.error("Failed to load model, returning fallback score")
                    return 50.0  # Fallback score
            
            # Prepare text for embedding - use shorter text for speed
            resume_embed_text = f"Resume: {resume_text[:1000]}"
            jd_embed_text = f"Job: {job_description[:1000]}"
            
            # Generate embeddings
            resume_embed = self.model.encode(resume_embed_text, convert_to_tensor=True)
            jd_embed = self.model.encode(jd_embed_text, convert_to_tensor=True)
            
            # Calculate cosine similarity
            similarity = util.cos_sim(resume_embed, jd_embed).item()
            
            # Convert to percentage
            score = round(similarity * 100, 2)
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating semantic score: {e}")
            # Return a reasonable fallback score instead of 0
            return 50.0
    
    def calculate_skill_score(self, resume_skills: List[str], job_description: str) -> Dict[str, Any]:
        """Calculate comprehensive skill matching score with improved algorithm"""
        try:
            # Extract skills from job description
            jd_skills = self._extract_skills_from_jd(job_description)
            
            if not jd_skills:
                return {
                    'score': 0.0,
                    'matched_skills': [],
                    'missing_skills': [],
                    'extra_skills': resume_skills,
                    'skill_coverage': 0.0
                }
            
            # Find matched skills
            matched_skills = []
            missing_skills = []
            
            for jd_skill in jd_skills:
                if any(self._skill_match(jd_skill, resume_skill) for resume_skill in resume_skills):
                    matched_skills.append(jd_skill)
                else:
                    missing_skills.append(jd_skill)
            
            # Calculate base skill coverage
            skill_coverage = len(matched_skills) / len(jd_skills) if jd_skills else 0
            base_score = skill_coverage * 100
            
            # Find extra skills (bonus points)
            extra_skills = [skill for skill in resume_skills 
                          if not any(self._skill_match(skill, jd_skill) for jd_skill in jd_skills)]
            
            # Bonus for extra relevant skills (up to 15 points)
            extra_bonus = min(15, len(extra_skills) * 2)
            
            # Bonus for high skill coverage (up to 10 points)
            coverage_bonus = 0
            if skill_coverage >= 0.8:  # 80% or more skills matched
                coverage_bonus = 10
            elif skill_coverage >= 0.6:  # 60% or more skills matched
                coverage_bonus = 5
            
            # Calculate final skill score
            skill_score = round(min(100, base_score + extra_bonus + coverage_bonus), 2)
            
            return {
                'score': skill_score,
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'extra_skills': extra_skills,
                'skill_coverage': skill_coverage,
                'base_score': base_score,
                'extra_bonus': extra_bonus,
                'coverage_bonus': coverage_bonus
            }
            
        except Exception as e:
            logger.error(f"Error calculating skill score: {e}")
            return {
                'score': 0.0,
                'matched_skills': [],
                'missing_skills': [],
                'extra_skills': [],
                'skill_coverage': 0.0
            }
    
    def _extract_skills_from_jd(self, job_description: str) -> List[str]:
        """Extract required skills from job description"""
        try:
            jd_lower = job_description.lower()
            found_skills = []
            
            # Direct keyword matching
            for skill in self.skill_keywords:
                if skill.lower() in jd_lower:
                    found_skills.append(skill)
            
            # Look for skill patterns
            skill_patterns = [
                r'required\s+skills?[:\s]+([^.]*)',
                r'must\s+have[:\s]+([^.]*)',
                r'requirements[:\s]+([^.]*)',
                r'qualifications[:\s]+([^.]*)',
                r'proficient\s+in[:\s]+([^.]*)',
                r'experience\s+with[:\s]+([^.]*)'
            ]
            
            for pattern in skill_patterns:
                matches = re.findall(pattern, jd_lower)
                for match in matches:
                    # Extract skills from the matched text
                    for skill in self.skill_keywords:
                        if skill.lower() in match and skill not in found_skills:
                            found_skills.append(skill)
            
            return list(set(found_skills))
            
        except Exception as e:
            logger.error(f"Error extracting skills from JD: {e}")
            return []
    
    def _skill_match(self, skill1: str, skill2: str) -> bool:
        """Check if two skills match (with fuzzy matching)"""
        try:
            s1, s2 = skill1.lower(), skill2.lower()
            
            # Exact match
            if s1 == s2:
                return True
            
            # Partial match
            if s1 in s2 or s2 in s1:
                return True
            
            # Handle common variations
            variations = {
                'javascript': ['js', 'ecmascript'],
                'python': ['py'],
                'react': ['reactjs', 'react.js'],
                'node.js': ['nodejs', 'node'],
                'machine learning': ['ml', 'machine learning'],
                'artificial intelligence': ['ai', 'artificial intelligence'],
                'data science': ['datascience', 'data science'],
                'devops': ['dev ops', 'development operations'],
                'ci/cd': ['continuous integration', 'continuous deployment'],
                'rest api': ['rest', 'api', 'restful'],
                'graphql': ['graph ql', 'graph-ql']
            }
            
            for main_skill, variants in variations.items():
                if s1 == main_skill and s2 in variants:
                    return True
                if s2 == main_skill and s1 in variants:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in skill matching: {e}")
            return False
    
    def _extract_required_experience(self, job_description: str) -> int:
        """Extract required years of experience from job description"""
        try:
            if not job_description:
                return 0
                
            jd_lower = job_description.lower()
            
            # Look for experience patterns with more variations
            experience_patterns = [
                r'(?:experience|exp|work\s*experience)[\s\w]*?(\d+)\s*\+?\s*(?:years?|yrs?|y\.?\s*e\.?\s*a?r?s?\b)',
                r'(\d+)\s*\+?\s*(?:years?|yrs?|y\.?\s*e\.?\s*a?r?s?\b)\s*(?:of\s*)?(?:experience|exp|work\s*experience)',
                r'(?:minimum|min\.?|at\s+least|\bmin\b)[\s\w]*(\d+)\s*(?:years?|yrs?|y\.?\s*e\.?\s*a?r?s?\b)',
                r'(\d+)\s*\+?\s*(?:years?|yrs?|y\.?\s*e\.?\s*a?r?s?\b)[\s\w]*(?:experience|exp|work\s*experience|required|needed|preferred)',
                r'(?:\b(?:seeking|looking\s*for|required|needs?|wants?|requires?|must\s*have)[\s\w]*(?:with|of)?\s*)(\d+)\s*\+?\s*(?:years?|yrs?|y\.?\s*e\.?\s*a?r?s?\b)',
                r'(?:\b(?:experience|exp|work\s*experience)[\s\w]*(?:in|of)?\s*)(\d+)\s*\+?\s*(?:years?|yrs?|y\.?\s*e\.?\s*a?r?s?\b)'
            ]
            
            # Also check for ranges like "3-5 years" and take the higher number
            range_patterns = [
                r'(\d+)\s*[\-–—]\s*(\d+)\s*(?:years?|yrs?|y\.?\s*e\.?\s*a?r?s?\b)',
                r'(?:between\s*)?(\d+)\s*(?:and|to|&)\s*(\d+)\s*(?:years?|yrs?|y\.?\s*e\.?\s*a?r?s?\b)'
            ]
            
            max_years = 0
            
            # Check standard patterns
            for pattern in experience_patterns:
                matches = re.findall(pattern, jd_lower)
                for match in matches:
                    try:
                        years = int(match)
                        max_years = max(max_years, years)
                    except (ValueError, TypeError):
                        continue
            
            # Check range patterns
            for pattern in range_patterns:
                matches = re.findall(pattern, jd_lower)
                for match in matches:
                    if isinstance(match, tuple):
                        for m in match:
                            try:
                                years = int(m)
                                max_years = max(max_years, years)
                            except (ValueError, TypeError):
                                continue
                    else:
                        try:
                            years = int(match)
                            max_years = max(max_years, years)
                        except (ValueError, TypeError):
                            continue
            
            # If no specific number found, look for general experience indicators
            if max_years == 0 and any(term in jd_lower for term in ['experience', 'exp', 'work experience']):
                if 'entry level' in jd_lower or 'fresher' in jd_lower or '0-1' in jd_lower or '0 to 1' in jd_lower:
                    return 0
                elif 'senior' in jd_lower or 'lead' in jd_lower or 'principal' in jd_lower:
                    return 5
                elif 'mid-level' in jd_lower or 'mid level' in jd_lower or 'mid' in jd_lower:
                    return 3
                else:
                    return 2  # Default to 2 years if no specific number found but experience is mentioned
            
            return max_years
            
        except Exception as e:
            logger.error(f"Error extracting required experience: {e}")
            return 0
            
    def calculate_experience_score(self, experience_years: int, job_description: str) -> Dict[str, Any]:
        """Calculate experience matching score with improved algorithm"""
        try:
            # Extract required experience from job description
            required_years = self._extract_required_experience(job_description)
            
            if required_years == 0:
                # If no specific requirement, use a default based on job level
                if any(word in job_description.lower() for word in ['senior', 'lead', 'principal', 'architect']):
                    required_years = 5
                elif any(word in job_description.lower() for word in ['junior', 'entry', 'graduate', 'intern']):
                    required_years = 1
                else:
                    required_years = 3
            
            # Calculate base score
            if experience_years >= required_years:
                base_score = 100.0
            else:
                base_score = max(0, (experience_years / required_years) * 100)
            
            # Bonus for optimal experience range (not too junior, not too senior)
            experience_bonus = 0
            if required_years <= 2:  # Junior positions
                if 1 <= experience_years <= 3:
                    experience_bonus = 10  # Perfect fit for junior role
                elif experience_years > 5:
                    experience_bonus = -5   # Overqualified
            elif required_years <= 5:  # Mid-level positions
                if 3 <= experience_years <= 7:
                    experience_bonus = 10  # Perfect fit for mid-level role
                elif experience_years > 10:
                    experience_bonus = -5   # Overqualified
            else:  # Senior positions
                if experience_years >= required_years and experience_years <= required_years + 3:
                    experience_bonus = 10  # Perfect fit for senior role
                elif experience_years < required_years - 2:
                    experience_bonus = -10  # Underqualified
            
            # Bonus for over-qualification (but not too much)
            if experience_years > required_years * 2:
                overqual_bonus = min(5, (experience_years - required_years * 2))
                experience_bonus += overqual_bonus
            
            # Calculate final experience score
            experience_score = round(min(100, max(0, base_score + experience_bonus)), 2)
            
            return {
                'score': experience_score,
                'required_years': required_years,
                'candidate_years': experience_years,
                'experience_gap': experience_years - required_years,
                'base_score': base_score,
                'experience_bonus': experience_bonus
            }
            
        except Exception as e:
            logger.error(f"Error calculating experience score: {e}")
            return {
                'score': 0.0,
                'required_years': 0,
                'candidate_years': experience_years,
                'experience_gap': 0
            }
            
    def calculate_education_score(self, education: List[str], job_description: str) -> Dict[str, Any]:
        """Calculate education matching score"""
        try:
            # Extract education requirements from job description
            jd_lower = job_description.lower()
            
            education_keywords = {
                'bachelor': ['bachelor', 'b.tech', 'b.e', 'b.sc', 'bca'],
                'master': ['master', 'm.tech', 'm.e', 'm.sc', 'mba', 'mca'],
                'phd': ['phd', 'doctorate', 'ph.d'],
                'diploma': ['diploma', 'certificate']
            }
            
            required_education = []
            for level, keywords in education_keywords.items():
                if any(keyword in jd_lower for keyword in keywords):
                    required_education.append(level)
            
            if not required_education:
                return {'score': 50.0, 'required': 'Any', 'candidate': education}
            
            # Check if candidate meets requirements
            candidate_education = ' '.join(education).lower()
            score = 0
            
            for req in required_education:
                # Make sure req exists in education_keywords before accessing
                if req in education_keywords:
                    if any(keyword in candidate_education for keyword in education_keywords[req]):
                        score = 100.0
                        break
            
            return {
                'score': score,
                'required': required_education,
                'candidate': education
            }
            
        except Exception as e:
            logger.error(f"Error calculating education score: {e}")
            return {'score': 0.0, 'required': [], 'candidate': education}
            
    def calculate_overall_score(self, resume_text: str, job_description: str, 
                            resume_skills: List[str], experience_years: int,
                            education: Optional[List[str]] = None) -> Dict[str, Any]:
        """Calculate comprehensive overall score with optimized weights"""
        try:
            # Calculate individual scores
            safe_education = education if education is not None else []
            semantic_score = self.calculate_semantic_score(resume_text, job_description)
            skill_analysis = self.calculate_skill_score(resume_skills, job_description)
            experience_analysis = self.calculate_experience_score(experience_years, job_description)
            education_analysis = self.calculate_education_score(safe_education, job_description)
        
            # Calculate weighted final score with optimized weights
            final_score = round(
                self.scoring_weights.get('skills', 0.45) * skill_analysis.get('score', 0) +
                self.scoring_weights.get('experience', 0.35) * experience_analysis.get('score', 0) +
                self.scoring_weights.get('semantic', 0.20) * semantic_score,
                2
            )
            
            # Determine fit category
            fit_category = self._determine_fit_category(final_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                final_score, skill_analysis, experience_analysis, education_analysis
            )
            
            # Generate detailed breakdown
            breakdown = {
                'final_score': final_score,
                'fit_category': fit_category,
                'semantic_score': semantic_score,
                'skill_score': skill_analysis.get('score', 0),
                'experience_score': experience_analysis.get('score', 0),
                'education_score': education_analysis.get('score', 0),
                'skill_analysis': skill_analysis,
                'experience_analysis': experience_analysis,
                'education_analysis': education_analysis,
                'recommendations': recommendations
            }
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error calculating overall score: {e}")
            return {
                'final_score': 0.0,
                'fit_category': 'Error',
                'semantic_score': 0.0,
                'skill_score': 0.0,
                'experience_score': 0.0,
                'education_score': 0.0,
                'recommendations': ['Error occurred during scoring']
            }

    def _generate_recommendations(self, final_score: float, skill_analysis: Dict, 
                                experience_analysis: Dict, education_analysis: Dict) -> List[str]:
        """Generate personalized recommendations based on score analysis"""
        recommendations = []
        
        # Skill-based recommendations
        if skill_analysis.get('score', 0) < 70:
            missing_skills = skill_analysis.get('missing_skills', [])
            if missing_skills:
                recommendations.append(
                    f"Consider gaining experience with: {', '.join(missing_skills[:3])}"
                )
            else:
                recommendations.append(
                    "Highlight your technical skills more prominently in your resume"
                )
        
        # Experience-based recommendations
        exp_gap = experience_analysis.get('experience_gap', 0)
        if exp_gap < 0:
            recommendations.append(
                f"Consider gaining {abs(exp_gap)} more years of experience in this field"
            )
        elif exp_gap > 5:
            recommendations.append(
                "Consider emphasizing your leadership and mentorship experience"
            )
        
        # Education-based recommendations
        if education_analysis.get('score', 0) < 100:
            req_edu = education_analysis.get('required', [])
            if isinstance(req_edu, list) and req_edu and req_edu != 'Any':
                recommendations.append(
                    f"The position prefers candidates with: {', '.join(req_edu)} education"
                )
            elif isinstance(req_edu, str) and req_edu != 'Any':
                recommendations.append(
                    f"The position prefers candidates with: {req_edu} education"
                )
        
        # General recommendations based on score
        if final_score < 50:
            recommendations.append(
                "Consider applying to more junior positions or gaining additional experience"
            )
        elif final_score > 90:
            recommendations.append(
                "You're an excellent match for this position! Highlight your most relevant achievements."
            )
        
        return recommendations or ["Your profile looks good. Make sure to tailor your application to the job description."]

    def _determine_fit_category(self, score: float) -> str:
        """Determine fit category based on score"""
        if score >= 85:
            return "Excellent Fit"
        elif score >= 70:
            return "Good Fit"
        elif score >= 50:
            return "Moderate Fit"
        else:
            return "Poor Fit"

# Global instance for caching
_scorer_instance = None

def get_scorer() -> ResumeScorer:
    """Get singleton instance of ResumeScorer"""
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = ResumeScorer()
    return _scorer_instance

def calculate_similarity(resume_text: str, 
                        job_description: str, 
                        resume_skills: Optional[List[str]] = None, 
                        experience_years: int = 0,
                        education: Optional[List[str]] = None) -> Dict[str, Any]:
    """Convenience function for backward compatibility"""
    scorer = get_scorer()
    return scorer.calculate_overall_score(
        resume_text, 
        job_description, 
        resume_skills or [], 
        experience_years,
        education or []
    ) 