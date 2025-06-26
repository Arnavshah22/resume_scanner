import os
import logging
from pathlib import Path
from dotenv import load_dotenv
# import requests  # No longer needed

# Load environment variables from .env file
load_dotenv()

# Application Configuration
APP_NAME = "AI Resume Scanner Pro"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# File Upload Configuration
UPLOAD_FOLDER = Path("uploads")
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# AI Model Configuration
SENTENCE_TRANSFORMER_MODEL = "BAAI/bge-large-en-v1.5"
SPACY_MODEL = "en_core_web_sm"

# AI Summary API Configuration
ENABLE_AI_SUMMARY = False  # No API usage

# Summary Generation Settings
SUMMARY_MAX_TOKENS = 500
SUMMARY_TEMPERATURE = 0.7

# Scoring Weights - Optimized for best hiring decisions
SCORING_WEIGHTS = {
    'skills': 0.45,        # 45% - Most important for technical roles
    'experience': 0.35,    # 35% - Second most important
    'semantic': 0.20       # 20% - Overall content relevance
}

# Score Thresholds
SCORE_THRESHOLDS = {
    'strong_fit': 75,
    'moderate_fit': 45,
    'weak_fit': 0
}

# Skill Keywords (extended for industrial use)
SKILL_KEYWORDS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'swift', 'kotlin',
    'php', 'ruby', 'scala', 'r', 'matlab', 'perl', 'bash', 'powershell',
    
    # Web Technologies
    'html', 'css', 'sass', 'scss', 'react', 'angular', 'vue', 'next.js', 'nuxt.js',
    'node.js', 'express.js', 'django', 'flask', 'fastapi', 'spring', 'laravel', 'symfony',
    'rails', 'asp.net', 'jquery', 'bootstrap', 'tailwind', 'webpack', 'vite',
    
    # Databases
    'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'sql server',
    'mariadb', 'cassandra', 'elasticsearch', 'dynamodb', 'firebase',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github',
    'gitlab', 'bitbucket', 'terraform', 'ansible', 'chef', 'puppet', 'vagrant',
    'nginx', 'apache', 'traefik', 'istio', 'helm', 'prometheus', 'grafana',
    
    # AI/ML/Data Science
    'machine learning', 'ml', 'ai', 'data science', 'deep learning', 'nlp',
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
    'matplotlib', 'seaborn', 'plotly', 'opencv', 'spacy', 'nltk', 'gensim',
    'hugging face', 'transformers', 'bert', 'gpt', 'llm', 'computer vision',
    'natural language processing', 'neural networks', 'statistics',
    
    # Big Data
    'hadoop', 'spark', 'kafka', 'flink', 'storm', 'hive', 'pig', 'sqoop',
    'flume', 'zookeeper', 'hbase', 'impala', 'presto', 'airflow', 'luigi',
    
    # Mobile Development
    'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic',
    'cordova', 'phonegap', 'swiftui', 'kotlin multiplatform',
    
    # Testing & Quality
    'junit', 'pytest', 'selenium', 'cypress', 'jest', 'mocha', 'chai',
    'sonarqube', 'codecov', 'jenkins', 'gitlab ci', 'github actions',
    'travis ci', 'circleci', 'teamcity', 'bamboo',
    
    # Methodologies
    'agile', 'scrum', 'kanban', 'lean', 'devops', 'ci/cd', 'tdd', 'bdd',
    'waterfall', 'spiral', 'v-model', 'extreme programming',
    
    # Tools & Platforms
    'jira', 'confluence', 'slack', 'teams', 'zoom', 'figma', 'sketch',
    'adobe xd', 'invision', 'postman', 'swagger', 'graphql', 'rest',
    'soap', 'microservices', 'api', 'websocket', 'grpc', 'thrift',
    
    # Security
    'oauth', 'jwt', 'ssl', 'tls', 'encryption', 'authentication',
    'authorization', 'penetration testing', 'vulnerability assessment',
    'siem', 'ids', 'ips', 'firewall', 'vpn', 'mfa', '2fa',
    
    # Business Intelligence
    'tableau', 'power bi', 'qlik', 'looker', 'metabase', 'superset',
    'etl', 'elt', 'data warehouse', 'data lake', 'data pipeline',
    'business intelligence', 'analytics', 'reporting', 'dashboard'
}

# Experience Patterns
EXPERIENCE_PATTERNS = [
    r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp|work)',
    r'(\d+)\+?\s*(?:year|yr)\s*(?:experience|exp)',
    r'experience\s*[:.]?\s*(\d+)\+?\s*(?:years?|yrs?)',
    r'(\d+)\+?\s*(?:years?|yrs?)\s*in\s*(?:software|development|programming|coding)',
    r'(\d+)\+?\s*(?:years?|yrs?)\s*as\s*(?:developer|engineer|programmer)',
]

# Phone Patterns (International)
PHONE_PATTERNS = [
    r'\+91[\s-]?\d{10}',  # Indian format with +91
    r'\b\d{10}\b',        # 10-digit number
    r'\+\d{1,3}[\s-]?\d{8,15}',  # International format
    r'\(\d{3}\)[\s-]?\d{3}[\s-]?\d{4}',  # US format
    r'\d{3}[\s-]?\d{3}[\s-]?\d{4}',  # US format without parentheses
]

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Cache Configuration
CACHE_TTL = 3600  # 1 hour in seconds

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "True").lower() == "true"

# Performance Configuration
MAX_CONCURRENT_SCANS = 5
MODEL_CACHE_SIZE = 100 