import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // New state to hold the detailed form data
  const [formData, setFormData] = useState({
    experience: 2,
    candidateSkills: 'React, Node.js, MongoDB',
    requiredSkills: 'React, Node.js, Express, MongoDB, Python',
    education: 3,
    cgpa: 7.5,
    projects: 4,
  });

  const [score, setScore] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Function to handle changes in the input fields
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      // Use parseFloat for numbers that can be decimals, otherwise use value
      [name]: (name === 'cgpa') ? parseFloat(value) : (['experience', 'education', 'projects'].includes(name) ? Number(value) : value),
    });
  };

  // --- NEW LOGIC: Calculate Skill Match Percentage ---
  const calculateSkillMatch = (candidateSkills, requiredSkills) => {
    const candidateSet = new Set(candidateSkills.split(',').map(skill => skill.trim().toLowerCase()));
    const requiredSet = new Set(requiredSkills.split(',').map(skill => skill.trim().toLowerCase()));
    
    if (requiredSet.size === 0) return 100;

    let matchCount = 0;
    for (const skill of candidateSet) {
      if (requiredSet.has(skill)) {
        matchCount++;
      }
    }
    return Math.round((matchCount / requiredSet.size) * 100);
  };


  // Function to handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setScore(null);
    setIsLoading(true);

    // Calculate the skill match percentage
    const skillMatchPercentage = calculateSkillMatch(formData.candidateSkills, formData.requiredSkills);

    // --- THIS IS THE PART THAT WAS UPDATED ---
    // Prepare data to send to the backend, including the new fields
    const apiPayload = {
      experience: formData.experience,
      skill_match: skillMatchPercentage,
      education: formData.education,
      cgpa: formData.cgpa,         // This line was added
      projects: formData.projects,   // This line was added
    };

    try {
      const response = await axios.post('http://localhost:5000/predict', apiPayload);
      setScore(response.data.fit_score);
    } catch (err) {
      setError('Failed to get a response from the server. Is it running?');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Resume Screening Assistant</h1>
      <p>Enter the candidate's details to calculate their fit score.</p>
      
      <form onSubmit={handleSubmit}>
        {/* -- Text Areas for Skills -- */}
        <div className="form-group">
          <label>Required Job Skills (comma-separated)</label>
          <textarea
            name="requiredSkills"
            value={formData.requiredSkills}
            onChange={handleChange}
            rows="3"
          />
        </div>
        <div className="form-group">
          <label>Candidate's Skills (comma-separated)</label>
          <textarea
            name="candidateSkills"
            value={formData.candidateSkills}
            onChange={handleChange}
            rows="3"
          />
        </div>
        
        {/* -- Number Inputs for other metrics -- */}
        <div className="grid-container">
          <div className="form-group">
            <label>Experience (yrs)</label>
            <input type="number" name="experience" value={formData.experience} onChange={handleChange} min="0" max="15"/>
          </div>
          <div className="form-group">
            <label>Education (1-5)</label>
            <input type="number" name="education" value={formData.education} onChange={handleChange} min="1" max="5"/>
          </div>
          <div className="form-group">
            <label>CGPA</label>
            <input type="number" name="cgpa" value={formData.cgpa} onChange={handleChange} min="0" max="10" step="0.1"/>
          </div>
          <div className="form-group">
            <label>No. of Projects</label>
            <input type="number" name="projects" value={formData.projects} onChange={handleChange} min="0" max="20"/>
          </div>
        </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Calculating...' : 'Calculate Score'}
        </button>
      </form>

      {score !== null && (
        <div className="result">
          <h2>Candidate Fit Score:</h2>
          <p className="score">{score} / 100</p>
        </div>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default App;