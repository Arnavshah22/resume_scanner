import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!resume || !jobDescription) {
      alert('Please upload a resume and enter job description.');
      return;
    }

    const formData = new FormData();
    formData.append('resume', resume);
    formData.append('job_description', jobDescription);

    try {
      const res = await axios.post('http://localhost:5000/scan', formData);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Error scanning resume.');
    }
  };

  return (
    <div className="container">
      <h1>Resume Scanner</h1>

      <form onSubmit={handleSubmit}>
        <label>Job Description</label>
        <textarea
          rows={6}
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          placeholder="Paste the job description here..."
          required
        />

        <label>Upload Resume (PDF or DOCX)</label>
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={(e) => setResume(e.target.files[0])}
          required
        />

        <button type="submit">Scan Resume</button>
      </form>

      {result && (
        <div className="result">
          <h2>Scan Result</h2>
          <p><strong>Final Match Score:</strong> {result.match_score}%</p>
          <p><strong>Fit:</strong> {result.fit}</p>
          <p><strong>Summary:</strong> {result.summary}</p>

          <h3>Score Breakdown</h3>
          <ul>
            <li><strong>Semantic Score:</strong> {result.score_breakdown?.semantic_score}%</li>
            <li><strong>Skill Score:</strong> {result.score_breakdown?.skill_score}%</li>
            <li><strong>Experience Score:</strong> {result.score_breakdown?.experience_score}%</li>
          </ul>

          <h3>Candidate Info</h3>
          <p><strong>Name:</strong> {result.candidate_info?.name}</p>
          <p><strong>Email:</strong> {result.candidate_info?.email}</p>
          <p><strong>Phone:</strong> {result.candidate_info?.phone}</p>
          <p><strong>Address:</strong> {result.candidate_info?.address}</p>
          <p><strong>Experience:</strong> {result.candidate_info?.experience_years} years</p>

          <p><strong>Skills:</strong><br />
            {(result.candidate_info?.skills || []).map((skill, i) => (
              <span key={i} className="badge">{skill}</span>
            ))}
          </p>
        </div>
      )}
    </div>
  );
}

export default App; 
