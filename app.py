import streamlit as st
import sqlite3
import time
from google import genai

st.set_page_config(page_title="FitBuddy - AI Fitness Coach", page_icon="💪", layout="wide")

# --- Sidebar - User enters own key ---
st.sidebar.title("🔑 Setup")
st.sidebar.markdown("Enter your free Gemini key to use the app")
st.sidebar.link_button("Get Free API Key", "https://aistudio.google.com/app/apikey")

user_api_key = st.sidebar.text_input("Your Gemini API Key *", type="password", placeholder="AIzaSy...")

if not user_api_key:
    st.title("💪 FitBuddy - AI Fitness Plan Generator")
    st.info("👈 Please enter your Gemini API Key in the left sidebar to start. Your key is safe, it stays only in your session.")
    st.stop()

# --- DB ---
DB_NAME = "fitbuddy.db"
conn = sqlite3.connect(DB_NAME)
conn.execute("CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY, plan TEXT, goal TEXT)")
conn.commit()
conn.close()

# --- AI Function with NEW 2026 Models ---
def generate_plan(prompt_text):
    client = genai.Client(api_key=user_api_key.strip())
    # Try new models in order - 2.0-flash is stable in 2026
    models_to_try = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash"]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text
            )
            if response and response.text and len(response.text) > 20:
                return response.text.strip()
        except Exception as e:
            err = str(e).lower()
            if "404" in err or "not found" in err:
                continue # try next model
            if "429" in err or "quota" in err:
                st.error("Your free quota finished. Create new API key from AI Studio.")
                return None
            time.sleep(1)
            continue

    st.error("AI is busy (503). Please wait 15 seconds and click Generate again.")
    return None

st.markdown("<h2 style='text-align:center'>💪 FitBuddy - AI Fitness Plan Generator</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Your Personalized 7-Day AI Coach</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Scenario 1: Generate Plan", "Scenario 2: Update with Feedback", "Scenario 3: Nutrition / Recovery Tip"])

with tab1:
    st.subheader("Scenario 1: Generate Personalized Plan")
    with st.form("form1"):
        name = st.text_input("Name *", placeholder="Your Name")
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", 10, 100, 21)
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 60.0)
            intensity = st.selectbox("Preferred Workout Intensity *", ["Low", "Medium", "High"])
        with c2:
            height = st.number_input("Height (cm)", 100.0, 250.0, 164.97)
            gender = st.selectbox("Gender", ["Female", "Male", "Other"])
            activity = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
        goal = st.selectbox("Fitness Goal *", ["Weight Loss", "Muscle Gain", "General Fitness"])
        diet = st.radio("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan"], horizontal=True)
        allergies = st.text_input("Allergies / Foods to Avoid (Optional)")
        submit = st.form_submit_button("🚀 Generate My 7-Day Plan", use_container_width=True)

    if submit:
        if not name.strip():
            st.error("Enter Name")
        else:
            bmi = weight / ((height/100)**2)
            prompt = f"Create personalized 7-day workout plan for: Name={name}, Age={age}, Weight={weight}kg, Height={height}cm, BMI={bmi:.1f}, Gender={gender}, Goal={goal}, Intensity={intensity}, Activity={activity}, Diet={diet}, Avoid={allergies}. Include day-wise exercise with sets reps rest, plus 1 nutrition tip and 1 recovery tip. Keep short and structured."
            with st.spinner("FitBuddy AI is creating your plan..."):
                plan = generate_plan(prompt)
            if plan:
                st.session_state[f"plan_{name.lower().strip()}"] = plan
                st.session_state[f"goal_{name.lower().strip()}"] = goal
                conn = sqlite3.connect(DB_NAME)
                conn.execute("INSERT OR REPLACE INTO users VALUES (?,?,?)", (name.lower().strip(), plan, goal))
                conn.commit()
                conn.close()
                st.success(f"Plan Ready for {name}!")
                st.markdown(plan)
                st.download_button("📥 Download Plan", plan, file_name=f"{name}_plan.txt")

with tab2:
    st.subheader("Scenario 2: Update Plan with Feedback")
    fb_name = st.text_input("Enter Your Name *", key="fb_name2")
    feedback = st.text_area("Your Feedback *", placeholder="e.g. more cardio, less weights, knee pain")
    if st.button("🔄 Update Plan", use_container_width=True):
        clean = fb_name.lower().strip()
        prev = st.session_state.get(f"plan_{clean}")
        if not prev:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("SELECT plan FROM users WHERE name=?", (clean,))
            row = cur.fetchone()
            conn.close()
            if row: prev = row[0]
        if not prev:
            st.warning("No previous plan found. Generate in Tab 1 first.")
        else:
            prompt2 = f"Update this fitness plan based on user feedback '{feedback}'. Previous plan: {prev}. Keep 7-day format with sets reps rest + nutrition tip + recovery tip."
            with st.spinner("Updating plan..."):
                updated = generate_plan(prompt2)
            if updated:
                st.success("Updated Plan Ready!")
                st.markdown(updated)
                st.download_button("📥 Download Updated", updated, file_name=f"{fb_name}_updated.txt", key="dl2")

with tab3:
    st.subheader("Scenario 3: Nutrition / Recovery Tip")
    tip_goal = st.selectbox("Select Goal", ["Weight Loss", "Muscle Gain", "General Fitness"], key="tip_goal")
    tip_type = st.radio("Tip Type", ["Nutrition Tip", "Recovery Tip"], horizontal=True)
    if st.button("💡 Get Tip", use_container_width=True):
        prompt3 = f"Give 2-3 line expert {tip_type} for goal {tip_goal}. Indian diet friendly, practical."
        with st.spinner("Getting tip..."):
            tip = generate_plan(prompt3)
        if tip:
            st.info(tip)

st.markdown("---")
st.caption("Made with ❤️ by Team N3Bee - Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A | FastAPI + Gemini + Streamlit")
