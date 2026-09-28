# FitBuddy - AI Fitness Plan Generator - Team N3Bee
AI-powered personalized fitness coach built with Gemini + Streamlit + FastAPI pattern.

🚀 Live Demo: https://n3bee-fitbuddy.streamlit.app

Team N3Bee:
- Anushree P - Topic Links, Setup Environment, Main Application Logic in app.py, Conclusion
- Avinth Atchai C - Workflow, Develop Core Functionalities, Designing and Developing UI
- Ahammed Sha - Research and Select Model, Implement FastAPI Backend, Creating Dynamic Templates
- Afsal A - Define Architecture, Preparing for Local Deployment, Testing and Verifying

Features - 3 Scenarios:
Scenario 1: Generate Plan - Input Name, Age, Weight, Height, Gender, Goal, Intensity, Diet, Allergies -> 7-day plan with sets reps rest + nutrition + recovery
Scenario 2: Update with Feedback - User enters Name + Feedback e.g. "more cardio" -> Regenerates based on previous plan
Scenario 3: Nutrition / Recovery Tip - Selects Goal and gets instant tip

Tech Stack:
- Frontend: Streamlit
- AI: Google Gemini 1.5 Flash (5 models parallel)
- Backend: Python (FastAPI pattern)
- DB: SQLite + Session State

How to Use:
1. Get Gemini API Key from https://aistudio.google.com/app/apikey
2. Open app
3. Enter API Key in sidebar
4. Generate your plan

Main Code: 5.Project Development Phase/app.py
Run: pip install -r 5.Project\ Development\ Phase/requirements.txt && streamlit run 5.Project\ Development\ Phase/app.py
