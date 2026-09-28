# 2.Requirement Analysis
Team N3Bee - Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A
Assigned to: Anushree P

Functional Requirements:
FR1: Input: Name, Age, Weight, Height, Gender, Activity, Intensity, Goal, Diet, Allergies
FR2: Scenario 1: Generate 7-Day Personalized Plan
FR3: Scenario 2: Update Plan with Feedback (e.g. knee pain, more cardio)
FR4: Scenario 3: Get Nutrition Tip / Recovery Tip
FR5: Save to DB and Download as txt

Non-Functional Requirements:
NFR1: Response < 10 sec (5 models parallel with ThreadPoolExecutor)
NFR2: Different Weight/Height MUST give different output (BMI, Calories, Protein logic)
NFR3: Works with 1 API key from sidebar, not hardcoded
NFR4: No error on API failure - dynamic fallback
NFR5: No same static output bug

Tech Stack: Python, Streamlit, google-genai SDK, SQLite3, concurrent.futures

Input/Output Example:
Input 60kg/165cm Goal Weight Loss -> Output: BMI 22.0, Calories 1440, Protein 96g, Cardio focused plan
Input 90kg/180cm Goal Muscle Gain -> Output: BMI 27.7, Calories 3150, Protein 180g, Strength focused plan
