import re
import spacy
import os
import subprocess
import sys
import logging
from typing import Dict, List, Optional, Tuple
from functools import lru_cache
import json
from datetime import datetime
from config import SKILL_KEYWORDS, EXPERIENCE_PATTERNS, PHONE_PATTERNS

# Configure logging
logger = logging.getLogger(__name__)

class ResumeExtractor:
    """Enhanced resume extractor with industrial-grade features"""
    
    def __init__(self):
        self.nlp = self._load_spacy_model()
        self.skill_keywords = SKILL_KEYWORDS
        self.experience_patterns = EXPERIENCE_PATTERNS
        self.phone_patterns = PHONE_PATTERNS
        
    def _load_spacy_model(self):
        """Load spaCy model with comprehensive error handling"""
        try:
            logger.info("Loading spaCy model...")
            nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
            return nlp
        except OSError:
            logger.warning("Model 'en_core_web_sm' not found. Attempting to download...")
            try:
                subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
                nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model downloaded and loaded successfully")
                return nlp
            except (subprocess.CalledProcessError, OSError) as e:
                logger.error(f"Failed to download spaCy model: {e}")
                logger.warning("Using blank English model. Some NER features may be limited.")
                return spacy.blank("en")
    
    @lru_cache(maxsize=100)
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text with caching for performance"""
        try:
            lower_text = text.lower()
            found_skills = []
            
            # Direct keyword matching
            for skill in self.skill_keywords:
                if skill.lower() in lower_text:
                    found_skills.append(skill)
            
            # Enhanced skill extraction using NLP
            if hasattr(self.nlp, 'pipe_names') and 'ner' in self.nlp.pipe_names:
                doc = self.nlp(text)
                for token in doc:
                    # Look for technical terms and proper nouns
                    if (token.pos_ in ['PROPN', 'NOUN'] and 
                        token.text.lower() in self.skill_keywords and
                        token.text not in found_skills):
                        found_skills.append(token.text)
            
            # Remove duplicates and sort
            unique_skills = list(set([skill.title() for skill in found_skills]))
            return sorted(unique_skills)
            
        except Exception as e:
            logger.error(f"Error extracting skills: {e}")
            return []
    
    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience with enhanced pattern matching"""
        try:
            years = []
            for pattern in self.experience_patterns:
                matches = re.findall(pattern, text.lower())
                years.extend([int(m) for m in matches])
            
            # Also look for experience in different formats
            additional_patterns = [
                r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:professional|technical|industry)',
                r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:in)?\s*(?:it|software|technology)',
                r'experience\s*[:.]?\s*(\d+)\+?\s*(?:years?|yrs?)',
            ]
            
            for pattern in additional_patterns:
                matches = re.findall(pattern, text.lower())
                years.extend([int(m) for m in matches])
            
            return max(years) if years else 0
            
        except Exception as e:
            logger.error(f"Error extracting experience years: {e}")
            return 0
    
    def extract_contact_info(self, text: str, filename: str = "") -> Dict:
        """Extract comprehensive contact information with enhanced accuracy"""
        try:
            info = {}
            
            # Extract name with multiple strategies
            name = self._extract_name(text, filename)
            
            # Extract email
            email = self._extract_email(text)
            
            # Extract phone
            phone = self._extract_phone(text)
            
            # Extract address
            address = self._extract_address(text)
            
            # Extract skills
            skills = self.extract_skills(text)
            
            # Extract experience
            experience_years = self.extract_experience_years(text)
            
            # Extract education
            education = self._extract_education(text)
            
            # Extract certifications
            certifications = self._extract_certifications(text)
            
            # Extract languages
            languages = self._extract_languages(text)
            
            # Extract social links
            social_links = self._extract_social_links(text)
            
            info.update({
                'name': name,
                'email': email,
                'phone': phone,
                'address': address,
                'skills': skills,
                'experience_years': experience_years,
                'education': education,
                'certifications': certifications,
                'languages': languages,
                'social_links': social_links,
                'extraction_timestamp': datetime.now().isoformat()
            })
            
            return info
            
        except Exception as e:
            logger.error(f"Error extracting contact info: {e}")
            return {
                'name': None,
                'email': None,
                'phone': None,
                'address': None,
                'skills': [],
                'experience_years': 0,
                'education': [],
                'certifications': [],
                'languages': [],
                'social_links': {},
                'extraction_timestamp': datetime.now().isoformat()
            }
    
    def _extract_name(self, text: str, filename: str) -> Optional[str]:
        """Extract candidate name with multiple strategies"""
        try:
            lines = text.strip().splitlines()
            
            # Strategy 1: First line (most common)
            if lines:
                name_line = lines[0]
                name = re.sub(r'[^a-zA-Z\s]', '', name_line).strip()
                if self._is_valid_name(name):
                    return name.title()
            
            # Strategy 2: Second line
            if len(lines) > 1:
                name = re.sub(r'[^a-zA-Z\s]', '', lines[1]).strip()
                if self._is_valid_name(name):
                    return name.title()
            
            # Strategy 3: Look for name patterns
            name_patterns = [
                r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
                r'Name\s*[:.]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*[-|]\s*(?:Resume|CV)'
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, text)
                if match:
                    name = match.group(1).strip()
                    if self._is_valid_name(name):
                        return name.title()
            
            # Strategy 4: Use filename
            if filename:
                name = filename.replace("_", " ").replace("-", " ").split(".")[0]
                if self._is_valid_name(name):
                    return name.title()
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting name: {e}")
            return None
    
    def _is_valid_name(self, name: str) -> bool:
        """Validate if extracted text is a valid name"""
        if not name or len(name) < 3:
            return False
        
        # Check if it contains only letters and spaces
        if not re.match(r'^[A-Za-z\s]+$', name):
            return False
        
        # Check if it has at least one word with 2+ characters
        words = name.split()
        if not any(len(word) >= 2 for word in words):
            return False
        
        # Check if it's not too long (more than 4 words)
        if len(words) > 4:
            return False
        
        return True
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address with enhanced validation"""
        try:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_matches = re.findall(email_pattern, text)
            
            for email in email_matches:
                # Additional validation
                if len(email) <= 254 and '@' in email and '.' in email.split('@')[1]:
                    return email.lower()
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting email: {e}")
            return None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number with international support"""
        try:
            for pattern in self.phone_patterns:
                phone_match = re.search(pattern, text)
                if phone_match:
                    phone = phone_match.group()
                    # Clean up the phone number
                    phone = re.sub(r'[^\d+]', '', phone)
                    return phone
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting phone: {e}")
            return None
    
    def _extract_address(self, text: str) -> Optional[str]:
        """Extract address using NER and pattern matching"""
        try:
            address_chunks = []
            
            # Use spaCy NER for location extraction
            if hasattr(self.nlp, 'pipe_names') and 'ner' in self.nlp.pipe_names:
                doc = self.nlp(text)
                for ent in doc.ents:
                    if ent.label_ in ['GPE', 'LOC']:
                        ent_text = ent.text.strip()
                        if (len(ent_text.split()) <= 4 and 
                            len(ent_text) > 2 and
                            ent_text.lower() not in [skill.lower() for skill in self.skill_keywords]):
                            address_chunks.append(ent_text)
            
            # Extract pincode/postal code
            pincode_patterns = [
                r'\b[1-9]\d{5}\b',  # Indian pincode
                r'\b\d{5}(?:-\d{4})?\b',  # US ZIP code
                r'\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b',  # Canadian postal code
            ]
            
            for pattern in pincode_patterns:
                match = re.search(pattern, text)
                if match:
                    address_chunks.append(match.group())
            
            # Remove duplicates while preserving order
            seen = set()
            unique_chunks = []
            for chunk in address_chunks:
                if chunk.lower() not in seen:
                    seen.add(chunk.lower())
                    unique_chunks.append(chunk)
            
            return ', '.join(unique_chunks) if unique_chunks else None
            
        except Exception as e:
            logger.error(f"Error extracting address: {e}")
            return None
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        try:
            education = []
            education_keywords = [
                'bachelor', 'master', 'phd', 'doctorate', 'diploma', 'certificate',
                'b.tech', 'm.tech', 'b.e', 'm.e', 'b.sc', 'm.sc', 'mba', 'bca', 'mca'
            ]
            
            lines = text.lower().split('\n')
            for line in lines:
                for keyword in education_keywords:
                    if keyword in line:
                        # Extract the full education line
                        education.append(line.strip().title())
                        break
            
            return list(set(education))
            
        except Exception as e:
            logger.error(f"Error extracting education: {e}")
            return []
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        try:
            certifications = []
            cert_keywords = [
                'certified', 'certification', 'certificate', 'aws', 'azure', 'gcp',
                'pmp', 'scrum', 'agile', 'cisco', 'microsoft', 'oracle', 'comptia'
            ]
            
            lines = text.lower().split('\n')
            for line in lines:
                for keyword in cert_keywords:
                    if keyword in line:
                        certifications.append(line.strip().title())
                        break
            
            return list(set(certifications))
            
        except Exception as e:
            logger.error(f"Error extracting certifications: {e}")
            return []
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract programming and spoken languages"""
        try:
            languages = []
            
            # Programming languages
            prog_languages = ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust']
            for lang in prog_languages:
                if lang in text.lower():
                    languages.append(lang.title())
            
            # Spoken languages
            spoken_languages = ['english', 'spanish', 'french', 'german', 'chinese', 'japanese', 'hindi']
            for lang in spoken_languages:
                if lang in text.lower():
                    languages.append(lang.title())
            
            return list(set(languages))
            
        except Exception as e:
            logger.error(f"Error extracting languages: {e}")
            return []
    
    def _extract_social_links(self, text: str) -> Dict[str, str]:
        """Extract social media and professional profile links"""
        try:
            social_links = {}
            
            # LinkedIn
            linkedin_pattern = r'linkedin\.com/in/[\w-]+'
            linkedin_match = re.search(linkedin_pattern, text)
            if linkedin_match:
                social_links['linkedin'] = linkedin_match.group()
            
            # GitHub
            github_pattern = r'github\.com/[\w-]+'
            github_match = re.search(github_pattern, text)
            if github_match:
                social_links['github'] = github_match.group()
            
            # Portfolio/Website
            website_pattern = r'https?://(?:www\.)?[\w-]+\.(?:com|org|net|io)'
            website_match = re.search(website_pattern, text)
            if website_match:
                social_links['website'] = website_match.group()
            
            return social_links
            
        except Exception as e:
            logger.error(f"Error extracting social links: {e}")
            return {}
    
    def get_extraction_summary(self, info: Dict) -> Dict:
        """Generate a summary of the extraction results"""
        try:
            summary = {
                'total_skills_found': len(info.get('skills', [])),
                'has_contact_info': bool(info.get('email') or info.get('phone')),
                'has_address': bool(info.get('address')),
                'experience_level': self._categorize_experience(info.get('experience_years', 0)),
                'education_count': len(info.get('education', [])),
                'certification_count': len(info.get('certifications', [])),
                'language_count': len(info.get('languages', [])),
                'social_profiles': len(info.get('social_links', {})),
                'extraction_quality': self._assess_extraction_quality(info)
            }
            return summary
            
        except Exception as e:
            logger.error(f"Error generating extraction summary: {e}")
            return {}
    
    def _categorize_experience(self, years: int) -> str:
        """Categorize experience level"""
        if years == 0:
            return "Entry Level"
        elif years <= 2:
            return "Junior"
        elif years <= 5:
            return "Mid Level"
        elif years <= 10:
            return "Senior"
        else:
            return "Expert"
    
    def _assess_extraction_quality(self, info: Dict) -> str:
        """Assess the quality of extraction"""
        score = 0
        
        if info.get('name'):
            score += 20
        if info.get('email'):
            score += 20
        if info.get('phone'):
            score += 15
        if info.get('address'):
            score += 10
        if info.get('skills'):
            score += 20
        if info.get('experience_years', 0) > 0:
            score += 15
        
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"

# Global instance for caching
_extractor_instance = None

def get_extractor() -> ResumeExtractor:
    """Get singleton instance of ResumeExtractor"""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = ResumeExtractor()
    return _extractor_instance

def extract_contact_info(text: str, filename: str = "") -> Dict:
    """Convenience function for backward compatibility"""
    extractor = get_extractor()
    return extractor.extract_contact_info(text, filename) 