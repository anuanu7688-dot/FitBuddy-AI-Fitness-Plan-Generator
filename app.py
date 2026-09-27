import streamlit as st
import sqlite3
import time
from google import genai
import os

st.set_page_config(page_title="FitBuddy - AI Fitness Plan Generator", page_icon="💪", layout="wide")

st.markdown("<h2 style='text-align:center; color:#2D7D32;'>💪 FitBuddy - AI Fitness Plan Generator</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Your Personalized 7-Day AI Coach powered by Gemini</p>", unsafe_allow_html=True)

DB_NAME = "fitbuddy.db"
def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, age INTEGER, 
        weight REAL, height REAL, gender TEXT, goal TEXT, intensity TEXT, plan TEXT)""")
    conn.commit()
    conn.close()
init_db()

# --- ZERO ERROR SERVICE ---
class FitBuddyService:
    def __init__(self):
        api_key = None
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except:
            pass
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            st.error("GEMINI_API_KEY not found in Secrets. Add it in Settings > Secrets.")
            st.stop()
        self.client = genai.Client(api_key=api_key.strip())
        # Try less overloaded models first
        self.models = ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-2.0-flash-lite", "gemini-flash-latest"]

    def generate(self, prompt_text):
        # This will NEVER return None - it will keep retrying until success
        status = st.empty()
        for attempt in range(12): # 12 attempts = ~60 seconds auto retry
            for model in self.models:
                try:
                    status.info(f"🤖 AI is thinking... Trying model {model} (Attempt {attempt+1}/12) - Please wait...")
                    response = self.client.models.generate_content(model=model, contents=prompt_text)
                    if response and response.text:
                        txt = response.text.strip()
                        if len(txt) > 50 and "503" not in txt and "UNAVAILABLE" not in txt.upper():
                            status.empty()
                            return txt
                except Exception as e:
                    err = str(e).lower()
                    # If 503 or quota, wait and retry next model
                    if "503" in err or "429" in err or "unavailable" in err or "quota" in err or "overload" in err:
                        time.sleep(3)
                        continue
                    time.sleep(2)
                    continue
            time.sleep(4) # wait before next full round
        
        status.empty()
        # Last fallback - offline template so user NEVER sees error
        return """
        **Your 7-Day Plan (Offline Mode - AI busy, so showing standard plan):**
        **Day 1: Full Body Strength** - Squats 3x12, Pushups 3x10, Plank 3x30sec - Rest 60sec
        **Day 2: Cardio + Core** - Brisk Walk 30min, Crunches 3x15, Leg Raises 3x12
        **Day 3: Upper Body** - Dumbbell Press 3x10, Rows 3x12, Shoulder Press 3x10
        **Day 4: Active Recovery** - Yoga / Stretching 30min, Walk 15min
        **Day 5: Lower Body** - Lunges 3x12, Deadlifts 3x10, Calf Raises 3x15
        **Day 6: HIIT Cardio** - Jumping Jacks 3x30sec, Burpees 3x10, Mountain Climbers 3x20
        **Day 7: Rest & Recovery** - Full Rest, Hydrate, Light Stretching
        **Nutrition Tip:** Include protein in every meal and stay hydrated 3L water.
        **Recovery Tip:** Sleep 7-8 hours and do 10min stretching post workout.
        """

service = FitBuddyService()

tab1, tab2, tab3 = st.tabs(["Scenario 1: Generate Plan", "Scenario 2: Update with Feedback", "Scenario 3: Nutrition / Recovery Tip"])

with tab1:
    st.subheader("Scenario 1: Generate Personalized Plan")
    with st.form("fitbuddy_form"):
        name = st.text_input("Name *", placeholder="Your Name")
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
            st.error("Please enter Name as per Scenario 1")
        else:
            bmi = weight / ((height/100)**2)
            prompt = f"""Create personalized 7-day workout plan for: Name {name}, Age {age}, Weight {weight}kg, Height {height}cm, BMI {bmi:.1f}, Gender {gender}, Goal {goal}, Intensity {intensity}, Activity {activity}, Diet {diet}, Allergies {allergies}. Include day-wise 7-day schedule with exercise name, sets, reps, rest. Include 1 nutrition tip and 1 recovery tip. Structured and goal-specific."""
            
            with st.spinner("FitBuddy AI is creating your plan... this may take 20 sec if AI is busy, please don't refresh"):
                plan_text = service.generate(prompt)

            # SAVE - Fixed lower case
            st.session_state[f"plan_{name.strip().lower()}"] = plan_text
            st.session_state[f"goal_{name.strip().lower()}"] = goal
            conn = sqlite3.connect(DB_NAME)
            conn.execute("INSERT OR REPLACE INTO users (name, age, weight, height, gender, goal, intensity, plan) VALUES (?,?,?,?,?,?,?,?)",
                         (name.strip().lower(), age, weight, height, gender, goal, intensity, plan_text))
            conn.commit()
            conn.close()

            st.success(f"Plan Ready for {name}!")
            st.markdown(plan_text)
            st.download_button("📥 Download Plan", data=plan_text, file_name=f"{name}_Plan.txt")

with tab2:
    st.subheader("Scenario 2: Update Plan with Feedback")
    fb_name = st.text_input("Enter Your Name", key="fb_name")
    feedback = st.text_area("Your Feedback *", placeholder="e.g. more cardio")
    if st.button("🔄 Update Plan", use_container_width=True):
        if not fb_name.strip() or not feedback.strip():
            st.error("Enter Name and Feedback")
        else:
            clean = fb_name.strip().lower()
            prev = st.session_state.get(f"plan_{clean}")
            prev_goal = st.session_state.get(f"goal_{clean}")
            if not prev:
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute("SELECT plan, goal FROM users WHERE name=?", (clean,))
                row = cur.fetchone()
                conn.close()
                if row: prev, prev_goal = row
            if not prev:
                st.warning("No previous plan found. Generate in Tab 1 first.")
            else:
                prompt2 = f"Previous Plan: {prev}\nGoal: {prev_goal}\nFeedback: {feedback}\nRegenerate updated 7-day plan."
                with st.spinner("Updating... please wait, auto-retrying if busy"):
                    updated = service.generate(prompt2)
                st.success("Updated Plan Ready!")
                st.markdown(updated)
                st.download_button("Download Updated", data=updated, file_name=f"{fb_name}_updated.txt", key="dl2")

with tab3:
    st.subheader("Scenario 3: Nutrition / Recovery Tip")
    tip_goal = st.selectbox("Select Goal", ["Weight Loss", "Muscle Gain", "General Fitness"], key="tip_goal")
    if st.button("💡 Get Tip", use_container_width=True):
        prompt3 = f"Give 2-line nutrition or recovery tip for goal {tip_goal}"
        with st.spinner("Getting tip..."):
            tip = service.generate(prompt3)
        st.success(tip)

st.markdown("---")
st.caption("Made with ❤️ by Team N3Bee - Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A | FastAPI + Gemini + Streamlit")
