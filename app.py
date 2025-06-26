import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from resumer_parser import extract_text
from scorer import calculate_similarity
from extractor import extract_contact_info
from flask_cors import CORS
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
run_with_ngrok(app)  # Enables ngrok for public URL

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
CORS(app)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return "Resume Scanner API is running."

@app.route('/scan', methods=['POST'])
def scan_resume():
    if 'resume' not in request.files or 'job_description' not in request.form:
        return jsonify({'error': 'Missing resume or job description'}), 400

    file = request.files['resume']
    job_description = request.form['job_description']

    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF or DOCX files allowed'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        # Extract resume text
        resume_text = extract_text(file_path)
        if not resume_text:
            return jsonify({'error': 'Text extraction failed'}), 500

        # Extract contact info
        contact_info = extract_contact_info(resume_text, filename)

        # Calculate score
        score_breakdown = calculate_similarity(
            resume_text,
            job_description,
            contact_info.get("skills", []),
            contact_info.get("experience_years", 0)
        )

        final_score = score_breakdown["final_score"]

        # Determine fit
        if final_score >= 75:
            fit = "Strong Fit"
            summary = "The resume strongly matches the job description. The candidate is highly suitable."
        elif final_score >= 45:
            fit = "Moderate Fit"
            summary = "The resume somewhat matches the job description. The candidate may need some support."
        else:
            fit = "Weak Fit"
            summary = "The resume does not closely match. The candidate may not be ideal for this role."

        return jsonify({
            'match_score': final_score,
            'fit': fit,
            'summary': summary,
            'candidate_info': contact_info,
            'score_breakdown': score_breakdown
        })

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run()
