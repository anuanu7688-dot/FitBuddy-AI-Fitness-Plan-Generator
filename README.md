# 💪 FitBuddy - AI Fitness Plan Generator

AI-powered personalized fitness coach built with Gemini + Streamlit + FastAPI logic.

**Team N3Bee:** Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A

### Features - Satisfies 3 Scenarios
**Scenario 1: Generate Plan:** User enters Name, Age, Weight, Height, Gender, Goal, Intensity, Activity Level, Diet. AI generates 7-day workout plan with sets, reps, rest + nutrition tip + recovery tip.

**Scenario 2: Update with Feedback:** User enters Name + Feedback (e.g., "more cardio"). AI regenerates plan based on previous plan + feedback.

**Scenario 3: Nutrition / Recovery Tip:** User selects Goal and gets instant 2-line tip from AI.

### How to Use
1. Get your free Gemini API Key from https://aistudio.google.com/app/apikey
2. Open the app
3. Enter your API Key in sidebar (Your key stays in your browser only, not saved)
4. Generate your plan

### Tech Stack
- Frontend: Streamlit
- AI: Google Gemini 1.5 Flash
- Backend Logic: Python (FastAPI pattern)
- DB: SQLite + Session State

### Run Locally
