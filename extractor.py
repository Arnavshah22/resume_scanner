import re
import spacy
import os
import subprocess
import sys

def load_spacy_model():
    """Load spaCy model with fallback handling for deployment."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        print("Model 'en_core_web_sm' not found. Attempting to download...")
        try:
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            return spacy.load("en_core_web_sm")
        except (subprocess.CalledProcessError, OSError):
            print("Warning: Using blank English model. Some NER features may be limited.")
            return spacy.blank("en")

# Load English model for NER
nlp = load_spacy_model()

# Skill keywords to detect from resume
SKILL_KEYWORDS = {
    'python', 'laravel', 'php', 'javascript', 'java', 'c++', 'c#', 'ruby', 'go', 
    'rust', 'swift', 'kotlin', 'typescript', 'html', 'css', 'sass', 'scss',
    'react', 'angular', 'vue', 'node.js', 'express.js', 'next.js', 'nuxt.js',
    'django', 'flask', 'fastapi', 'spring', 'laravel', 'symfony', 'rails',
    'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'sql server',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github',
    'machine learning', 'ml', 'ai', 'data science', 'tensorflow', 'pytorch',
    'pandas', 'numpy', 'scikit-learn', 'opencv', 'nlp', 'deep learning'
}

# Words that look like locations but are actually tech or irrelevant
FALSE_ADDRESS_TERMS = {
    'ai', 'ml', 'ananta', 'express.js', 'node.js', 'react', 'next.js', 'postgresql',
    'mysql', 'mongodb', 'redis', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
    'python', 'java', 'javascript', 'typescript', 'html', 'css', 'php', 'laravel',
    'django', 'flask', 'spring', 'angular', 'vue', 'github', 'git', 'api', 'rest',
    'graphql', 'sql', 'nosql', 'ci/cd', 'devops', 'agile', 'scrum', 'tensorflow',
    'pytorch', 'pandas', 'numpy', 'opencv', 'nlp', 'sass', 'scss', 'webpack'
}

def extract_experience_years(text):
    """
    Extracts the highest number of years of experience mentioned in the resume.
    Matches formats like: '3+ years', '5 years of experience', etc.
    """
    # Enhanced regex patterns for experience
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp|work)',
        r'(\d+)\+?\s*(?:year|yr)\s*(?:experience|exp)',
        r'experience\s*[:.]?\s*(\d+)\+?\s*(?:years?|yrs?)',
        r'(\d+)\+?\s*(?:years?|yrs?)\s*in\s*(?:software|development|programming|coding)',
    ]
    
    years = []
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        years.extend([int(m) for m in matches])
    
    return max(years) if years else 0

def extract_contact_info(text, filename=""):
    """Extract comprehensive contact information from resume text."""
    info = {}
    
    lower_text = text.lower()
    found_skills = [kw for kw in SKILL_KEYWORDS if kw.lower() in lower_text]
    found_skills_set = set([s.lower() for s in found_skills])
    
    # Extract name (improved logic)
    lines = text.strip().splitlines()
    name_line = lines[0] if lines else ''
    
    # Clean the name line and extract name
    name = re.sub(r'[^a-zA-Z\s]', '', name_line).strip()
    
    # If name is too short or empty, try second line or filename
    if not name or len(name.split()) < 1 or len(name) < 3:
        if len(lines) > 1:
            name = re.sub(r'[^a-zA-Z\s]', '', lines[1]).strip()
        if not name or len(name) < 3:
            name = filename.replace("_", " ").replace("-", " ").split(".")[0]
    
    # Extract email (improved regex)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.findall(email_pattern, text)
    email = email_match[0] if email_match else None
    
    # Extract phone (improved patterns for Indian and international numbers)
    phone_patterns = [
        r'\+91[\s-]?\d{10}',  # Indian format with +91
        r'\b\d{10}\b',        # 10-digit number
        r'\+\d{1,3}[\s-]?\d{8,15}',  # International format
        r'\(\d{3}\)[\s-]?\d{3}[\s-]?\d{4}',  # US format
    ]
    
    phone = None
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            phone = phone_match.group()
            break
    
    # Extract address using NER (only if spaCy model is properly loaded)
    address_chunks = []
    if hasattr(nlp, 'pipe_names') and 'ner' in nlp.pipe_names:
        try:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['GPE', 'LOC']:
                    ent_text = ent.text.strip()
                    if (ent_text.lower() not in found_skills_set and 
                        ent_text.lower() not in FALSE_ADDRESS_TERMS and
                        len(ent_text.split()) <= 4 and
                        len(ent_text) > 2):
                        address_chunks.append(ent_text)
        except Exception as e:
            print(f"NER processing failed: {e}")
    
    # Pincode (Indian) - improved pattern
    pincode_match = re.search(r'\b[1-9]\d{5}\b', text)
    if pincode_match:
        address_chunks.append(pincode_match.group())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_address_chunks = []
    for chunk in address_chunks:
        if chunk.lower() not in seen:
            seen.add(chunk.lower())
            unique_address_chunks.append(chunk)
    
    address = ', '.join(unique_address_chunks) if unique_address_chunks else None
    
    # Extract experience
    experience_years = extract_experience_years(text)
    
    # Final structured output
    info.update({
        'name': name.title() if name else None,
        'email': email,
        'phone': phone,
        'skills': sorted(set([skill.title() for skill in found_skills])),
        'address': address,
        'experience_years': experience_years
    })
    
    return info