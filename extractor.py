import re
import spacy

# Load English model for NER
nlp = spacy.load("en_core_web_sm")

# Skill keywords to detect from resume
SKILL_KEYWORDS = {
    'python', 'laravel', 'php'
}

# Words that look like locations but are actually tech or irrelevant
FALSE_ADDRESS_TERMS = {
    'ai', 'ml', 'ananta', 'express.js', 'node.js', 'react', 'next.js', 'postgresql'
}


def extract_experience_years(text):
    """
    Extracts the highest number of years of experience mentioned in the resume.
    Matches formats like: '3+ years', '5 years of experience', etc.
    """
    matches = re.findall(r'(\d+)\+?\s*(?:years|yrs)\s*(?:of)?\s*(?:experience|exp)?', text.lower())
    years = [int(m) for m in matches]
    return max(years) if years else 0


def extract_contact_info(text, filename=""):
    info = {}

    lower_text = text.lower()
    found_skills = [kw for kw in SKILL_KEYWORDS if kw.lower() in lower_text]
    found_skills_set = set([s.lower() for s in found_skills])

    # Extract name
    lines = text.strip().splitlines()
    name_line = lines[0] if lines else ''
    name = re.sub(r'[^a-zA-Z\s]', '', name_line).strip()
    if not name or len(name.split()) < 1:
        name = filename.replace("_", " ").split(".")[0]

    # Extract email
    email_match = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    email = email_match[0] if email_match else None

    # Extract phone
    phone_match = re.findall(r'\+?\d[\d\s\-()]{8,15}', text)
    phone = phone_match[0] if phone_match else None

    # Extract address using NER
    doc = nlp(text)
    address_chunks = []
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC']:
            ent_text = ent.text.strip()
            if ent_text.lower() not in found_skills_set and ent_text.lower() not in FALSE_ADDRESS_TERMS:
                if len(ent_text.split()) <= 4:
                    address_chunks.append(ent_text)

    # Pincode (Indian)
    pincode_match = re.search(r'\b\d{6}\b', text)
    if pincode_match:
        address_chunks.append(pincode_match.group())

    address = ', '.join(sorted(set(address_chunks), key=address_chunks.index)) if address_chunks else None

    # Extract experience
    experience_years = extract_experience_years(text)

    # Final structured output
    info.update({
        'name': name,
        'email': email,
        'phone': phone,
        'skills': sorted(set(found_skills)),
        'address': address,
        'experience_years': experience_years
    })

    return info
