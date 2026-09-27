FitBuddy – AI Fitness Plan Generator
A college team project built with FastAPI, Gemini AI, SQLite, HTML and CSS.
Features
Scenario 1: user enters name, age, weight, goal and intensity -> personalized 7-day plan.
Scenario 2: user submits feedback -> plan is regenerated/refined.
Scenario 3: goal-specific nutrition/recovery tip.
SQLite stores users and generated plans.
/docs exposes the FastAPI API documentation.
/health provides a deployment health check.
If GEMINI_API_KEY is unavailable or Gemini is temporarily unavailable, a built-in safe fallback keeps the application usable.
Team
Anushree P
Avinth Atchai C
Ahammed Sha
Afsal A
Run locally
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
Open http://127.0.0.1:8000.
Gemini setup
Create a Gemini API key in Google AI Studio and set it as an environment variable:
Windows PowerShell:
$env:GEMINI_API_KEY="YOUR_KEY"
macOS/Linux:
export GEMINI_API_KEY="YOUR_KEY"
Optional model override:
export GEMINI_MODEL="gemini-2.5-flash"
Never commit the API key to GitHub.
Deploy
For a service that supports a Procfile, use:
uvicorn main:app --host 0.0.0.0 --port $PORT
Set GEMINI_API_KEY in the deployment platform's Environment Variables/Secrets.
SQLite is suitable for a college demo. Some cloud platforms use ephemeral disks; if permanent production data is required, replace SQLite with a managed database or attach persistent storage.
