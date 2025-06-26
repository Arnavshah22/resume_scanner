#!/usr/bin/env python3
"""
Test script to verify the streamlit app components are working
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import streamlit: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pandas: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ plotly imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import plotly: {e}")
        return False
    
    try:
        # Try importing resumer_parser
        import resumer_parser
        print("✅ resumer_parser imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import resumer_parser: {e}")
        return False
    
    try:
        from enhanced_scorer import ResumeScorer
        print("✅ enhanced_scorer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import enhanced_scorer: {e}")
        return False
    
    try:
        from extractor import extract_contact_info
        print("✅ extractor imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import extractor: {e}")
        return False
    
    return True

def test_scorer_initialization():
    """Test if the ResumeScorer can be initialized"""
    print("\nTesting ResumeScorer initialization...")
    
    try:
        from enhanced_scorer import ResumeScorer
        scorer = ResumeScorer()
        print("✅ ResumeScorer initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize ResumeScorer: {e}")
        return False

def test_sample_scoring():
    """Test if scoring works with sample data"""
    print("\nTesting sample scoring...")
    
    try:
        from enhanced_scorer import ResumeScorer
        
        scorer = ResumeScorer()
        
        # Sample data
        resume_text = """
        John Doe
        Software Engineer with 5 years of experience in Python, Django, and React.
        Skills: Python, JavaScript, React, Django, SQL, Git
        Experience: 5 years
        Education: Bachelor's in Computer Science
        """
        
        job_description = """
        We are looking for a Python Software Engineer with 3+ years of experience.
        Required Skills: Python, Django/Flask, SQL, Git, REST APIs
        Responsibilities: Develop web applications, work with databases, collaborate with team
        Nice to have: React, AWS, Docker, Machine Learning
        """
        
        result = scorer.calculate_overall_score(
            resume_text=resume_text,
            job_description=job_description,
            resume_skills=["Python", "JavaScript", "React", "Django", "SQL", "Git"],
            experience_years=5,
            education=["Bachelor's in Computer Science"]
        )
        
        print(f"✅ Sample scoring completed successfully")
        print(f"   Final Score: {result.get('final_score', 'N/A')}")
        print(f"   Fit Category: {result.get('fit_category', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to perform sample scoring: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Streamlit App Components")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check your dependencies.")
        return False
    
    # Test scorer initialization
    if not test_scorer_initialization():
        print("\n❌ Scorer initialization failed.")
        return False
    
    # Test sample scoring
    if not test_sample_scoring():
        print("\n❌ Sample scoring failed.")
        return False
    
    print("\n🎉 All tests passed! The streamlit app should work correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 