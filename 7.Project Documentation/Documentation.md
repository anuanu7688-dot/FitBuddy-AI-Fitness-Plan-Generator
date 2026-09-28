# 7.Project Documentation

Project: FitBuddy - AI Fitness Plan Generator
Team N3Bee: Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A

Tech Stack:
Frontend: Streamlit (3 Tabs)
AI: Google Gemini 5 Models Parallel (2.0-flash-lite, 2.5-flash-lite, 2.0-flash, 1.5-flash-8b, 1.5-flash)
Backend: Python + concurrent.futures ThreadPoolExecutor + sqlite3
DB: fitbuddy.db

Core Files:
- 5.Project Development Phase/app.py (Main Application Logic - Anushree P)
- 5.Project Development Phase/requirements.txt (streamlit, google-genai)
- All 8 Phases docs

How to Run:
1. pip install streamlit google-genai
2. Get key from https://aistudio.google.com/app/apikey
3. streamlit run 5.Project Development Phase/app.py
4. Enter key in sidebar, fill form, generate.

Key Features:
- BMI auto calc, Calories = weight*24/30/35 logic, Protein = weight*1.6/2.0
- No hardcoded API key, key from sidebar
- Download plan as txt
- Indian diet context
