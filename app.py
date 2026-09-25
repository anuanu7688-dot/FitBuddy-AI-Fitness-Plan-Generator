import streamlit as st
import sqlite3
from google import genai

st.set_page_config(page_title="FitBuddy - AI Fitness Plan Generator", page_icon="💪", layout="centered")

st.markdown("<h2 style='text-align:center; color:#2D7D32;'>💪 FitBuddy - AI Fitness Plan Generator</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Personalized workout plans & nutrition tips using Gemini AI</p>", unsafe_allow_html=True)

# --- DB ---
try:
    c = sqlite3.connect("fitbuddy.db")
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, weight REAL, height REAL, goal TEXT, intensity TEXT, plan TEXT)")
    c.commit()
    c.close()
except:
    pass

# --- API Key ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
    if not api_key:
        st.warning("Add GEMINI_API_KEY in Secrets")
        st.stop()

client = genai.Client(api_key=api_key.strip())

# --- FAST FALLBACK - FIX FOR SLOW + 503 ---
def generate_with_fallback(prompt_text):
    for model in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-lite-latest"]:
        try:
            res = client.models.generate_content(
                model=model,
                contents=prompt_text,
                config={"max_output_tokens": 900, "temperature": 0.7}
            )
            return res.text
        except:
            continue
    return "Gemini is busy, please click again after 5 seconds!"

tab1, tab2, tab3 = st.tabs(["Scenario 1: Generate Plan", "Scenario 2: Feedback Update", "Scenario 3: Nutrition Tip"])

with tab1:
    st.subheader("Generate Your Personalized Plan")
    with st.form("form1"):
        name = st.text_input("Name")
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", 10, 100, 23)
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 60.0)
        with c2:
            height = st.number_input("Height (cm)", 100.0, 250.0, 165.0)
            gender = st.selectbox("Gender", ["Female", "Male", "Other"])
        intensity = st.selectbox("Workout Intensity", ["High", "Medium", "Low"])
        activity = st.radio("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"], horizontal=True)
        goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "General Wellness"])
        diet = st.radio("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian", "Jain"], horizontal=True)
        allergies = st.text_input("Any Allergies?")
        btn1 = st.form_submit_button("Generate 7-Day Plan")

    if btn1:
        if not name.strip():
            st.error("Please enter Name")
        else:
            bmi = weight / ((height/100)**2)
            prompt = f"Give 7-day workout plan for {name}, Age {age}, {gender}, {weight}kg, {height}cm, BMI {bmi:.1f}, Goal {goal}, Intensity {intensity}, Activity {activity}, Diet {diet}, Allergies {allergies}. Include daily exercise sets reps duration, 1 nutrition tip and 1 recovery tip for {goal}. Keep structured, short bullet points."
            with st.spinner("Creating your plan... (5 sec)"):
                plan_text = generate_with_fallback(prompt)
            try:
                conn = sqlite3.connect("fitbuddy.db")
                conn.execute("INSERT INTO users (name, age, weight, height, goal, intensity, plan) VALUES (?,?,?,?,?,?,?)",
                             (name.strip(), age, weight, height, goal, intensity, plan_text))
                conn.commit()
                conn.close()
            except:
                pass
            st.session_state[f"plan_{name.lower().strip()}"] = plan_text
            st.session_state[f"goal_{name.lower().strip()}"] = goal
            st.success(f"Your Plan is Ready, {name}! 💪")
            st.markdown(plan_text)
            st.balloons()
            st.download_button("Download Plan", plan_text, file_name=f"Plan_{name}.txt")

with tab2:
    st.subheader("Update Plan with Feedback")
    fb_name = st.text_input("Enter Your Name", key="fb_name2")
    feedback = st.text_area("Your Feedback", placeholder="include more cardio, rest days")
    if st.button("Update My Plan with AI"):
        if not fb_name.strip() or not feedback.strip():
            st.error("Enter both Name and Feedback")
        else:
            key = fb_name.strip().lower()
            prev_plan = st.session_state.get(f"plan_{key}")
            prev_goal = st.session_state.get(f"goal_{key}")
            if not prev_plan:
                try:
                    conn = sqlite3.connect("fitbuddy.db")
                    cur = conn.cursor()
                    cur.execute("SELECT plan, goal FROM users WHERE LOWER(name)=LOWER(?) ORDER BY id DESC LIMIT 1", (fb_name.strip(),))
                    row = cur.fetchone()
                    conn.close()
                    if row:
                        prev_plan, prev_goal = row
                except:
                    pass
            if not prev_plan:
                st.error("No previous plan found for this name. Generate in Tab 1 first.")
            else:
                prompt2 = f"Previous plan: {prev_plan}. Goal: {prev_goal}. Feedback: {feedback}. Update 7-day plan based on feedback. Keep short."
                with st.spinner("Updating..."):
                    updated = generate_with_fallback(prompt2)
                st.success("Updated Plan Ready!")
                st.markdown(updated)

with tab3:
    st.subheader("Get Nutrition / Recovery Tip")
    tip_goal = st.selectbox("Select Goal", ["Weight Loss", "Muscle Gain", "General Wellness"], key="tg")
    if st.button("Get Tip"):
        prompt3 = f"Give 60-word nutrition or recovery tip for {tip_goal}. Practical and short."
        with st.spinner("Getting tip..."):
            tip = generate_with_fallback(prompt3)
        st.success(tip)

st.markdown("---")
st.caption("Made with love by Team N3Bee - Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A | Powered by Gemini | FastAPI + SQLite + Gemini + HTML")
