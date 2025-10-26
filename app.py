# =============================================================================
# 1. IMPORT LIBRARIES
# =============================================================================
from flask import Flask, request, jsonify
from flask_cors import CORS 
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import fitz  # PyMuPDF library for reading PDFs
import re    # Regular expressions for text analysis

# =============================================================================
# 2. CREATE THE FLASK APP
# =============================================================================
app = Flask(__name__)
CORS(app) 

# =============================================================================
# 3. FUZZY LOGIC CALCULATION FUNCTION (Unchanged)
# =============================================================================
# This function remains the same as before.
def calculate_fit_score(exp, skills, edu, cgpa, projects):
    # (The entire fuzzy logic calculation code is here, same as before)
    # Define Fuzzy Variables
    experience = ctrl.Antecedent(np.arange(0, 16, 1), 'experience')
    skill_match = ctrl.Antecedent(np.arange(0, 101, 1), 'skill_match')
    education = ctrl.Antecedent(np.arange(1, 6, 1), 'education')
    profile_strength = ctrl.Antecedent(np.arange(0, 11, 1), 'profile_strength')
    candidate_fit = ctrl.Consequent(np.arange(0, 101, 1), 'candidate_fit')

    # Define Membership Functions
    experience['None'] = fuzz.trimf(experience.universe, [0, 0, 2])
    experience['Some'] = fuzz.trimf(experience.universe, [1, 4, 7])
    experience['Matched'] = fuzz.trimf(experience.universe, [5, 8, 11])
    experience['Extensive'] = fuzz.trimf(experience.universe, [9, 15, 15])
    skill_match['Low'] = fuzz.trimf(skill_match.universe, [0, 0, 50])
    skill_match['Medium'] = fuzz.trimf(skill_match.universe, [30, 65, 90])
    skill_match['High'] = fuzz.trimf(skill_match.universe, [70, 100, 100])
    education['Relevant'] = fuzz.trimf(education.universe, [1, 3, 4])
    education['Advanced'] = fuzz.trimf(education.universe, [3, 5, 5])
    profile_strength['Weak'] = fuzz.trimf(profile_strength.universe, [0, 0, 4])
    profile_strength['Average'] = fuzz.trimf(profile_strength.universe, [3, 5, 7])
    profile_strength['Strong'] = fuzz.trimf(profile_strength.universe, [6, 10, 10])
    candidate_fit['Poor Fit'] = fuzz.trimf(candidate_fit.universe, [0, 0, 40])
    candidate_fit['Possible Fit'] = fuzz.trimf(candidate_fit.universe, [30, 55, 75])
    candidate_fit['Good Fit'] = fuzz.trimf(candidate_fit.universe, [65, 80, 95])
    candidate_fit['Top Candidate'] = fuzz.trimf(candidate_fit.universe, [85, 100, 100])

    # Define Fuzzy Rules
    rule1 = ctrl.Rule(skill_match['High'] & experience['Matched'], candidate_fit['Top Candidate'])
    rule2 = ctrl.Rule(skill_match['High'] & experience['Some'], candidate_fit['Good Fit'])
    rule3 = ctrl.Rule(skill_match['Low'] | experience['None'], candidate_fit['Poor Fit'])
    rule4 = ctrl.Rule(skill_match['High'] & education['Advanced'], candidate_fit['Top Candidate'])
    rule5 = ctrl.Rule(skill_match['Medium'] & experience['Some'], candidate_fit['Possible Fit'])
    rule6 = ctrl.Rule(skill_match['High'] & profile_strength['Strong'], candidate_fit['Good Fit'])
    rule7 = ctrl.Rule(experience['None'] & profile_strength['Weak'], candidate_fit['Poor Fit'])
    rule8 = ctrl.Rule(skill_match['Medium'] & profile_strength['Average'], candidate_fit['Possible Fit'])

    # Create and run the control system
    fit_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8])
    fit_simulation = ctrl.ControlSystemSimulation(fit_ctrl)

    # Combine CGPA and Projects
    cgpa_score = (cgpa / 10) * 5 
    project_score = min(projects, 5)
    combined_profile_score = cgpa_score + project_score
    
    # Pass inputs
    fit_simulation.input['experience'] = exp
    fit_simulation.input['skill_match'] = skills
    fit_simulation.input['education'] = edu
    fit_simulation.input['profile_strength'] = combined_profile_score
    
    fit_simulation.compute()
    return fit_simulation.output['candidate_fit']

