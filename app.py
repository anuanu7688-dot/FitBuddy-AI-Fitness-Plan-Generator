from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

APP_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("DATABASE_PATH", str(APP_DIR / "fitbuddy.db")))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

TEAM = [
    "Anushree P",
    "Avinth Atchai C",
    "Ahammed Sha",
    "Afsal A",
]

GOALS = {"weight loss", "muscle gain", "general wellness"}
INTENSITIES = {"low", "medium", "high"}

app = FastAPI(
    title="FitBuddy – AI Fitness Plan Generator",
    description=(
        "A FastAPI + Gemini + SQLite fitness planner that creates 7-day plans, "
        "refines plans from feedback, and provides nutrition/recovery tips."
    ),
    version="1.0.0",
)

HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FitBuddy | AI Fitness Plan Generator</title>
<style>
:root{
  --bg:#f4f7fb; --card:#fff; --ink:#172033; --muted:#667085;
  --primary:#2563eb; --primary2:#7c3aed; --line:#e6eaf0;
  --success:#0f9d58; --danger:#dc3545; --shadow:0 16px 45px rgba(25,35,55,.10);
}
*{box-sizing:border-box}
body{margin:0;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;
background:linear-gradient(135deg,#eef5ff,#f8f4ff 55%,#f4f7fb);color:var(--ink)}
.container{max-width:1180px;margin:auto;padding:24px}
.hero{background:linear-gradient(135deg,#111827,#263b77 55%,#6d28d9);color:#fff;
border-radius:28px;padding:34px;box-shadow:var(--shadow);position:relative;overflow:hidden}
.hero:after{content:"";position:absolute;width:260px;height:260px;border-radius:50%;
right:-90px;top:-100px;background:rgba(255,255,255,.10)}
.badges{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.badge{padding:7px 12px;border-radius:999px;background:rgba(255,255,255,.14);font-size:12px}
h1{margin:0 0 8px;font-size:clamp(30px,5vw,48px);line-height:1.05}
.hero p{max-width:760px;color:#dce5ff;font-size:16px;line-height:1.65}
.grid{display:grid;grid-template-columns:360px 1fr;gap:22px;margin-top:22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:22px;
box-shadow:0 10px 30px rgba(25,35,55,.06)}
.card h2{margin:0 0 6px;font-size:20px}.sub{color:var(--muted);font-size:13px;margin:0 0 18px}
label{font-size:13px;font-weight:700;display:block;margin:13px 0 7px}
input,select,textarea{width:100%;padding:12px 13px;border:1px solid #d9dee8;border-radius:12px;
font:inherit;background:#fff;color:var(--ink);outline:none}
input:focus,select:focus,textarea:focus{border-color:var(--primary);box-shadow:0 0 0 3px rgba(37,99,235,.10)}
button{border:0;border-radius:12px;padding:12px 16px;font-weight:800;cursor:pointer;
background:linear-gradient(135deg,var(--primary),var(--primary2));color:#fff;width:100%;
box-shadow:0 8px 18px rgba(37,99,235,.20)}
button:disabled{opacity:.55;cursor:not-allowed}
.secondary{background:#eef3ff;color:#2147a5;box-shadow:none}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.status{display:flex;align-items:center;gap:9px;margin:0 0 18px;padding:11px 13px;border-radius:12px;
background:#f6f8fb;color:#475467;font-size:13px}
.dot{width:9px;height:9px;border-radius:50%;background:#94a3b8}
.dot.ai{background:var(--success)}.dot.fallback{background:#f59e0b}
.plan-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:16px}
.plan-head h2{margin:0}.pill{font-size:12px;font-weight:800;padding:7px 10px;border-radius:999px;background:#eef3ff;color:#2147a5}
.days{display:grid;grid-template-columns:repeat(2,1fr);gap:13px}
.day{border:1px solid var(--line);border-radius:17px;padding:16px;background:#fbfcfe}
.day h3{margin:0 0 5px;font-size:16px}.focus{font-weight:800;color:#334155;font-size:13px}
.meta{color:var(--muted);font-size:12px;margin:7px 0 10px}
.day ul{padding-left:19px;margin:8px 0}.day li{margin:5px 0;font-size:13px;line-height:1.4}
.note{font-size:12px;color:#475467;background:#f4f6fa;border-radius:10px;padding:9px}
.actions{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:18px}
.tip{margin-top:16px;background:linear-gradient(135deg,#eff6ff,#f5f3ff);border:1px solid #dbe5ff}
.tip strong{display:block;margin-bottom:7px}.tip p{margin:0;line-height:1.55;color:#475467}
.footer{text-align:center;color:#667085;font-size:13px;padding:28px 10px 12px}
.footer b{color:#334155}.hidden{display:none}
.spinner{display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,.5);
border-top-color:#fff;border-radius:50%;animation:spin .7s linear infinite;vertical-align:-2px;margin-right:7px}
@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:850px){.grid{grid-template-columns:1fr}.days{grid-template-columns:1fr}}
@media(max-width:500px){.container{padding:13px}.hero{padding:25px 20px}.two,.actions{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="container">
  <section class="hero">
    <div class="badges"><span class="badge">Healthcare</span><span class="badge">Generative AI</span>
    <span class="badge">FastAPI</span><span class="badge">Gemini</span><span class="badge">SQLite</span></div>
    <h1>FitBuddy</h1>
    <p>AI Fitness Plan Generator that creates a structured 7-day workout plan, adapts it from
    user feedback, and provides a goal-specific nutrition or recovery tip.</p>
  </section>

  <div class="grid">
    <aside>
      <section class="card">
        <h2>Create your plan</h2>
        <p class="sub">Enter the required details. FitBuddy will personalize the weekly schedule.</p>
        <form id="planForm">
          <label>Name</label>
          <input id="name" required maxlength="80" placeholder="e.g. Anu">
          <div class="two">
            <div><label>Age</label><input id="age" required type="number" min="13" max="100" value="20"></div>
            <div><label>Weight (kg)</label><input id="weight" required type="number" min="25" max="300" step="0.1" value="60"></div>
          </div>
          <label>Fitness goal</label>
          <select id="goal">
            <option>weight loss</option><option>muscle gain</option><option>general wellness</option>
          </select>
          <label>Workout intensity</label>
          <select id="intensity">
            <option>low</option><option selected>medium</option><option>high</option>
          </select>
          <button id="generateBtn" type="submit">Generate 7-Day Plan</button>
        </form>
      </section>

      <section class="card" style="margin-top:18px">
        <h2>Refine with feedback</h2>
        <p class="sub">Example: “more focus on cardio” or “include more rest days”.</p>
        <textarea id="feedback" rows="4" placeholder="Tell FitBuddy what you want to change..."></textarea>
        <button id="feedbackBtn" class="secondary" style="margin-top:10px" onclick="refinePlan()">Update My Plan</button>
      </section>
    </aside>

    <main>
      <section class="card">
        <div class="status"><span id="statusDot" class="dot"></span><span id="statusText">Ready — create a plan to begin.</span></div>
        <div class="plan-head">
          <div><h2 id="welcome">Your personalized plan</h2><p class="sub" id="summary">Your 7-day plan will appear here.</p></div>
          <span class="pill" id="modePill">AI READY</span>
        </div>
        <div id="days" class="days"></div>
        <div id="empty" style="color:#667085;text-align:center;padding:45px 10px">
          <div style="font-size:42px">🏃</div>
          <b>Your fitness journey starts here.</b><br>
          Generate a plan from the form.
        </div>
      </section>

      <section class="card tip">
        <strong>🥗 Nutrition / Recovery Tip</strong>
        <p id="tipText">Choose a goal and generate a plan to receive a targeted tip.</p>
        <button class="secondary" style="margin-top:12px" onclick="getTip()">Refresh Tip</button>
      </section>
    </main>
  </div>

  <div class="footer">
    <b>Made with ♥ by Team FitBuddy</b><br>
    Anushree P · Avinth Atchai C · Ahammed Sha · Afsal A
  </div>
</div>

<script>
let currentPlan = null;

function setLoading(button, loading, label) {
  button.disabled = loading;
  button.innerHTML = loading ? '<span class="spinner"></span>Working...' : label;
}

function showStatus(message, mode="") {
  document.getElementById("statusText").textContent = message;
  const dot = document.getElementById("statusDot");
  dot.className = "dot " + (mode === "ai" ? "ai" : mode === "fallback" ? "fallback" : "");
  document.getElementById("modePill").textContent =
    mode === "ai" ? "GEMINI AI" : mode === "fallback" ? "SMART FALLBACK" : "AI READY";
}

function formData() {
  return {
    name: document.getElementById("name").value.trim(),
    age: Number(document.getElementById("age").value),
    weight: Number(document.getElementById("weight").value),
    goal: document.getElementById("goal").value,
    intensity: document.getElementById("intensity").value
  };
}

function renderPlan(data) {
  currentPlan = data;
  document.getElementById("empty").classList.add("hidden");
  document.getElementById("welcome").textContent = `Hi ${data.user.name}, here is your plan`;
  document.getElementById("summary").textContent = data.plan.summary || "Personalized 7-day schedule.";
  const days = document.getElementById("days");
  days.innerHTML = "";
  (data.plan.days || []).forEach(d => {
    const card = document.createElement("article");
    card.className = "day";
    card.innerHTML = `
      <h3>${escapeHtml(d.day || "")}</h3>
      <div class="focus">${escapeHtml(d.focus || "")}</div>
      <div class="meta">${escapeHtml(d.duration || "")}</div>
      <ul>${(d.workout || []).map(x => `<li>${escapeHtml(x)}</li>`).join("")}</ul>
      <div class="note">${escapeHtml(d.note || "")}</div>`;
    days.appendChild(card);
  });
  if (data.tip) document.getElementById("tipText").textContent = data.tip;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"
  }[c]));
}

document.getElementById("planForm").addEventListener("submit", async e => {
  e.preventDefault();
  const btn = document.getElementById("generateBtn");
  setLoading(btn, true, "Generate 7-Day Plan");
  showStatus("Building your personalized plan...");
  try {
    const res = await fetch("/api/generate-plan", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify(formData())
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Unable to generate the plan.");
    renderPlan(data);
    showStatus(data.source === "gemini" ? "Gemini AI generated your plan." : "Plan generated with the built-in fallback.", data.source);
  } catch(err) {
    showStatus(err.message);
  } finally { setLoading(btn, false, "Generate 7-Day Plan"); }
});

async function refinePlan() {
  if (!currentPlan) { showStatus("Generate a plan first."); return; }
  const feedback = document.getElementById("feedback").value.trim();
  if (!feedback) { showStatus("Please enter feedback first."); return; }
  const btn = document.getElementById("feedbackBtn");
  setLoading(btn, true, "Update My Plan");
  showStatus("Refining your plan using the feedback...");
  try {
    const res = await fetch("/api/feedback", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({user:currentPlan.user, plan:currentPlan.plan, feedback})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Unable to update the plan.");
    renderPlan(data);
    document.getElementById("feedback").value = "";
    showStatus(data.source === "gemini" ? "Plan updated by Gemini AI." : "Plan updated with the built-in fallback.", data.source);
  } catch(err) { showStatus(err.message); }
  finally { setLoading(btn, false, "Update My Plan"); }
}

async function getTip() {
  const f = formData();
  const p = currentPlan?.plan || null;
  try {
    const res = await fetch("/api/tip", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({goal:f.goal, plan:p})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Unable to get tip.");
    document.getElementById("tipText").textContent = data.tip;
  } catch(err) { document.getElementById("tipText").textContent = err.message; }
}
</script>
</body>
</html>
"""

# --------------------------- Data models ---------------------------

class UserInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=25, le=300)
    goal: str
    intensity: str


class FeedbackInput(BaseModel):
    user: dict[str, Any]
    plan: dict[str, Any]
    feedback: str = Field(min_length=2, max_length=1000)


class TipInput(BaseModel):
    goal: str
    plan: dict[str, Any] | None = None


# --------------------------- Database ---------------------------

def db_connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with db_connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                weight REAL NOT NULL,
                goal TEXT NOT NULL,
                intensity TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_json TEXT NOT NULL,
                feedback TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        conn.commit()


@app.on_event("startup")
def startup_event() -> None:
    init_db()


def save_plan(user: UserInput, plan: dict[str, Any], feedback: str | None = None) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with db_connect() as conn:
        cur = conn.execute(
            """INSERT INTO users(name, age, weight, goal, intensity, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user.name, user.age, user.weight, user.goal, user.intensity, now),
        )
        user_id = int(cur.lastrowid)
        conn.execute(
            """INSERT INTO plans(user_id, plan_json, feedback, created_at)
               VALUES (?, ?, ?, ?)""",
            (user_id, json.dumps(plan, ensure_ascii=False), feedback, now),
        )
        conn.commit()
        return user_id


# --------------------------- Validation ---------------------------

def validate_user(data: UserInput) -> None:
    data.goal = data.goal.strip().lower()
    data.intensity = data.intensity.strip().lower()
    if data.goal not in GOALS:
        raise HTTPException(status_code=400, detail=f"Goal must be one of: {', '.join(sorted(GOALS))}.")
    if data.intensity not in INTENSITIES:
        raise HTTPException(status_code=400, detail="Intensity must be low, medium, or high.")


# --------------------------- Built-in fallback ---------------------------

def fallback_plan(user: UserInput, feedback: str = "") -> dict[str, Any]:
    goal = user.goal.lower()
    intensity = user.intensity.lower()

    volume = {
        "low": ("20–30 min", 2),
        "medium": ("30–45 min", 3),
        "high": ("45–60 min", 4),
    }[intensity]

    if goal == "weight loss":
        themes = [
            ("Full Body + Cardio", ["Brisk walk", "Bodyweight squats", "Wall/incline push-ups", "Glute bridges"]),
            ("Cardio + Core", ["Brisk walk/jog intervals", "Marching high knees", "Dead bug", "Plank"]),
            ("Lower Body", ["Squats", "Reverse lunges", "Glute bridges", "Calf raises"]),
            ("Upper Body + Cardio", ["Incline push-ups", "Backpack rows", "Shoulder taps", "Easy cardio"]),
            ("Active Cardio", ["Brisk walk", "Cycling or dancing", "Low-impact intervals", "Stretching"]),
            ("Full Body Circuit", ["Squats", "Incline push-ups", "Backpack rows", "Mountain climbers"]),
            ("Recovery", ["Easy walk", "Gentle mobility", "Breathing exercises"]),
        ]
        summary = "A balanced week combining strength, cardio and recovery for gradual fitness progress."
        tip = "Build meals around vegetables, protein-rich foods, whole grains and water. Avoid aggressive calorie restriction."
    elif goal == "muscle gain":
        themes = [
            ("Full Body Strength", ["Squats", "Push-ups", "Backpack rows", "Glute bridges"]),
            ("Lower Body Strength", ["Squats", "Reverse lunges", "Hip hinges", "Calf raises"]),
            ("Recovery", ["Easy walk", "Mobility", "Gentle stretching"]),
            ("Upper Body Strength", ["Push-ups", "Backpack rows", "Pike push-ups", "Shoulder taps"]),
            ("Lower Body + Core", ["Split squats", "Glute bridges", "Hip hinges", "Plank"]),
            ("Full Body Strength", ["Squats", "Push-ups", "Rows", "Lunges"]),
            ("Rest + Mobility", ["Easy walk", "Full-body mobility", "Relaxed stretching"]),
        ]
        summary = "A strength-focused week with recovery days to support progressive training."
        tip = "Include a protein source in each main meal and eat enough overall to support training and recovery."
    else:
        themes = [
            ("Full Body Fitness", ["Squats", "Incline push-ups", "Glute bridges", "Brisk walk"]),
            ("Cardio", ["Brisk walk", "Cycling or dancing", "Mobility"]),
            ("Strength + Core", ["Squats", "Backpack rows", "Dead bug", "Plank"]),
            ("Mobility", ["Hip mobility", "Shoulder mobility", "Gentle yoga", "Easy walk"]),
            ("Full Body Circuit", ["Lunges", "Push-ups", "Rows", "Marching high knees"]),
            ("Outdoor Activity", ["Walking", "Cycling or sport", "Gentle stretching"]),
            ("Recovery", ["Easy walk", "Breathing", "Gentle full-body stretching"]),
        ]
        summary = "A sustainable week combining movement, strength, cardio, mobility and recovery."
        tip = "Aim for balanced meals, adequate hydration, regular sleep and a variety of fruits, vegetables and protein foods."

    days = []
    for i, (focus, exercises) in enumerate(themes, start=1):
        if focus in {"Recovery", "Rest + Mobility", "Mobility"}:
            duration = "20–30 min"
            note = "Keep the effort comfortable. Stop if you feel pain or unusual symptoms."
        else:
            duration = volume[0]
            note = f"Complete {volume[1]} comfortable rounds when appropriate; rest between exercises."
        days.append({
            "day": f"Day {i}",
            "focus": focus,
            "duration": duration,
            "workout": exercises,
            "note": note,
        })

    if feedback:
        low = feedback.lower()
        if "cardio" in low:
            days[0]["workout"].insert(0, "10–15 min extra easy-to-moderate cardio")
            days[4]["focus"] = "Extra Cardio + Mobility"
        if "rest" in low or "recovery" in low:
            days[2]["focus"] = "Rest & Recovery"
            days[2]["workout"] = ["Easy walk", "Gentle mobility", "Relaxed breathing"]
            days[6]["focus"] = "Rest & Recovery"
            days[6]["workout"] = ["Gentle stretching", "Easy walk if comfortable"]
        if "strength" in low:
            days[0]["workout"].append("Optional resistance-band or backpack strength work")
            days[5]["focus"] = "Strength Focus"

    return {"summary": summary, "days": days, "tip": tip}


# --------------------------- Gemini integration ---------------------------

def extract_json(text: str) -> dict[str, Any]:
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "", 1).replace("```", "", 1).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Gemini did not return JSON.")
    return json.loads(cleaned[start:end + 1])


def call_gemini(prompt: str) -> dict[str, Any] | None:
    if not GEMINI_API_KEY:
        return None

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.45,
            "maxOutputTokens": 4000,
            "responseMimeType": "application/json",
        },
    }

    try:
        response = requests.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=35,
        )
        response.raise_for_status()
        body = response.json()
        text = body["candidates"][0]["content"]["parts"][0]["text"]
        return extract_json(text)
    except (requests.RequestException, KeyError, IndexError, ValueError, json.JSONDecodeError):
        # The application remains usable even when Gemini is unavailable,
        # rate-limited, or the API key is not configured.
        return None


def ai_plan(user: UserInput, feedback: str = "") -> dict[str, Any] | None:
    feedback_text = feedback or "No previous feedback. Create the initial plan."
    prompt = f"""
You are FitBuddy, a careful fitness-planning assistant.
Create a safe, beginner-friendly 7-day fitness plan from these details:
name={user.name}, age={user.age}, weight_kg={user.weight}, goal={user.goal},
intensity={user.intensity}, feedback={feedback_text}

Return ONLY valid JSON with exactly this structure:
{{
  "summary": "one short paragraph",
  "days": [
    {{
      "day": "Day 1",
      "focus": "short focus",
      "duration": "20-60 min",
      "workout": ["exercise 1", "exercise 2", "exercise 3", "exercise 4"],
      "note": "short safety/recovery note"
    }}
  ],
  "tip": "one concise nutrition or recovery tip"
}}

Rules:
- Include exactly 7 day objects, Day 1 through Day 7.
- Match the selected goal and intensity.
- Include at least one recovery/rest-focused day.
- Do not prescribe medication, supplements, starvation, dehydration, or dangerous exercise.
- Do not make medical diagnoses.
- Keep advice practical and general.
- If feedback requests more cardio, add cardio emphasis.
- If feedback requests more rest/recovery, add recovery emphasis.
- Keep exercise names simple and suitable for a general user.
"""
    result = call_gemini(prompt)
    if not result:
        return None
    try:
        days = result.get("days", [])
        if len(days) != 7:
            return None
        for i, day in enumerate(days, 1):
            day["day"] = f"Day {i}"
            day.setdefault("focus", "Fitness")
            day.setdefault("duration", "30–45 min")
            day.setdefault("workout", [])
            day.setdefault("note", "Exercise at a comfortable level and rest when needed.")
        result.setdefault("summary", "A personalized 7-day fitness plan.")
        result.setdefault("tip", "Prioritize balanced meals, hydration and adequate recovery.")
        return result
    except Exception:
        return None


# --------------------------- API routes ---------------------------

@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return HTML_PAGE


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "FitBuddy",
        "gemini_configured": bool(GEMINI_API_KEY),
        "model": GEMINI_MODEL,
        "database": str(DB_PATH),
    }


@app.post("/api/generate-plan")
def generate_plan(data: UserInput) -> dict[str, Any]:
    validate_user(data)
    plan = ai_plan(data)
    source = "gemini" if plan else "fallback"
    if not plan:
        plan = fallback_plan(data)
    save_plan(data, plan)
    return {"user": data.model_dump(), "plan": plan, "tip": plan["tip"], "source": source}


@app.post("/api/feedback")
def feedback(data: FeedbackInput) -> dict[str, Any]:
    if not data.feedback.strip():
        raise HTTPException(status_code=400, detail="Feedback cannot be empty.")

    try:
        user = UserInput(**data.user)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Saved user details are invalid.") from exc

    validate_user(user)

    updated = ai_plan(user, data.feedback)
    source = "gemini" if updated else "fallback"
    if not updated:
        updated = fallback_plan(user, data.feedback)

    save_plan(user, updated, data.feedback)
    return {"user": user.model_dump(), "plan": updated, "tip": updated["tip"], "source": source}


@app.post("/api/tip")
def nutrition_tip(data: TipInput) -> dict[str, str]:
    goal = data.goal.strip().lower()
    if goal not in GOALS:
        raise HTTPException(status_code=400, detail="Invalid fitness goal.")

    if GEMINI_API_KEY:
        prompt = f"""
Give one concise, practical nutrition or recovery tip for the fitness goal "{goal}".
Do not diagnose conditions, prescribe medication, or recommend extreme dieting.
Return ONLY JSON: {{"tip":"..."}}
"""
        result = call_gemini(prompt)
        if result and isinstance(result.get("tip"), str) and result["tip"].strip():
            return {"tip": result["tip"].strip(), "source": "gemini"}

    tips = {
        "weight loss": "Build meals around vegetables, protein-rich foods, whole grains and water; avoid aggressive calorie restriction.",
        "muscle gain": "Include a protein source in each main meal and eat enough overall to support training and recovery.",
        "general wellness": "Prioritize balanced meals, hydration, regular sleep and a variety of fruits and vegetables.",
    }
    return {"tip": tips[goal], "source": "fallback"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
