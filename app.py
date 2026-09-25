import streamlit as st
import sqlite3
from google import genai

st.set_page_config(title="FitBuddy - AI Fitness Plan Generator", page_icon="💪", layout="centered")

st.markdown("<h2 style='text-align:center; color:#2D7D32;'>💪 FitBuddy - AI Fitness Plan Generator</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Personalized workout plans & nutrition tips using Gemini AI</p>", unsafe_allow_html=True)

# --- Database for Skill Wallet (SQLite) ---
conn_init = sqlite3.connect("fitbuddy.db")
conn_init.execute("""CREATE TABLE IF NOT EXISTS users 
(id INTEGER PRIMARY KEY, name TEXT, age INTEGER, weight REAL, height REAL, goal TEXT, intensity TEXT, plan TEXT)""")
conn_init.commit()
conn_init.close()

# --- Gemini API Key ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.sidebar.header("🔑 API Configuration")
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
    if not api_key:
        st.warning("Please enter your Gemini API Key in sidebar to continue.")
        st.stop()

client = genai.Client(api_key=api_key.strip())

# --- FIX FOR 503 ERROR - Fallback Models ---
def generate_with_fallback(prompt_text):
    models_to_try = ["gemini-2.5-flash-lite", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-lite-latest"]
    last_error = ""
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(model=model_name, contents=prompt_text)
            return response.text
        except Exception as e:
            last_error = str(e)
            if "503" in last_error or "UNAVAILABLE" in last_error or "overloaded" in last_error.lower():
                continue
            else:
                continue
    return f"Gemini is busy (503). Please click the button again after 10 seconds! Error: {last_error}"

# --- Tabs as per requirement ---
tab1, tab2, tab3 = st.tabs(["Scenario 1: Generate Plan", "Scenario 2: Feedback Update", "Scenario 3: Nutrition Tip"])

# ================= TAB 1 =================
with tab1:
    st.subheader("Generate Your Personalized Plan")
    with st.form("fitbuddy_form"):
        name = st.text_input("Name", placeholder="Your Name")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 10, 100, 23)
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 60.0)
        with col2:
            height = st.number_input("Height (cm)", 100.0, 250.0, 165.0)
            gender = st.selectbox("Gender", ["Female", "Male", "Other"])
        
        intensity = st.selectbox("Workout Intensity (High/Medium/Low)", ["High", "Medium", "Low"])
        activity = st.radio("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"], horizontal=True)
        goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "General Wellness"])
        diet = st.radio("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian", "Jain"], horizontal=True)
        allergies = st.text_input("Any Allergies / Avoid? (Optional)", placeholder="Ex: Peanuts, Milk")
        submitted = st.form_submit_button("Generate 7-Day Plan")

    if submitted:
        if not name.strip():
            st.error("Please enter Name as per Scenario 1")
        else:
            try:
                bmi_val = weight / ((height / 100) ** 2)
                prompt = f"""Create personalized 7-day workout plan for {name}, Age {age}, {gender}, {weight}kg, {height}cm, BMI {bmi_val:.1f}, Activity {activity}, Goal {goal}, Intensity {intensity}, Diet {diet}, Allergies {allergies}.
                Include: day-wise 7-day schedule: exercise name, sets, reps, duration.
                Also include exactly 1 nutrition tip and 1 recovery tip for goal {goal}.
                Keep it structured and goal-specific. Mention diet {diet} clearly."""

                with st.spinner("FitBuddy AI is creating your plan..."):
                    plan_text = generate_with_fallback(prompt)

                # Save to SQLite - Required
                conn = sqlite3.connect("fitbuddy.db")
                conn.execute("INSERT INTO users (name, age, weight, height, goal, intensity, plan) VALUES (?,?,?,?,?,?,?)",
                             (name.strip(), age, weight, height, goal, intensity, plan_text))
                conn.commit()
                conn.close()

                # Save to Session also - FIX for SQLite reset on Streamlit Cloud
                st.session_state[f"plan_{name.lower().strip()}"] = plan_text
                st.session_state[f"goal_{name.lower().strip()}"] = goal

                st.success(f"Your Plan is Ready, {name}! 💪")
                st.markdown(plan_text)
                st.balloons()
                st.download_button("Download Plan", data=plan_text, file_name=f"FitBuddy_Plan_{name}.txt")

            except Exception as e:
                st.error(f"Error: {e}. Click Generate again!")

# ================= TAB 2 =================
with tab2:
    st.subheader("Update Plan with Feedback")
    st.caption("Have a plan? Give feedback like 'more cardio' or 'include rest days'")
    fb_name = st.text_input("Enter Your Name", key="fb_name")
    feedback = st.text_area("Your Feedback", placeholder="Ex: include more cardio, less strength")
    
    if st.button("Update My Plan with AI"):
        if not fb_name.strip() or not feedback.strip():
            st.error("Please enter both Name and Feedback")
        else:
            fb_name_clean = fb_name.strip()
            # Check Session First + SQLite Second
            prev_plan = st.session_state.get(f"plan_{fb_name_clean.lower()}")
            prev_goal = st.session_state.get(f"goal_{fb_name_clean.lower()}")

            if not prev_plan:
                try:
                    conn = sqlite3.connect("fitbuddy.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT plan, goal FROM users WHERE LOWER(name)=LOWER(?) ORDER BY id DESC LIMIT 1", (fb_name_clean,))
                    row = cursor.fetchone()
                    conn.close()
                    if row:
                        prev_plan, prev_goal = row
                except Exception as e:
                    st.error(f"DB Error: {e}")

            if not prev_plan:
                st.error("No previous plan found for this name. Generate in Tab 1 first.")
            else:
                prompt2 = f"Previous plan: {prev_plan}. User feedback: {feedback}. Goal: {prev_goal}. Regenerate updated 7-day workout plan based on feedback. Keep structure same but apply feedback."
                with st.spinner("Updating plan based on feedback..."):
                    updated_plan = generate_with_fallback(prompt2)
                st.success("Updated Plan Ready!")
                st.markdown(updated_plan)
                st.download_button("Download Updated Plan", data=updated_plan, file_name=f"Updated_Plan_{fb_name_clean}.txt", key="dl2")

# ================= TAB 3 =================
with tab3:
    st.subheader("Get Nutrition / Recovery Tip")
    tip_goal = st.selectbox("Select Goal", ["Weight Loss", "Muscle Gain", "General Wellness"], key="tip_goal")
    if st.button("Get Tip"):
        prompt3 = f"Give a concise and relevant nutrition or recovery tip for fitness goal {tip_goal}. Example: include protein in post-workout meal, hydration, sleep. Make it practical and short (50-80 words)."
        with st.spinner("Getting tip..."):
            tip_text = generate_with_fallback(prompt3)
        st.success(tip_text)

# --- Footer as per requirement ---
st.markdown("---")
st.caption("Made with love by Team N3Bee - Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A | Powered by Gemini | FastAPI + SQLite + Gemini + HTML")

# Note for Skill Wallet Epic 5 - This code uses SQLite + Gemini + Session fallback to ensure Feedback Update works even after Streamlit Cloud reboot.