# =============================================================================
# 4. --- NEW: HELPER FUNCTIONS FOR PDF ANALYSIS ---
# =============================================================================

def extract_text_from_pdf(pdf_file):
    """Reads a PDF file and returns its text content."""
    try:
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        return text.lower() # Convert to lowercase for easier analysis
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def analyze_resume_text(text, required_skills_str):
    """Analyzes the extracted text to find skills, CGPA, etc."""
    # This is a simplified analysis. A real-world version would be more complex.
    
    # 1. Analyze Skills
    candidate_skills = set(re.findall(r'\b(python|java|c\+\+|javascript|react\.js|node\.js|express\.js|mongodb|html5|css3|git|firebase)\b', text))
    required_skills = set(skill.strip().lower() for skill in required_skills_str.split(','))
    
    if not required_skills:
        skill_match_percent = 100
    else:
        matching_skills = candidate_skills.intersection(required_skills)
        skill_match_percent = round((len(matching_skills) / len(required_skills)) * 100)

    # 2. Analyze CGPA (finds numbers like 7.6, 8.5, etc.)
    cgpa_match = re.search(r'cgpa\s*[:\-]?\s*(\d\.\d+)', text)
    cgpa = float(cgpa_match.group(1)) if cgpa_match else 7.0 # Default CGPA if not found

    # 3. Analyze Projects (counts the word 'project')
    projects = text.count('project')
    
    # 4. Analyze Experience and Education (defaults for this simple version)
    experience = 2  # Default value
    education = 3   # Default value

    return {
        "experience": experience,
        "skill_match": skill_match_percent,
        "education": education,
        "cgpa": cgpa,
        "projects": projects
    }

# =============================================================================
# 5. DEFINE API ENDPOINTS
# =============================================================================

# Endpoint for Manual Entry (Unchanged)
@app.route('/predict', methods=['POST'])
def predict():
    # ... (this function is the same as before)
    data = request.get_json()
    required_fields = ['experience', 'skill_match', 'education', 'cgpa', 'projects']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing data'}), 400
    score = calculate_fit_score(
        data['experience'], data['skill_match'], data['education'], data['cgpa'], data['projects']
    )
    return jsonify({'fit_score': round(score, 2)})

# --- NEW: Endpoint for PDF Upload ---
@app.route('/upload', methods=['POST'])
def upload_resume():
    # Check if a file was uploaded
    if 'resume' not in request.files or 'requiredSkills' not in request.form:
        return jsonify({'error': 'Missing resume file or required skills'}), 400

    resume_file = request.files['resume']
    required_skills = request.form['requiredSkills']
    
    # Check if the file is a PDF
    if resume_file.filename == '' or not resume_file.filename.endswith('.pdf'):
        return jsonify({'error': 'Please upload a valid PDF file'}), 400

    # 1. Extract text from the PDF
    resume_text = extract_text_from_pdf(resume_file)
    if not resume_text:
        return jsonify({'error': 'Could not read text from PDF'}), 500

    # 2. Analyze the extracted text
    candidate_data = analyze_resume_text(resume_text, required_skills)
    
    # 3. Calculate the score using our fuzzy logic engine
    score = calculate_fit_score(
        candidate_data['experience'],
        candidate_data['skill_match'],
        candidate_data['education'],
        candidate_data['cgpa'],
        candidate_data['projects']
    )
    
    # 4. Return the score and the extracted data
    return jsonify({
        'fit_score': round(score, 2),
        'extracted_data': candidate_data
    })


# =============================================================================
# 6. RUN THE FLASK APP
# =============================================================================
if __name__ == '__main__':
    app.run(debug=True)