import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // --- NEW: State to control which mode is active ---
  const [mode, setMode] = useState('manual'); // 'manual' or 'upload'

  // State for Manual Form
  const [formData, setFormData] = useState({
    experience: 2,
    candidateSkills: 'React, Node.js, MongoDB',
    requiredSkills: 'React, Node.js, Express, MongoDB, Python',
    education: 3,
    cgpa: 7.5,
    projects: 4,
  });

  // State for Upload Form
  const [selectedFile, setSelectedFile] = useState(null);
  const [requiredSkillsForUpload, setRequiredSkillsForUpload] = useState('React, Node.js, Python');
  const [extractedData, setExtractedData] = useState(null);

  // Common State
  const [score, setScore] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // --- MANUAL FORM LOGIC ---
  const handleManualChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: (name === 'cgpa') ? parseFloat(value) : (['experience', 'education', 'projects'].includes(name) ? Number(value) : value),
    });
  };

  const calculateSkillMatch = (candidateSkills, requiredSkills) => {
    const candidateSet = new Set(candidateSkills.split(',').map(skill => skill.trim().toLowerCase()));
    const requiredSet = new Set(requiredSkills.split(',').map(skill => skill.trim().toLowerCase()));
    if (requiredSet.size === 0) return 100;
    let matchCount = 0;
    candidateSet.forEach(skill => {
      if (requiredSet.has(skill)) matchCount++;
    });
    return Math.round((matchCount / requiredSet.size) * 100);
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    clearResults();
    setIsLoading(true);
    const skillMatchPercentage = calculateSkillMatch(formData.candidateSkills, formData.requiredSkills);
    const apiPayload = { ...formData, skill_match: skillMatchPercentage };

    try {
      // --- UPDATED URL ---
      const response = await axios.post('https://resume-filter-backend-k1km.onrender.com/predict', apiPayload);
      setScore(response.data.fit_score);
    } catch (err) {
      handleApiError(err);
    } finally {
      setIsLoading(false);
    }
  };

  // --- UPLOAD FORM LOGIC ---
  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select a PDF file to upload.');
      return;
    }
    clearResults();
    setIsLoading(true);

    const uploadFormData = new FormData();
    uploadFormData.append('resume', selectedFile);
    uploadFormData.append('requiredSkills', requiredSkillsForUpload);

    try {
      // --- UPDATED URL ---
      const response = await axios.post('https://resume-filter-backend-k1km.onrender.com/upload', uploadFormData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setScore(response.data.fit_score);
      setExtractedData(response.data.extracted_data); // Save extracted data
    } catch (err) {
      handleApiError(err);
    } finally {
      setIsLoading(false);
    }
  };
  
  // --- HELPER FUNCTIONS ---
  const clearResults = () => {
    setError('');
    setScore(null);
    setExtractedData(null);
  };
  
  const handleApiError = (err) => {
    setError('Failed to get a response from the server.');
    console.error(err);
  }

  return (
    <div className="container">
      <h1>Resume Screening Assistant</h1>

      {/* --- Mode Switcher Tabs --- */}
      <div className="mode-switcher">
        <button onClick={() => setMode('manual')} className={mode === 'manual' ? 'active' : ''}>
          Manual Entry
        </button>
        <button onClick={() => setMode('upload')} className={mode === 'upload' ? 'active' : ''}>
          Upload Resume
        </button>
      </div>

      {/* --- Show form based on mode --- */}
      {mode === 'manual' ? (
        // --- MANUAL FORM ---
        <form onSubmit={handleManualSubmit}>
          <div className="form-group">
            <label>Required Job Skills (comma-separated)</label>
            <textarea name="requiredSkills" value={formData.requiredSkills} onChange={handleManualChange} rows="3" />
          </div>
          <div className="form-group">
            <label>Candidate's Skills (comma-separated)</label>
            <textarea name="candidateSkills" value={formData.candidateSkills} onChange={handleManualChange} rows="3" />
          </div>
          <div className="grid-container">
            <div className="form-group"><label>Experience (yrs)</label><input type="number" name="experience" value={formData.experience} onChange={handleManualChange} min="0" max="15"/></div>
            <div className="form-group"><label>Education (1-5)</label><input type="number" name="education" value={formData.education} onChange={handleManualChange} min="1" max="5"/></div>
            <div className="form-group"><label>CGPA</label><input type="number" name="cgpa" value={formData.cgpa} onChange={handleManualChange} min="0" max="10" step="0.1"/></div>
            <div className="form-group"><label>No. of Projects</label><input type="number" name="projects" value={formData.projects} onChange={handleManualChange} min="0" max="20"/></div>
          </div>
          <button type="submit" disabled={isLoading}>{isLoading ? 'Calculating...' : 'Calculate Score'}</button>
        </form>
      ) : (
        // --- UPLOAD FORM ---
        <form onSubmit={handleUploadSubmit}>
          <div className="form-group">
            <label>Required Job Skills (comma-separated)</label>
            <textarea value={requiredSkillsForUpload} onChange={(e) => setRequiredSkillsForUpload(e.target.value)} rows="3" />
          </div>
          <div className="form-group">
            <label>Upload Resume (PDF only)</label>
            <input type="file" name="resume" onChange={handleFileChange} accept=".pdf" />
          </div>
          <button type="submit" disabled={isLoading}>{isLoading ? 'Analyzing...' : 'Analyze Resume'}</button>
        </form>
      )}

      {/* --- RESULTS SECTION --- */}
      {isLoading && <p className="loading-text">Analyzing...</p>}
      {score !== null && (
        <div className="result">
          <h2>Candidate Fit Score:</h2>
          <p className="score">{score} / 100</p>
          {extractedData && (
            <div className="extracted-data">
              <h3>Extracted Data:</h3>
              <p><strong>Skill Match:</strong> {extractedData.skill_match}% | <strong>CGPA:</strong> {extractedData.cgpa} | <strong>Projects:</strong> {extractedData.projects}</p>
            </div>
          )}
        </div>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default App;