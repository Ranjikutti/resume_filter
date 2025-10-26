# =============================================================================
# 1. IMPORT LIBRARIES
# =============================================================================
from flask import Flask, request, jsonify
# --- NEW: Import CORS to allow our React app to communicate with the backend ---
from flask_cors import CORS 
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# =============================================================================
# 2. CREATE THE FLASK APP
# =============================================================================
app = Flask(__name__)
# --- NEW: Enable CORS for all routes, allowing our frontend to make requests ---
CORS(app) 

# =============================================================================
# 3. FUZZY LOGIC CALCULATION FUNCTION
# =============================================================================
# We've updated this function to accept the new 'cgpa' and 'projects' inputs.
def calculate_fit_score(exp, skills, edu, cgpa, projects):
    # Define Fuzzy Variables (Inputs & Output)
    experience = ctrl.Antecedent(np.arange(0, 16, 1), 'experience')
    skill_match = ctrl.Antecedent(np.arange(0, 101, 1), 'skill_match')
    education = ctrl.Antecedent(np.arange(1, 6, 1), 'education')
    # --- NEW: Create a combined input for academic and practical profile ---
    profile_strength = ctrl.Antecedent(np.arange(0, 11, 1), 'profile_strength')
    
    candidate_fit = ctrl.Consequent(np.arange(0, 101, 1), 'candidate_fit')

    # Define Membership Functions
    # (Experience, Skill Match, and Education are unchanged)
    experience['None'] = fuzz.trimf(experience.universe, [0, 0, 2])
    experience['Some'] = fuzz.trimf(experience.universe, [1, 4, 7])
    experience['Matched'] = fuzz.trimf(experience.universe, [5, 8, 11])
    experience['Extensive'] = fuzz.trimf(experience.universe, [9, 15, 15])

    skill_match['Low'] = fuzz.trimf(skill_match.universe, [0, 0, 50])
    skill_match['Medium'] = fuzz.trimf(skill_match.universe, [30, 65, 90])
    skill_match['High'] = fuzz.trimf(skill_match.universe, [70, 100, 100])

    education['Relevant'] = fuzz.trimf(education.universe, [1, 3, 4])
    education['Advanced'] = fuzz.trimf(education.universe, [3, 5, 5])
    
    # --- NEW: Membership functions for 'profile_strength' ---
    profile_strength['Weak'] = fuzz.trimf(profile_strength.universe, [0, 0, 4])
    profile_strength['Average'] = fuzz.trimf(profile_strength.universe, [3, 5, 7])
    profile_strength['Strong'] = fuzz.trimf(profile_strength.universe, [6, 10, 10])

    # (Candidate Fit output is unchanged)
    candidate_fit['Poor Fit'] = fuzz.trimf(candidate_fit.universe, [0, 0, 40])
    candidate_fit['Possible Fit'] = fuzz.trimf(candidate_fit.universe, [30, 55, 75])
    candidate_fit['Good Fit'] = fuzz.trimf(candidate_fit.universe, [65, 80, 95])
    candidate_fit['Top Candidate'] = fuzz.trimf(candidate_fit.universe, [85, 100, 100])

    # --- UPDATED: Define Fuzzy Rules with new 'profile_strength' input ---
    rule1 = ctrl.Rule(skill_match['High'] & experience['Matched'], candidate_fit['Top Candidate'])
    rule2 = ctrl.Rule(skill_match['High'] & experience['Some'], candidate_fit['Good Fit'])
    rule3 = ctrl.Rule(skill_match['Low'] | experience['None'], candidate_fit['Poor Fit'])
    rule4 = ctrl.Rule(skill_match['High'] & education['Advanced'], candidate_fit['Top Candidate'])
    rule5 = ctrl.Rule(skill_match['Medium'] & experience['Some'], candidate_fit['Possible Fit'])
    
    # --- NEW RULES: These make the system smarter for junior candidates ---
    rule6 = ctrl.Rule(skill_match['High'] & profile_strength['Strong'], candidate_fit['Good Fit'])
    rule7 = ctrl.Rule(experience['None'] & profile_strength['Weak'], candidate_fit['Poor Fit'])
    rule8 = ctrl.Rule(skill_match['Medium'] & profile_strength['Average'], candidate_fit['Possible Fit'])


    # Create and run the control system
    fit_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8])
    fit_simulation = ctrl.ControlSystemSimulation(fit_ctrl)

    # --- NEW: Combine CGPA and Projects into a single Profile Strength score ---
    # Simple formula: Scale CGPA to be out of 5 and add number of projects (capped at 5)
    cgpa_score = (cgpa / 10) * 5 
    project_score = min(projects, 5) # Cap projects at 5 to balance the score
    combined_profile_score = cgpa_score + project_score
    
    # Pass inputs to the simulation
    fit_simulation.input['experience'] = exp
    fit_simulation.input['skill_match'] = skills
    fit_simulation.input['education'] = edu
    fit_simulation.input['profile_strength'] = combined_profile_score
    
    # Compute the result
    fit_simulation.compute()

    return fit_simulation.output['candidate_fit']

# =============================================================================
# 4. DEFINE THE API ENDPOINT
# =============================================================================
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # --- UPDATED: Check for the new fields ---
    required_fields = ['experience', 'skill_match', 'education', 'cgpa', 'projects']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing data'}), 400

    # Extract all data from the request
    exp = data['experience']
    skills = data['skill_match']
    edu = data['education']
    cgpa = data['cgpa']
    projects = data['projects']
    
    # Calculate the score
    score = calculate_fit_score(exp, skills, edu, cgpa, projects)
    
    # Send the score back
    return jsonify({'fit_score': round(score, 2)})

# =============================================================================
# 5. RUN THE FLASK APP
# =============================================================================
if __name__ == '__main__':
    app.run(debug=True)