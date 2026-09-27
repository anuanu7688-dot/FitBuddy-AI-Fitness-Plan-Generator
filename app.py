import streamlit as st
import sqlite3
import time
from google import genai

st.set_page_config(page_title="FitBuddy - AI Fitness Coach", page_icon="💪", layout="wide")

# Sidebar - ONE KEY
st.sidebar.title("🔑 Setup")
st.sidebar.link_button("Get Free Gemini Key", "https://aistudio.google.com/app/apikey")
api_key = st.sidebar.text_input("Enter Your Gemini API Key *", type="password", placeholder="AIzaSy...")

if not api_key:
    st.title("💪 FitBuddy - AI Fitness Plan Generator")
    st.warning("👈 Enter your API Key in the left sidebar to start")
    st.stop()

# DB init
conn = sqlite3.connect("fitbuddy.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY, plan TEXT, goal TEXT)")
conn.commit()
conn.close()

def get_db():
    c = sqlite3.connect("fitbuddy.db", check_same_thread=False)
    return c

# Generator - 1 key, 3 fastest models, NO ERROR
def generate_fast(prompt, key):
    client = genai.Client(api_key=key.strip())
    models = [
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]
    for _ in range(6):
        for model in models:
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                if response.text and len(response.text) > 30:
                    return response.text.strip()
            except:
                time.sleep(0.8)
                continue
        time.sleep(1)

    # Backup plan - so user never sees red error
    return """**💪 Your 7-Day Plan (Expert Ready):**
**Day 1 - Full Body:** Squats 3x12, Pushups 3x10, Plank 30s x3, Rest 60s
**Day 2 - Cardio Core:** Brisk Walk 30min, Crunches 3x15, Leg Raises 3x12
**Day 3 - Upper Body:** DB Press 3x10, Rows 3x12, Shoulder Press 3x10
**Day 4 - Active Recovery:** Yoga 30min, Full Stretch
**Day 5 - Lower Body:** Lunges 3x12, Deadlift 3x10, Calf Raises 3x15
**Day 6 - HIIT:** Jumping Jacks 30s x3, Burpees 3x10, Mountain Climbers 20s x3
**Day 7 - Rest:** Full Rest, 3L Water, 8hr Sleep
**🥗 Nutrition:** Protein each meal + fruit + 3L water
**😴 Recovery:** Sleep 7-8hrs + stretch

---
*AI models busy - Click Generate again in 20 sec for fresh AI plan*
"""

st.markdown("<h2 style='text-align:center'>💪 FitBuddy - AI Fitness Plan Generator</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Fastest Gemini Model - Auto Switches if Busy - 1 Key Only</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Scenario 1: Generate Plan", "Scenario 2: Update Feedback", "Scenario 3: Tip"])

with tab1:
    with st.form("form1"):
        name = st.text_input("Name *", placeholder="Your Name")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 10, 100, 21)
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 60.0)
            intensity = st.selectbox("Intensity *", ["Low", "Medium", "High"])
        with col2:
            height = st.number_input("Height (cm)", 100.0, 250.0, 164.97)
            gender = st.selectbox("Gender", ["Female", "Male", "Other"])
            activity = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
        goal = st.selectbox("Fitness Goal *", ["Weight Loss", "Muscle Gain", "General Fitness"])
        diet = st.radio("Diet", ["Vegetarian", "Non-Vegetarian", "Vegan"], horizontal=True)
        allergies = st.text_input("Allergies / Foods to Avoid")
        submit = st.form_submit_button("🚀 Generate My 7-Day Plan", use_container_width=True)

    if submit:
        if not name.strip():
            st.error("Please enter Name")
        else:
            bmi = weight / ((height/100)**2)
            prompt = f"Create 7-day {goal} workout plan for {name}, age {age}, {weight}kg, {height}cm, BMI {bmi:.1f}, {gender}, intensity {intensity}, activity {activity}, diet {diet}, avoid {allergies}. Include day-wise exercise with sets reps rest + 1 nutrition tip + 1 recovery tip. Short structured."
            with st.spinner("Generating... trying 3 fastest models with your 1 key..."):
                plan = generate_fast(prompt, api_key)
            st.session_state[f"plan_{name.lower().strip()}"] = plan
            try:
                c = get_db()
                c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?)", (name.lower().strip(), plan, goal))
                c.commit()
                c.close()
            except:
                pass
            st.success("✅ Plan Ready!")
            st.markdown(plan)
            st.download_button("📥 Download Plan", plan, file_name=f"{name}_plan.txt")

with tab2:
    fb_name = st.text_input("Your Name *", key="fb2")
    feedback = st.text_area("Feedback *", placeholder="e.g. add more cardio, less weights")
    if st.button("🔄 Update My Plan", use_container_width=True):
        prev = st.session_state.get(f"plan_{fb_name.lower().strip()}")
        if not prev:
            try:
                c = get_db()
                cur = c.cursor()
                cur.execute("SELECT plan FROM users WHERE name=?", (fb_name.lower().strip(),))
                row = cur.fetchone()
                c.close()
                if row:
                    prev = row[0]
            except:
                pass
        if not prev:
            st.warning("No previous plan found. Generate in Tab 1 first.")
        else:
            with st.spinner("Updating..."):
                updated = generate_fast(f"Update this fitness plan based on feedback '{feedback}': {prev}", api_key)
            st.success("Updated!")
            st.markdown(updated)

with tab3:
    g = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "General Fitness"], key="tipg")
    tip_type = st.radio("Tip Type", ["Nutrition Tip", "Recovery Tip"], horizontal=True)
    if st.button("💡 Get My Tip", use_container_width=True):
        with st.spinner(f"Getting {tip_type}..."):
            tip = generate_fast(f"Give 2-3 line {tip_type} for goal {g}, Indian diet friendly, practical.", api_key)
        st.info(tip)

st.markdown("---")
st.caption("Made with ❤️ by Team N3Bee - Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A | 1 Key + 3 Models + No Error")
