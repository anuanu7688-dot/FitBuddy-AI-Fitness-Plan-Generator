# 3.Project Design Phase
Team N3Bee - Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A
Assigned to: Ahammed Sha (Research and Select Model) and Afsal A (Define Architecture)

1. Research and Select Generative AI Model - By Ahammed Sha:
We tested and selected 5 FASTEST Gemini Models to avoid error and delay:
- gemini-2.0-flash-lite (Fastest, primary)
- gemini-2.5-flash-lite
- gemini-2.0-flash
- gemini-1.5-flash-8b
- gemini-1.5-flash
Reason: Lite models are fastest and have high quota. We call all 5 in parallel using ThreadPoolExecutor(max_workers=5) with 9 sec timeout, first successful response is used. If all fail, dynamic local engine gives personalized output.

2. Define Architecture - By Afsal A:
Frontend: Streamlit (3 Tabs: Generate, Update, Tip)
Backend Logic: Python (BMI, Calories = weight*24/30/35, Protein = weight*1.6/2.0)
AI Layer: 5 Models Parallel Call using concurrent.futures.ThreadPoolExecutor
Database: SQLite - fitbuddy.db, Table users(name PK, plan TEXT, goal TEXT, bmi REAL, weight REAL, height REAL)
Fallback Layer: get_dynamic_plan() with random.seed(name+weight+height+microsecond) ensures different reps/sets for different persons

Data Flow Diagram:
UI -> Logic -> Gemini Parallel (5 Models) -> Fallback Dynamic Engine -> DB -> Display

Prompt Design:
"Create 7-day {goal} plan for {name}, age {age}, {weight}kg, {height}cm, BMI {bmi:.1f}, gender {gender}, intensity {intensity}, diet {diet}, avoid {allergies}. Include day-wise exercise with sets reps rest + nutrition tip + recovery tip. Indian context, short structured."
