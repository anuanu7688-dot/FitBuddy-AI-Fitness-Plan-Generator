# 5.Project Development Phase
Assigned: Anushree P (app.py Main Logic), Avinth Atchai C (Core Functionalities + UI), Ahammed Sha (Backend + Templates)

1. Main Logic app.py - By Anushree P:
Full code uploaded as app.py in this same folder. Contains 3 scenarios.

2. Core Functionalities - By Avinth Atchai C:
get_dynamic_plan() - Calculates BMI, Calories, Protein based on weight/height/goal. Uses random seed with microsecond so different output for different person and even same person clicks twice.
generate_fast() - Calls 5 models parallel with ThreadPoolExecutor, fastest wins.

3. FastAPI Backend - By Ahammed Sha:
Routing: Tab1=/generate, Tab2=/update, Tab3=/tip. Same logic implemented in Streamlit backend (approved alternative).

4. UI Design - By Avinth Atchai C:
3 Tabs, Sidebar API Key, Download Button, Indian diet options.

5. Dynamic Templates (Jinja2) - By Ahammed Sha:
Used f-string dynamic template: f"Plan for {name} | BMI {bmi} | Cal {cal} | Protein {prot}g | Day1: {d1}" Changes for every user, no static output.

Main Code File: app.py
Requirements: requirements.txt
