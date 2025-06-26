#!/usr/bin/env python3
"""
Test script for AI Summary Generator
Tests both OpenRouter and Groq API integrations
"""

import os
import sys
from ai_summary_generator import AISummaryGenerator, get_summary_generator

def test_ai_summary():
    """Test AI summary generation with sample data"""
    
    print("🤖 Testing AI Summary Generator...")
    
    # Sample data
    resume_text = """
    John Doe
    Software Engineer
    john.doe@email.com
    
    EXPERIENCE:
    Senior Software Engineer at TechCorp (2020-2023)
    - Developed full-stack web applications using React, Node.js, and Python
    - Led a team of 5 developers on multiple projects
    - Implemented CI/CD pipelines and automated testing
    
    Software Engineer at StartupXYZ (2018-2020)
    - Built REST APIs and microservices
    - Worked with AWS cloud services
    - Collaborated with cross-functional teams
    """
    
    job_description = """
    Senior Software Engineer Position
    
    We are looking for a Senior Software Engineer to join our growing team.
    
    Requirements:
    - 5+ years of experience in software development
    - Proficiency in Python, JavaScript, and React
    - Experience with cloud platforms (AWS, Azure, or GCP)
    - Knowledge of CI/CD practices
    - Strong problem-solving skills
    - Team leadership experience
    
    Nice to have:
    - Experience with microservices architecture
    - Knowledge of Docker and Kubernetes
    - Agile development methodologies
    """
    
    score_breakdown = {
        'final_score': 85,
        'semantic_score': 88,
        'skill_score': 92,
        'experience_score': 75,
        'skill_analysis': {
            'matched_skills': ['Python', 'JavaScript', 'React', 'AWS', 'CI/CD'],
            'missing_skills': ['Kubernetes', 'Docker'],
            'extra_skills': ['Node.js', 'Microservices']
        },
        'experience_analysis': {
            'required_years': 5,
            'candidate_years': 5,
            'experience_gap': 0
        }
    }
    
    candidate_info = {
        'name': 'John Doe',
        'experience_years': 5,
        'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'CI/CD', 'Microservices']
    }
    
    # Test OpenRouter
    print("\n📡 Testing OpenRouter Integration...")
    openrouter_generator = AISummaryGenerator(provider="openrouter")
    
    if openrouter_generator.enabled:
        try:
            summary = openrouter_generator.generate_summary(
                resume_text, job_description, score_breakdown, candidate_info
            )
            print("✅ OpenRouter Summary Generated:")
            print("-" * 50)
            print(summary)
            print("-" * 50)
        except Exception as e:
            print(f"❌ OpenRouter Error: {e}")
    else:
        print("⚠️ OpenRouter disabled (no API key)")
    
    # Test Groq
    print("\n📡 Testing Groq Integration...")
    groq_generator = AISummaryGenerator(provider="groq")
    
    if groq_generator.enabled:
        try:
            summary = groq_generator.generate_summary(
                resume_text, job_description, score_breakdown, candidate_info
            )
            print("✅ Groq Summary Generated:")
            print("-" * 50)
            print(summary)
            print("-" * 50)
        except Exception as e:
            print(f"❌ Groq Error: {e}")
    else:
        print("⚠️ Groq disabled (no API key)")
    
    # Test fallback
    print("\n📝 Testing Fallback Summary...")
    fallback_generator = AISummaryGenerator(provider="nonexistent")
    summary = fallback_generator.generate_summary(
        resume_text, job_description, score_breakdown, candidate_info
    )
    print("✅ Fallback Summary Generated:")
    print("-" * 50)
    print(summary)
    print("-" * 50)
    
    # Test singleton
    print("\n🔄 Testing Singleton Pattern...")
    generator1 = get_summary_generator()
    generator2 = get_summary_generator()
    print(f"Same instance: {generator1 is generator2}")

if __name__ == "__main__":
    test_ai_summary() 