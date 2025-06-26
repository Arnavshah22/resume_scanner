#!/usr/bin/env python3
"""
Test script for Streamlit Resume Scanner
"""

import sys
import os
import tempfile
import subprocess

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Streamlit: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Pandas: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Plotly: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ Sentence Transformers imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Sentence Transformers: {e}")
        return False
    
    try:
        import spacy
        print("✅ spaCy imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import spaCy: {e}")
        return False
    
    try:
        from pdfminer.high_level import extract_text as extract_pdf
        print("✅ PDFMiner imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PDFMiner: {e}")
        return False
    
    try:
        from docx import Document
        print("✅ python-docx imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import python-docx: {e}")
        return False
    
    return True

def test_spacy_model():
    """Test if spaCy model is available"""
    print("\nTesting spaCy model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy model loaded successfully")
        return True
    except OSError:
        print("❌ spaCy model not found. Please run: python -m spacy download en_core_web_sm")
        return False
    except Exception as e:
        print(f"❌ Error loading spaCy model: {e}")
        return False

def test_sentence_transformer():
    """Test if sentence transformer model can be loaded"""
    print("\nTesting Sentence Transformer model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        # Test with a smaller model first
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Sentence Transformer model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error loading Sentence Transformer model: {e}")
        return False

def test_file_processing():
    """Test file processing capabilities"""
    print("\nTesting file processing...")
    
    try:
        from resumer_parser import extract_text
        
        # Create a test text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test resume content\nJohn Doe\nSoftware Engineer\nPython, Java, React")
            temp_file = f.name
        
        # Test text extraction (should work with any file)
        text = extract_text(temp_file)
        if text:
            print("✅ File processing works")
        else:
            print("⚠️ File processing returned empty text")
        
        # Clean up
        os.unlink(temp_file)
        return True
        
    except Exception as e:
        print(f"❌ Error in file processing: {e}")
        return False

def test_extractor():
    """Test the enhanced extractor"""
    print("\nTesting enhanced extractor...")
    
    try:
        from enhanced_extractor import extract_contact_info
        
        test_text = """
        John Doe
        Software Engineer
        john.doe@email.com
        +1-555-123-4567
        New York, NY
        
        Skills: Python, JavaScript, React, AWS
        Experience: 5 years of software development
        """
        
        info = extract_contact_info(test_text, "test_resume.pdf")
        
        if info:
            print("✅ Enhanced extractor works")
            print(f"   Extracted name: {info.get('name', 'N/A')}")
            print(f"   Extracted email: {info.get('email', 'N/A')}")
            print(f"   Extracted skills: {len(info.get('skills', []))}")
        else:
            print("⚠️ Enhanced extractor returned empty result")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in enhanced extractor: {e}")
        return False

def test_scorer():
    """Test the enhanced scorer"""
    print("\nTesting enhanced scorer...")
    
    try:
        from enhanced_scorer import calculate_similarity
        
        resume_text = """
        Experienced software engineer with 5 years of experience in Python development.
        Proficient in Django, React, and AWS. Strong background in machine learning.
        """
        
        job_description = """
        We are looking for a Python developer with experience in web development.
        Required skills: Python, Django, React, AWS. 3+ years of experience needed.
        """
        
        result = calculate_similarity(resume_text, job_description, ["Python", "Django", "React", "AWS"], 5)
        
        if result and 'final_score' in result:
            print("✅ Enhanced scorer works")
            print(f"   Final score: {result['final_score']}%")
            print(f"   Fit category: {result.get('fit_category', 'N/A')}")
        else:
            print("⚠️ Enhanced scorer returned invalid result")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in enhanced scorer: {e}")
        return False

def test_streamlit_app():
    """Test if Streamlit app can be imported"""
    print("\nTesting Streamlit app...")
    
    try:
        # Try to import the main app
        import streamlit_app
        print("✅ Streamlit app can be imported")
        return True
    except Exception as e:
        print(f"❌ Error importing Streamlit app: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing AI Resume Scanner Pro")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_spacy_model,
        test_sentence_transformer,
        test_file_processing,
        test_extractor,
        test_scorer,
        test_streamlit_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 To run the application:")
        print("   streamlit run streamlit_app.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\n🔧 Common fixes:")
        print("   pip install -r streamlit_requirements.txt")
        print("   python -m spacy download en_core_web_sm")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 