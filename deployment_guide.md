# AI Resume Scanner Pro - Industrial Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the AI Resume Scanner Pro application in an industrial environment using Streamlit Cloud or self-hosted solutions.

## 🚀 Quick Start (Streamlit Cloud)

### 1. Prerequisites
- GitHub account
- Streamlit Cloud account (free tier available)
- Python 3.8+ environment

### 2. Repository Setup
```bash
# Clone or create your repository
git clone <your-repo-url>
cd resume_scanerr_ai

# Ensure all files are committed
git add .
git commit -m "Initial Streamlit deployment"
git push origin main
```

### 3. Streamlit Cloud Deployment
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository and branch
5. Set the main file path: `streamlit_app.py`
6. Click "Deploy"

## 🏭 Industrial Deployment Options

### Option 1: Streamlit Cloud (Recommended for Small-Medium Scale)

**Pros:**
- Zero infrastructure management
- Automatic scaling
- Built-in security
- Easy deployment

**Cons:**
- Limited customization
- Resource constraints on free tier
- Data privacy concerns

**Configuration:**
```toml
# .streamlit/config.toml
[server]
maxUploadSize = 10
enableXsrfProtection = true
enableCORS = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

### Option 2: Docker Deployment (Recommended for Large Scale)

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY streamlit_requirements.txt .
RUN pip install -r streamlit_requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application files
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Docker Compose:**
```yaml
version: '3.8'

services:
  resume-scanner:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DEBUG=False
      - LOG_LEVEL=INFO
      - SECRET_KEY=your-secret-key-here
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - resume-scanner
    restart: unless-stopped
```

### Option 3: Kubernetes Deployment (Enterprise Scale)

**Deployment YAML:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resume-scanner
  labels:
    app: resume-scanner
spec:
  replicas: 3
  selector:
    matchLabels:
      app: resume-scanner
  template:
    metadata:
      labels:
        app: resume-scanner
    spec:
      containers:
      - name: resume-scanner
        image: your-registry/resume-scanner:latest
        ports:
        - containerPort: 8501
        env:
        - name: DEBUG
          value: "False"
        - name: LOG_LEVEL
          value: "INFO"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: resume-scanner-secret
              key: secret-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: resume-scanner-service
spec:
  selector:
    app: resume-scanner
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8501
  type: LoadBalancer
```

## 🔧 Configuration

### Environment Variables
```bash
# Application
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=your-secure-secret-key

# Performance
MAX_CONCURRENT_SCANS=5
MODEL_CACHE_SIZE=100

# Security
ENABLE_ANALYTICS=True
ALLOWED_EXTENSIONS=pdf,docx,doc
MAX_FILE_SIZE=10485760

# AI Models
SENTENCE_TRANSFORMER_MODEL=BAAI/bge-large-en-v1.5
SPACY_MODEL=en_core_web_sm
```

### Production Settings
```python
# config.py additions for production
PRODUCTION_CONFIG = {
    'enable_telemetry': False,
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'allowed_extensions': {'pdf', 'docx', 'doc'},
    'session_timeout': 3600,  # 1 hour
    'max_upload_retries': 3,
    'enable_rate_limiting': True,
    'rate_limit_per_minute': 10,
    'enable_logging': True,
    'log_retention_days': 30,
    'enable_backup': True,
    'backup_interval_hours': 24
}
```

## 🔒 Security Considerations

### 1. Data Privacy
```python
# Add to streamlit_app.py
import hashlib
import os

def sanitize_filename(filename):
    """Sanitize uploaded filename"""
    name, ext = os.path.splitext(filename)
    sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    return f"{sanitized_name}_{hashlib.md5(filename.encode()).hexdigest()[:8]}{ext}"

def validate_file(file):
    """Validate uploaded file"""
    if file.size > MAX_FILE_SIZE:
        st.error(f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB")
        return False
    
    if not file.name.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
        st.error(f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
        return False
    
    return True
```

### 2. Authentication (Optional)
```python
# Add authentication wrapper
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 User not known or password incorrect")
        return False
    else:
        return True
```

## 📊 Monitoring & Analytics

