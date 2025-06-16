from sentence_transformers import SentenceTransformer, util

# Load top-tier semantic embedding model
model = SentenceTransformer('BAAI/bge-large-en-v1.5')

# Define your required skills (or pass them dynamically later)
JD_SKILLS = {'python', 'laravel', 'php'}

# Set required years of experience
REQUIRED_EXPERIENCE = 3


def calculate_semantic_score(resume_text, job_description):
    resume_embed = model.encode("Represent this sentence for matching: " + resume_text, convert_to_tensor=True)
    jd_embed = model.encode("Represent this sentence for matching: " + job_description, convert_to_tensor=True)

    similarity = util.cos_sim(resume_embed, jd_embed).item()
    return round(similarity * 100, 2)


def calculate_skill_score(resume_skills, jd_skills=JD_SKILLS):
    matched = [skill for skill in resume_skills if skill.lower() in jd_skills]
    if not jd_skills:
        return 0
    return round(len(matched) / len(jd_skills) * 100, 2)


def calculate_experience_score(experience_years, required_years=REQUIRED_EXPERIENCE):
    return min(100, round((experience_years / required_years) * 100, 2))


def calculate_similarity(resume_text, job_description, resume_skills=[], experience_years=0):
    semantic_score = calculate_semantic_score(resume_text, job_description)
    skill_score = calculate_skill_score(resume_skills)
    experience_score = calculate_experience_score(experience_years)

    final_score = round(
        0.6 * semantic_score +
        0.25 * skill_score +
        0.15 * experience_score,
        2
    )

    return {
        "final_score": final_score,
        "semantic_score": semantic_score,
        "skill_score": skill_score,
        "experience_score": experience_score
    }
