import streamlit as st
import os
import tempfile
import logging
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json

# Import your existing modules
from resumer_parser import extract_text
from enhanced_scorer import ResumeScorer, calculate_similarity
from extractor import extract_contact_info
from ai_summary_generator import get_summary_generator

# Initialize the enhanced scorer with caching
@st.cache_resource
def get_scorer():
    """Get cached scorer instance"""
    return ResumeScorer()

scorer = get_scorer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration with modern theme
st.set_page_config(
    page_title="ResumeScan AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium UI
st.markdown("""
<style>
    :root {
        --primary: #6366f1;
        --primary-light: #818cf8;
        --secondary: #8b5cf6;
        --accent: #ec4899;
        --dark: #1e293b;
        --light: #f8fafc;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }
    
    /* Main Container */
    .main {
        background: linear-gradient(135deg, #f0f4f8 0%, #e6eef7 100%);
        color: var(--dark);
    }
    
    /* Glassmorphism Effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.15);
        border-color: rgba(255, 255, 255, 0.6);
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .main-header:before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.7);
        padding: 1.8rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        border: 1px solid rgba(99, 102, 241, 0.1);
        transition: all 0.3s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(to bottom, var(--primary), var(--accent));
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    
    /* Skill Badges */
    .skill-badge {
        background: rgba(99, 102, 241, 0.1);
        color: var(--primary);
        padding: 0.5rem 1.2rem;
        border-radius: 20px;
        margin: 0.3rem;
        display: inline-flex;
        align-items: center;
        font-size: 0.85rem;
        font-weight: 500;
        border: 1px solid rgba(99, 102, 241, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .skill-badge:before {
        content: '✓';
        margin-right: 0.5rem;
        font-size: 0.7rem;
        color: var(--success);
    }
    
    .skill-badge:hover {
        background: rgba(99, 102, 241, 0.15);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
    }
    
    /* Score Indicators */
    .score-high { 
        color: var(--success);
        font-weight: 700;
        position: relative;
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        background: rgba(16, 185, 129, 0.1);
    }
    
    .score-medium { 
        color: var(--warning);
        font-weight: 700;
        position: relative;
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        background: rgba(245, 158, 11, 0.1);
    }
    
    .score-low { 
        color: var(--danger);
        font-weight: 700;
        position: relative;
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        background: rgba(239, 68, 68, 0.1);
    }
    
    /* Progress Bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary), var(--accent));
        border-radius: 10px;
    }
    
    /* Buttons */
    .stButton > button {
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        z-index: 1;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.4);
        color: white;
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    .stButton > button:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 0;
        height: 100%;
        background: linear-gradient(135deg, var(--secondary), var(--accent));
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: -1;
    }
    
    .stButton > button:hover:before {
        width: 100%;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
        backdrop-filter: blur(16px) saturate(180%);
        border-right: 1px solid rgba(0, 0, 0, 0.05);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05);
        padding: 0 !important;
        min-width: 280px !important;
    }
    
    .stSidebar .sidebar-content {
        background: transparent !important;
        padding: 0 !important;
    }
    
    /* Sidebar header */
    .sidebar-header {
        text-align: center;
        margin: 0 0 1.5rem 0;
        padding: 2rem 1.5rem 1.5rem;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .sidebar-header h1 {
        font-size: 1.8rem !important;
        margin: 0 0 0.25rem 0 !important;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: white !important;
    }
    
    .sidebar-header p {
        opacity: 0.9;
        margin: 0;
        font-size: 0.9rem;
        font-weight: 400;
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* Navigation Items */
    .nav-item {
        padding: 0.8rem 1.5rem;
        margin: 0.25rem 0.5rem;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        color: #4b5563;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    
    .nav-item:hover {
        background: rgba(99, 102, 241, 0.1);
        color: var(--primary);
        transform: translateX(5px);
    }
    
    .nav-item.active {
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
        color: var(--primary);
        font-weight: 600;
        border-left: 4px solid var(--primary);
        border-radius: 0 12px 12px 0;
        margin-left: 0;
        box-shadow: none;
    }
    
    .nav-item span:first-child {
        font-size: 1.2rem;
        width: 24px;
        text-align: center;
    }
    
    /* Footer */
    .sidebar-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1.5rem;
        text-align: center;
        color: #6b7280;
        font-size: 0.8rem;
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(0, 0, 0, 0.05);
        z-index: 1000;
    }
    
    .sidebar-footer p {
        margin: 0.25rem 0;
        line-height: 1.4;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        margin-bottom: 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        margin: 0 0.3rem;
        transition: all 0.3s ease;
        font-weight: 500;
        color: var(--dark);
        border: 1px solid rgba(99, 102, 241, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        border: none;
    }
    
    /* File Uploader */
    .stFileUploader {
        border: 2px dashed rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: var(--primary);
        background: rgba(99, 102, 241, 0.05);
    }
    
    /* Text Areas */
    .stTextArea textarea {
        border-radius: 12px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }
    
    /* Expanders */
    .stExpander {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
        border: 1px solid rgba(99, 102, 241, 0.1);
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .stExpander label {
        font-weight: 600;
        color: var(--primary);
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99, 102, 241, 0.5);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_sample_job_descriptions():
    """Load sample job descriptions for demo purposes"""
    return {
        "Software Engineer (Python)": """
        We are looking for a Python Software Engineer with 3+ years of experience.
        Required Skills: Python, Django/Flask, SQL, Git, REST APIs
        Responsibilities: Develop web applications, work with databases, collaborate with team
        Nice to have: React, AWS, Docker, Machine Learning
        """,
        "Data Scientist": """
        Seeking a Data Scientist with strong analytical skills and ML experience.
        Required Skills: Python, Pandas, NumPy, Scikit-learn, SQL, Statistics
        Responsibilities: Build ML models, analyze data, create visualizations
        Nice to have: TensorFlow, PyTorch, AWS, Big Data tools
        """,
        "Full Stack Developer": """
        Full Stack Developer needed for modern web applications.
        Required Skills: JavaScript, React, Node.js, HTML/CSS, SQL, Git
        Responsibilities: Build frontend and backend, deploy applications
        Nice to have: TypeScript, AWS, Docker, CI/CD
        """
    }

@st.cache_resource
def initialize_session_state():
    """Initialize session state variables"""
    if 'scan_history' not in st.session_state:
        st.session_state.scan_history = []
    if 'current_scan' not in st.session_state:
        st.session_state.current_scan = None

def save_scan_result(result, filename, job_description):
    """Save scan result to session state"""
    scan_data = {
        'timestamp': datetime.now().isoformat(),
        'filename': filename,
        'job_description': job_description,
        'result': result
    }
    st.session_state.scan_history.append(scan_data)
    st.session_state.current_scan = scan_data

def process_resume(uploaded_file, job_description):
    """Process uploaded resume and return results"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        # Single spinner for all processing
        with st.spinner("🚀 Analyzing your resume..."):
            # Extract text
            resume_text = extract_text(tmp_path)
            if not resume_text:
                st.error("Failed to extract text from the uploaded file.")
                return None

            # Extract contact info
            contact_info = extract_contact_info(resume_text, uploaded_file.name)

            # Calculate similarity score using enhanced scorer
            try:
                score_breakdown = scorer.calculate_overall_score(
                    resume_text=resume_text,
                    job_description=job_description,
                    resume_skills=contact_info.get("skills", []),
                    experience_years=contact_info.get("experience_years", 0),
                    education=contact_info.get("education", [])
                )
                
            except Exception as e:
                st.error(f"Error in scoring: {str(e)}")
                logger.error(f"Scoring error: {str(e)}")
                return None

        # Generate AI-powered summary
        try:
            summary_generator = get_summary_generator()
            ai_summary = summary_generator.generate_summary(
                resume_text=resume_text,
                job_description=job_description,
                score_breakdown=score_breakdown,
                candidate_info=contact_info
            )
        except Exception as e:
            logger.warning(f"AI summary generation failed: {e}")
            # Fallback to basic summary
            ai_summary = " ".join(score_breakdown.get("recommendations", [])[:2]) if score_breakdown.get("recommendations") else "No specific recommendations available."

        # Get results from score breakdown
        final_score = score_breakdown.get("final_score", 0)
        fit = score_breakdown.get("fit_category", "Unknown")
        
        # Set fit color based on score
        if final_score >= 75:
            fit_color = "score-high"
        elif final_score >= 50:
            fit_color = "score-medium"
        else:
            fit_color = "score-low"

        # Clean up temporary file
        os.unlink(tmp_path)

        result = {
            'match_score': final_score,
            'fit': fit,
            'fit_color': fit_color,
            'summary': ai_summary,
            'candidate_info': contact_info,
            'score_breakdown': score_breakdown,
            'resume_text': resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
        }
        
        return result

    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        st.error(f"An error occurred while processing the resume: {str(e)}")
        return None

def display_results(result):
    """Display scan results in a modern, interactive format"""
    if not result:
        st.error("No results to display. Please try analyzing a resume again.")
        return
    if not isinstance(result, dict):
        st.error("Result data is corrupted or invalid. Please re-upload your resume and try again.")
        return
    
    # Extract data with proper error handling
    match_score = result.get('match_score', 0)
    fit = result.get('fit', 'Unknown')
    candidate = result.get('candidate_info', {})
    score_breakdown = result.get('score_breakdown', {})
    
    # Determine color based on match score
    if match_score >= 80:
        score_color = "#10b981"  # Green for high scores
        gradient_start = "#10b981"
        gradient_end = "#34d399"
    elif match_score >= 50:
        score_color = "#f59e0b"  # Yellow for medium scores
        gradient_start = "#f59e0b"
        gradient_end = "#fbbf24"
    else:
        score_color = "#ef4444"  # Red for low scores
        gradient_start = "#ef4444"
        gradient_end = "#f87171"
    
    # Main results header with enhanced score display
    st.markdown(f"""
    <div class="glass-card" style="
        padding: 2.5rem; 
        margin-bottom: 2rem; 
        text-align: center;
        background: linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0.6) 100%);
        border: 1px solid rgba(255,255,255,0.4);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        border-radius: 20px;
    ">
        <h1 style="
            margin: 0 0 1.5rem 0; 
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, {gradient_start}, {gradient_end});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">
            Resume Analysis Complete
        </h1>
        <div style="
            width: 180px;
            height: 180px;
            margin: 0 auto 1.5rem auto;
            border-radius: 50%;
            background: conic-gradient(
                {gradient_start} 0% {match_score}%,
                #f1f5f9 {match_score}% 100%
            );
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        ">
            <div style="
                width: 160px;
                height: 160px;
                background: white;
                border-radius: 50%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                box-shadow: inset 0 0 15px rgba(0,0,0,0.05);
                transition: all 0.3s ease;
            ">
                <span style="
                    font-size: 2.5rem; 
                    font-weight: 800; 
                    background: linear-gradient(135deg, {gradient_start}, {gradient_end});
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin-bottom: 0.5rem;
                ">
                    {match_score}%
                </span>
                <span style="
                    font-size: 1rem; 
                    font-weight: 600; 
                    color: {score_color};
                    background: rgba(0,0,0,0.03);
                    padding: 0.25rem 1rem;
                    border-radius: 20px;
                ">
                    {fit}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Score breakdown with progress bars
    st.subheader("📈 Score Breakdown")
    semantic_score = score_breakdown.get('semantic_score', 0)
    skill_score = score_breakdown.get('skill_score', 0)
    experience_score = score_breakdown.get('experience_score', 0)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Semantic Match**")
        st.progress(semantic_score / 100)
        st.metric("Score", f"{semantic_score}%")
    with col2:
        st.markdown("**Skill Match**")
        st.progress(skill_score / 100)
        st.metric("Score", f"{skill_score}%")
    with col3:
        st.markdown("**Experience Match**")
        st.progress(experience_score / 100)
        st.metric("Score", f"{experience_score}%")

    # Experience details
    if 'experience_analysis' in score_breakdown and score_breakdown['experience_analysis']:
        exp = score_breakdown['experience_analysis']
        gap = exp.get('experience_gap', 0)
        gap_text = f"{abs(gap)} years {'over' if gap > 0 else 'under'}"
        st.subheader("📊 Experience Analysis")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Required Experience", f"{exp.get('required_years', 0)} years")
        with col2:
            st.metric("Your Experience", f"{exp.get('candidate_years', 0)} years")
        with col3:
            st.metric("Experience Gap", gap_text)

    # Candidate information
    st.subheader("👤 Candidate Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {candidate.get('name', 'N/A')}")
        st.write(f"**Email:** {candidate.get('email', 'N/A')}")
        st.write(f"**Phone:** {candidate.get('phone', 'N/A')}")
        st.write(f"**Experience:** {candidate.get('experience_years', 0)} years")
    with col2:
        st.write(f"**Location:** {candidate.get('address', 'N/A')}")
        st.write(f"**Skills Found:** {len(candidate.get('skills', []))}")

    # Skills visualization
    if candidate.get('skills'):
        st.subheader("🛠️ Skills Analysis")
        skills = candidate['skills']
        skills_df = pd.DataFrame({
            'Skill': skills,
            'Count': [1] * len(skills)
        })
        fig = px.bar(skills_df, x='Skill', y='Count', 
                    title="Skills Found in Resume",
                    color_discrete_sequence=['#667eea'])
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True, key=f"skills_chart_{datetime.now().timestamp()}")
        st.markdown("**Skills:**", unsafe_allow_html=True)
        st.markdown(
            ' '.join([
                f'<span class="skill-badge">{skill}</span>' for skill in skills
            ]),
            unsafe_allow_html=True
        )

    # Summary
    st.subheader("📝 Analysis Summary")
    summary = result.get('summary', 'No summary available.')
    st.info(summary)

    # Resume preview
    with st.expander("📄 Resume Text Preview"):
        resume_text = result.get('resume_text', 'No text extracted')
        st.text(resume_text)

def display_analytics():
    """Display analytics dashboard for multiple scans"""
    if not st.session_state.scan_history:
        st.info("No scan history available. Complete some scans to see analytics.")
        return

    st.subheader("📊 Analytics Dashboard")
    
    # Convert history to DataFrame
    df_data = []
    for scan in st.session_state.scan_history:
        try:
            result = scan.get('result', {})
            score_breakdown = result.get('score_breakdown', {})
            
            df_data.append({
                'Date': scan['timestamp'][:10] if isinstance(scan['timestamp'], str) else scan['timestamp'].strftime('%Y-%m-%d'),
                'Filename': scan['filename'],
                'Match Score': result.get('match_score', 0),
                'Fit': result.get('fit', 'Unknown'),
                'Semantic Score': score_breakdown.get('semantic_score', 0),
                'Skill Score': score_breakdown.get('skill_score', 0),
                'Experience Score': score_breakdown.get('experience_score', 0)
            })
        except Exception as e:
            logger.error(f"Error processing scan data: {e}")
            continue
    
    if not df_data:
        st.warning("No valid scan data available for analytics.")
        return
    
    df = pd.DataFrame(df_data)
    
    # Score trends
    col1, col2 = st.columns(2)
    with col1:
        if len(df) > 1:
            fig = px.line(df, x='Date', y='Match Score', 
                         title="Match Score Trends",
                         color_discrete_sequence=['#667eea'])
            st.plotly_chart(fig, use_container_width=True, key=f"match_score_trend_{datetime.now().timestamp()}")
        else:
            st.info("Need at least 2 scans to show trends.")
    
    with col2:
        if len(df) > 1:
            fig = px.scatter(df, x='Semantic Score', y='Skill Score', 
                            color='Match Score', size='Experience Score',
                            title="Score Correlation Analysis",
                            color_continuous_scale='viridis')
            st.plotly_chart(fig, use_container_width=True, key=f"score_correlation_{datetime.now().timestamp()}")
        else:
            st.info("Need at least 2 scans to show correlation analysis.")

    # Fit distribution
    if len(df) > 0:
        fit_counts = df['Fit'].value_counts()
        fig = px.pie(values=fit_counts.values, names=fit_counts.index,
                     title="Fit Distribution")
        st.plotly_chart(fig, use_container_width=True, key=f"fit_distribution_{datetime.now().timestamp()}")

    # Data table
    st.subheader("📋 Scan History")
    st.dataframe(df, use_container_width=True)

def main():
    """Main application function with enhanced UI"""
    initialize_session_state()
    
    # Custom sidebar with navigation
    with st.sidebar:
        # Sidebar header
        st.markdown("""
        <div class="sidebar-header">
            <h1>ResumeScan AI</h1>
            <p>Intelligent Resume Analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Set default page if not set
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'scan'
        
        # Navigation items with icons
        nav_items = [
            {"icon": "📄", "label": "Scan Resume", "key": "scan"},
            {"icon": "📊", "label": "Analytics", "key": "analytics"},
            {"icon": "⚙️", "label": "Settings", "key": "settings"}
        ]
        
        # Navigation container with proper spacing
        st.markdown('<div style="padding: 0.5rem 0.5rem 5rem 0.5rem;">', unsafe_allow_html=True)
        
        # Render navigation items
        for item in nav_items:
            is_active = st.session_state.current_page == item['key']
            if st.button(
                f"{item['icon']} {item['label']}", 
                key=f"nav_{item['key']}", 
                type="primary" if is_active else "secondary",
                use_container_width=True
            ):
                st.session_state.current_page = item['key']
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Sidebar footer
        st.markdown("""
        <div class="sidebar-footer">
            <p>ResumeScan AI v1.0</p>
            <p>Powered by AI & Machine Learning</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    if st.session_state.current_page == 'scan':
        # Hero section with animated gradient
        st.markdown("""
        <div class="main-header">
            <h1>AI-Powered Resume Analysis</h1>
            <p style="opacity: 0.9; max-width: 700px; margin: 0 auto;">
                Get instant insights on how well your resume matches job descriptions
                using advanced AI and natural language processing.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main content columns
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # Upload card with drag and drop
            with st.container():
                st.markdown("""
                <div style="margin-bottom: 1.5rem;">
                    <h2 style="margin-bottom: 0.5rem;">📄 Upload Resume</h2>
                    <p style="color: #6b7280; margin-top: 0;">Upload your resume in PDF or DOCX format</p>
                </div>
                """, unsafe_allow_html=True)
                
                uploaded_file = st.file_uploader(
                    "Drag and drop or click to upload",
                    type=['pdf', 'docx'],
                    help="Supported formats: PDF, DOCX",
                    label_visibility="collapsed"
                )
                
                if uploaded_file:
                    st.success(f"✅ {uploaded_file.name} uploaded successfully!")
        
        with col2:
            # Job description card
            with st.container():
                st.markdown("""
                <div style="margin-bottom: 1.5rem;">
                    <h2 style="margin-bottom: 0.5rem;">📝 Job Description</h2>
                    <p style="color: #6b7280; margin-top: 0;">Paste the job description or select a sample</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Sample job descriptions
                sample_jobs = load_sample_job_descriptions()
                selected_sample = st.selectbox(
                    "Select a sample job description:",
                    ["Custom"] + list(sample_jobs.keys()),
                    label_visibility="collapsed"
                )
                
                job_description = st.text_area(
                    "Job Description",
                    value=sample_jobs.get(selected_sample, "") if selected_sample != "Custom" else "",
                    height=200,
                    placeholder="Paste the job description here...",
                    label_visibility="collapsed"
                )
        
        # Action button row
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            if st.button(
                "🚀 Analyze Resume Match",
                use_container_width=True,
                type="primary",
                help="Click to analyze how well your resume matches the job description"
            ):
                if uploaded_file and job_description:
                    with st.spinner("🧠 Analyzing your resume..."):
                        result = process_resume(uploaded_file, job_description)
                        if result:
                            save_scan_result(result, uploaded_file.name, job_description)
                            st.session_state.show_results = True
                            st.rerun()
                else:
                    st.error("Please upload a resume and enter a job description.")
        
        # Display results if available
        if st.session_state.get('show_results') and st.session_state.current_scan:
            st.markdown("---")
            display_results(st.session_state.current_scan['result'])
    
    elif st.session_state.current_page == 'analytics':
        display_analytics()
    
    elif st.session_state.current_page == 'settings':
        display_settings()
    
def display_settings():
    st.title("⚙️ Settings")
    with st.container():
        st.markdown("### 🤖 AI Summary Configuration")
        st.info("AI summaries are generated locally. No external API is used.")
        st.success("✅ Local summary generation is enabled.")

if __name__ == "__main__":
    main()