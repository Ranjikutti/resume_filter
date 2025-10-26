# Fuzzy Logic Resume Screening Assistant 📄🧠

This is a full-stack web application that uses a fuzzy logic inference system to intelligently screen resumes and provide a "Candidate Fit Score". The application features two modes: a detailed manual entry form and an automated analysis mode that extracts data directly from an uploaded PDF resume.

![App Screenshot](URL_TO_YOUR_SCREENSHOT_IMAGE)
*(You can take a screenshot of your working app and upload it to your GitHub repo to display it here)*

---

## ✨ Features

- **Dual Modes:** Switch between a detailed **Manual Entry** form and an automated **PDF Upload** system.
- **Intelligent Scoring:** Uses a fuzzy logic engine to score candidates based on multiple nuanced factors, not just rigid rules.
- **Dynamic Skill Analysis:** Automatically calculates a skill match percentage from comma-separated lists or from extracted resume text.
- **Full-Stack Architecture:** Built with a modern React frontend and a Python Flask backend.
- **Automated Data Extraction:** The backend uses PyMuPDF to read and parse text from uploaded PDF resumes to find skills, CGPA, and project counts.

---

## 🛠️ Tech Stack

- **Frontend:** React.js, Vite, Axios
- **Backend:** Python, Flask
- **Fuzzy Logic Engine:** `scikit-fuzzy`
- **PDF Parsing:** `PyMuPDF`
- **Core Libraries:** NumPy

---

## 🚀 How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Ranjikutti/resume_filter.git](https://github.com/Ranjikutti/resume_filter.git)
    cd resume_filter
    ```

2.  **Setup the Backend:**
    ```bash
    # Create and activate a virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate

    # Install backend dependencies
    pip install -r requirements.txt 
    # (Note: You'll need to create a requirements.txt file)

    # Run the backend server
    python app.py
    ```

3.  **Setup the Frontend:**
    ```bash
    # Navigate to the frontend directory
    cd frontend

    # Install frontend dependencies
    npm install

    # Run the frontend server
    npm run dev
    ```
- The backend will be running on `http://localhost:5000`
- The frontend will be running on `http://localhost:5173`