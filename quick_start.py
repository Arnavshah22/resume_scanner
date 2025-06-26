#!/usr/bin/env python3
"""
Quick Start Script for AI Resume Scanner Pro
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print application banner"""
    print("🎯" + "="*60 + "🎯")
    print("           AI Resume Scanner Pro - Quick Start")
    print("🎯" + "="*60 + "🎯")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ required.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install from requirements file
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "streamlit_requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def download_spacy_model():
    """Download spaCy model"""
    print("\n🤖 Downloading spaCy model...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("✅ spaCy model downloaded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download spaCy model: {e}")
        return False

def run_tests():
    """Run basic tests"""
    print("\n🧪 Running basic tests...")
    
    try:
        subprocess.check_call([sys.executable, "test_streamlit.py"])
        print("✅ All tests passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Some tests failed: {e}")
        return False

def start_application():
    """Start the Streamlit application"""
    print("\n🚀 Starting AI Resume Scanner Pro...")
    print("📱 The application will open in your browser")
    print("🔗 Local URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the application")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

def show_manual_instructions():
    """Show manual installation instructions"""
    print("\n📋 Manual Installation Instructions:")
    print("="*50)
    print("1. Install Python 3.8 or higher")
    print("2. Install dependencies:")
    print("   pip install -r streamlit_requirements.txt")
    print("3. Download spaCy model:")
    print("   python -m spacy download en_core_web_sm")
    print("4. Run the application:")
    print("   streamlit run streamlit_app.py")
    print("="*50)

def show_docker_instructions():
    """Show Docker instructions"""
    print("\n🐳 Docker Instructions:")
    print("="*30)
    print("1. Build the image:")
    print("   docker build -t resume-scanner .")
    print("2. Run the container:")
    print("   docker run -p 8501:8501 resume-scanner")
    print("3. Access at: http://localhost:8501")
    print("="*30)

def main():
    """Main quick start function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Please upgrade Python to version 3.8 or higher")
        show_manual_instructions()
        return
    
    # Check if requirements file exists
    if not os.path.exists("streamlit_requirements.txt"):
        print("❌ streamlit_requirements.txt not found")
        print("Please ensure you're in the correct directory")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        show_manual_instructions()
        return
    
    # Download spaCy model
    if not download_spacy_model():
        print("\n❌ Failed to download spaCy model")
        show_manual_instructions()
        return
    
    # Run tests
    if not run_tests():
        print("\n⚠️ Some tests failed, but continuing...")
    
    # Show deployment options
    print("\n🎯 Deployment Options:")
    print("1. Local Development (Recommended for testing)")
    print("2. Docker Deployment (Recommended for production)")
    print("3. Streamlit Cloud (Recommended for sharing)")
    
    choice = input("\nChoose deployment option (1-3) or press Enter for local: ").strip()
    
    if choice == "2":
        show_docker_instructions()
        return
    elif choice == "3":
        print("\n☁️ Streamlit Cloud Deployment:")
        print("1. Push your code to GitHub")
        print("2. Go to https://share.streamlit.io")
        print("3. Connect your repository")
        print("4. Set main file: streamlit_app.py")
        print("5. Deploy!")
        return
    else:
        # Start local application
        start_application()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        show_manual_instructions() 