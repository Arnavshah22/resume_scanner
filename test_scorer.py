#!/usr/bin/env python3
"""
Test script to verify the enhanced_scorer is working properly
"""

import sys
import os

def test_scorer():
    """Test the enhanced scorer with sample data"""
    print("🧪 Testing Enhanced Scorer")
    print("=" * 50)
    
    try:
        from enhanced_scorer import ResumeScorer
        
        # Initialize scorer
        print("Initializing ResumeScorer...")
        scorer = ResumeScorer()
        print("✅ ResumeScorer initialized successfully")
        
        # Sample data
        resume_text = """
        John Doe
        Software Engineer with 5 years of experience in Python, Django, and React.
        Skills: Python, JavaScript, React, Django, SQL, Git, AWS
        Experience: 5 years
        Education: Bachelor's in Computer Science
        """
        
        job_description = """
        We are looking for a Python Software Engineer with 3+ years of experience.
        Required Skills: Python, Django/Flask, SQL, Git, REST APIs
        Responsibilities: Develop web applications, work with databases, collaborate with team
        Nice to have: React, AWS, Docker, Machine Learning
        """
        
        print("\nTesting semantic score calculation...")
        semantic_score = scorer.calculate_semantic_score(resume_text, job_description)
        print(f"✅ Semantic Score: {semantic_score}")
        
        print("\nTesting skill score calculation...")
        skill_analysis = scorer.calculate_skill_score(
            ["Python", "JavaScript", "React", "Django", "SQL", "Git", "AWS"], 
            job_description
        )
        print(f"✅ Skill Score: {skill_analysis['score']}")
        print(f"   Matched Skills: {skill_analysis['matched_skills']}")
        print(f"   Missing Skills: {skill_analysis['missing_skills']}")
        
        print("\nTesting overall score calculation...")
        result = scorer.calculate_overall_score(
            resume_text=resume_text,
            job_description=job_description,
            resume_skills=["Python", "JavaScript", "React", "Django", "SQL", "Git", "AWS"],
            experience_years=5,
            education=["Bachelor's in Computer Science"]
        )
        
        print(f"✅ Overall Score: {result.get('final_score', 'N/A')}")
        print(f"   Fit Category: {result.get('fit_category', 'N/A')}")
        print(f"   Semantic Score: {result.get('semantic_score', 'N/A')}")
        print(f"   Skill Score: {result.get('skill_score', 'N/A')}")
        print(f"   Experience Score: {result.get('experience_score', 'N/A')}")
        print(f"   Education Score: {result.get('education_score', 'N/A')}")
        
        # Check if scores are reasonable
        if result.get('semantic_score', 0) > 0:
            print("✅ Semantic score is working correctly!")
        else:
            print("❌ Semantic score is 0 - there might be an issue with the model")
            
        if result.get('final_score', 0) > 0:
            print("✅ Overall scoring is working correctly!")
        else:
            print("❌ Overall score is 0 - there might be an issue with the scoring")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing scorer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scorer()
    sys.exit(0 if success else 1) 