### 1. Application Metrics
```python
# Add to streamlit_app.py
import time
from datetime import datetime

def log_scan_metrics(result, processing_time):
    """Log scan metrics for monitoring"""
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'match_score': result['final_score'],
        'processing_time': processing_time,
        'file_size': uploaded_file.size if uploaded_file else 0,
        'file_type': uploaded_file.type if uploaded_file else None,
        'user_agent': st.get_user_agent(),
        'session_id': st.session_state.get('session_id', 'unknown')
    }
    
    # Log to file or database
    with open('logs/scan_metrics.json', 'a') as f:
        json.dump(metrics, f)
        f.write('\n')
```

### 2. Health Checks
```python
# Add health check endpoint
def health_check():
    """Health check for monitoring"""
    try:
        # Test model loading
        scorer = get_scorer()
        extractor = get_extractor()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'models_loaded': True,
            'memory_usage': psutil.virtual_memory().percent
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
```

## 🚀 Performance Optimization

### 1. Caching Strategy
```python
# Enhanced caching for production
@st.cache_data(ttl=3600, max_entries=100)
def load_models():
    """Cache model loading"""
    return {
        'scorer': get_scorer(),
        'extractor': get_extractor()
    }

@st.cache_data(ttl=1800, max_entries=50)
def process_resume_cached(file_content, job_description):
    """Cache resume processing results"""
    return process_resume(file_content, job_description)
```

### 2. Background Processing
```python
# For heavy processing tasks
import threading
import queue

def background_processor():
    """Background processor for heavy tasks"""
    while True:
        try:
            task = task_queue.get(timeout=1)
            if task is None:
                break
            
            # Process task
            result = process_resume(task['file'], task['job_description'])
            task['callback'](result)
            
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"Background processing error: {e}")

# Start background processor
task_queue = queue.Queue()
processor_thread = threading.Thread(target=background_processor, daemon=True)
processor_thread.start()
```

## 📈 Scaling Considerations

### 1. Horizontal Scaling
- Use load balancer for multiple instances
- Implement session management
- Use shared storage for uploads
- Implement proper caching strategy

### 2. Vertical Scaling
- Increase memory allocation for large models
- Use GPU acceleration if available
- Optimize model loading and caching

### 3. Database Integration
```python
# Add database support for production
import sqlite3
import psycopg2

def save_scan_to_database(scan_data):
    """Save scan results to database"""
    # Implementation for your preferred database
    pass

def get_scan_history(user_id):
    """Retrieve scan history from database"""
    # Implementation for your preferred database
    pass
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r streamlit_requirements.txt
    - name: Run tests
      run: |
        python -m pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Streamlit Cloud
      run: |
        # Your deployment commands
        echo "Deployment completed"
```

## 📋 Maintenance Checklist

### Daily
- [ ] Check application logs for errors
- [ ] Monitor system resources
- [ ] Verify backup completion
- [ ] Check scan metrics

### Weekly
- [ ] Review performance metrics
- [ ] Update dependencies if needed
- [ ] Clean up old log files
- [ ] Verify security settings

### Monthly
- [ ] Update AI models
- [ ] Review and update skill keywords
- [ ] Performance optimization
- [ ] Security audit

## 🆘 Troubleshooting

### Common Issues

1. **Model Loading Failures**
   ```bash
   # Solution: Clear cache and reinstall
   pip uninstall sentence-transformers spacy
   pip install -r streamlit_requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Memory Issues**
   ```python
   # Add to config.py
   import gc
   
   def cleanup_memory():
       gc.collect()
       torch.cuda.empty_cache() if torch.cuda.is_available() else None
   ```

3. **File Upload Issues**
   ```python
   # Add file validation
   def validate_upload(file):
       if file.size > MAX_FILE_SIZE:
           return False, "File too large"
       if not file.name.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
           return False, "Invalid file type"
       return True, "Valid file"
   ```

## 📞 Support

For industrial deployment support:
- Create issues in the GitHub repository
- Contact: support@resumescanner.ai
- Documentation: https://docs.resumescanner.ai
- Community: https://community.resumescanner.ai 