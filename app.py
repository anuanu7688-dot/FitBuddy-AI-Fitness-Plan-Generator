import streamlit as st
import sqlite3
import time
from google import genai
import os

# --- PAGE CONFIG - Standard ---
st.set_page_config(
    page_title="FitBuddy - AI Fitness Plan Generator",
    page_icon="💪",
    layout="wide"
)

# --- CUSTOM CSS - Classy Look ---
st.markdown("""
<style>
.main-header {text-align:center; color:#1B5E20; font-weight:700;}
.card {background-color:#F1F8E9; padding:15px; border-radius:10px; border-left:5px solid #2E7D32;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>💪 FitBuddy - AI Fitness Plan Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Your Personalized 7-Day AI Coach powered by Gemini</p>", unsafe_allow_html=True)

# --- DATABASE - Fixed to lower case everywhere ---
DB_NAME = "fitbuddy.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            weight REAL,
            height REAL,
            gender TEXT,
            goal TEXT,
            intensity TEXT,
            plan TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- GEMINI SERVICE - Classy Standard - NO API KEY PROMPT ---
class FitBuddyService:
    def __init__(self):
        # Get key only from secrets/env, never ask user
        api_key = None
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", None)
        except:
            api_key = None
        
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY", None)

        if not api_key:
            st.error("⚠️ GEMINI_API_KEY not set in Streamlit Secrets. Please add it in Deploy Settings > Secrets.")
            st.stop()
        
        self.client = genai.Client(api_key=api_key.strip())
        self.models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]

    def generate(self, prompt_text):
        """Auto-retry for 503, never saves error"""
        for _ in range(3):
            for model in self.models:
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt_text
                    )
                    if response.text and "503" not in response.text and "UNAVAILABLE" not in response.text.upper():
                        return response.text
                except Exception:
                    time.sleep(1)
                    continue
            time.sleep(2)
        return None

service = FitBuddyService()

# --- TABS AS PER REQUIREMENT ---
tab1, tab2, tab3 = st.tabs([
    "Scenario 1: Generate Plan", 
    "Scenario 2: Update with Feedback", 
    "Scenario 3: Nutrition / Recovery Tip"
])

# ============ TAB 1: GENERATE PLAN ============
with tab1:
    st.subheader("Scenario 1: Generate Personalized Plan")
    with st.form("fitbuddy_form"):
        name = st.text_input("Name *", placeholder="As per Scenario 1")
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", 10, 100, 23)
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 60.0)
            intensity = st.selectbox("Preferred Workout Intensity *", ["Low", "Medium", "High"])
        with c2:
            height = st.number_input("Height (cm)", 100.0, 250.0, 165.0)
            gender = st.selectbox("Gender", ["Female", "Male", "Other"])
            activity = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
        
        goal = st.selectbox("Fitness Goal *", ["Weight Loss", "Muscle Gain", "General Fitness"])
        diet = st.radio("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan"], horizontal=True)
        allergies = st.text_input("Allergies / Food to Avoid (Optional)")
        
        submit = st.form_submit_button("🚀 Generate My 7-Day Plan", use_container_width=True)

    if submit:
        if not name.strip():
            st.error("Please enter Name as per Scenario 1 requirement")
        else:
            bmi = weight / ((height/100)**2)
            # FINAL PROMPT - Uses ALL inputs to satisfy 100%
            prompt = f"""
            You are FitBuddy AI Coach. Create a personalized 7-day workout plan for:
            Name: {name}, Age: {age}, Weight: {weight}kg, Height: {height}cm, Gender: {gender}, BMI: {bmi:.1f},
            Fitness Goal: {goal}, Preferred Intensity: {intensity}, Activity Level: {activity}, Diet: {diet}, Allergies: {allergies}

            Requirements:
            1. Day-by-day 7-day schedule tailored to goal {goal} and intensity {intensity}
            2. For each day: Exercise Name, Sets, Reps, Rest Time
            3. Include exactly 1 Nutrition Tip relevant to {goal} and diet {diet}
            4. Include exactly 1 Recovery Tip
            5. Keep structured, clean and motivational.
            """
            
            with st.spinner("FitBuddy AI is building your plan..."):
                plan_text = service.generate(prompt)
            
            if not plan_text:
                st.error("AI is busy (503). Please wait 15 seconds and click Generate again. Error not saved.")
            else:
                # Save to both Session and SQLite (lower case)
                st.session_state[f"plan_{name.strip().lower()}"] = plan_text
                st.session_state[f"goal_{name.strip().lower()}"] = goal

                conn = sqlite3.connect(DB_NAME)
                conn.execute("INSERT OR REPLACE INTO users (name, age, weight, height, gender, goal, intensity, plan) VALUES (?,?,?,?,?,?,?,?)",
                             (name.strip().lower(), age, weight, height, gender, goal, intensity, plan_text))
                conn.commit()
                conn.close()

                st.success(f"Plan Ready for {name}!")
                st.markdown(f"<div class='card'>{plan_text}</div>", unsafe_allow_html=True)
                st.download_button("📥 Download Plan", data=plan_text, file_name=f"{name}_FitBuddy_Plan.txt")

# ============ TAB 2: FEEDBACK ============
with tab2:
    st.subheader("Scenario 2: Update Plan with Feedback")
    st.caption("Example feedback: 'more focus on cardio' or 'include more rest days'")
    fb_name = st.text_input("Enter Your Name", key="fb_name")
    feedback = st.text_area("Your Feedback *", placeholder="e.g. more cardio, less leg day")

    if st.button("🔄 Update Plan with AI", use_container_width=True):
        if not fb_name.strip() or not feedback.strip():
            st.error("Please enter both Name and Feedback")
        else:
            clean_name = fb_name.strip().lower()
            prev_plan = st.session_state.get(f"plan_{clean_name}")
            prev_goal = st.session_state.get(f"goal_{clean_name}")

            if not prev_plan:
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute("SELECT plan, goal FROM users WHERE name=?", (clean_name,))
                row = cur.fetchone()
                conn.close()
                if row:
                    prev_plan, prev_goal = row

            if not prev_plan:
                st.warning("No previous plan found. Please generate plan in Tab 1 first.")
            else:
                prompt2 = f"Previous Plan: {prev_plan}\nGoal: {prev_goal}\nUser Feedback: {feedback}\nRegenerate updated 7-day plan based on feedback, keep same structure."
                with st.spinner("Regenerating based on your feedback..."):
                    updated = service.generate(prompt2)
                if not updated:
                    st.error("AI busy, try again after 15 sec")
                else:
                    st.success("Updated Plan!")
                    st.markdown(updated)
                    st.download_button("📥 Download Updated Plan", data=updated, file_name=f"{fb_name}_updated.txt", key="dl2")

# ============ TAB 3: TIP ============
with tab3:
    st.subheader("Scenario 3: Nutrition / Recovery Tip")
    tip_goal = st.selectbox("Select Fitness Goal", ["Weight Loss", "Muscle Gain", "General Fitness"], key="tip_goal")
    if st.button("💡 Get Tip", use_container_width=True):
        prompt3 = f"Give a concise and relevant 2-line nutrition or recovery tip for fitness goal: {tip_goal}. Example: 'include protein in your post-workout meal' for muscle gain."
        with st.spinner("Getting tip..."):
            tip = service.generate(prompt3)
        if tip:
            st.success(tip)
        else:
            st.error("AI busy, click again")

# --- FOOTER AS PER REQUIREMENT ---
st.markdown("---")
st.caption("Made with ❤️ by Team N3Bee - Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A | FastAPI + Gemini + Streamlit")
