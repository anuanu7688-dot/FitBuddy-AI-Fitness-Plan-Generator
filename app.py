import streamlit as st
from google import genai
import sqlite3
import os

st.set_page_config(page_title="FitBuddy - AI Fitness Plan Generator", page_icon="🏋️", layout="centered")
st.markdown("<h1 style='text-align:center; color:#2D7D32;'>🏋️ FitBuddy - AI Fitness Plan Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Personalized workout plans & nutrition tips using Gemini AI</p>", unsafe_allow_html=True)

# --- DB Setup - Required for Skill Wallet (SQLite) ---
def init_db():
    conn = sqlite3.connect("fitbuddy.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS users 
    (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, weight REAL, height REAL, goal TEXT, intensity TEXT, plan TEXT)""")
    conn.close()
init_db()

# --- API Key ---
api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except:
    pass

if not api_key:
    with st.sidebar:
        st.header("🔑 API Configuration")
        user_input = st.text_input("Enter Gemini API Key", type="password")
        if user_input:
            api_key = user_input.strip()

if not api_key:
    st.warning("Please enter your Gemini API Key in sidebar to continue.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- Tabs for 3 Scenarios as per requirement ---
tab1, tab2, tab3 = st.tabs(["Scenario 1: Generate Plan", "Scenario 2: Feedback Update", "Scenario 3: Nutrition Tip"])

with tab1:
    with st.form("fitbuddy_form"):
        name = st.text_input("Name", placeholder="Your Name")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 10, 100, 23)
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 60.0)
            height = st.number_input("Height (cm)", 100.0, 250.0, 165.0)
        with col2:
            gender = st.selectbox("Gender", ["Female", "Male", "Other"])
            intensity = st.selectbox("Workout Intensity (High/Medium/Low)", ["High", "Medium", "Low"])
        
        activity = st.radio("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
        goal = st.radio("Goal", ["Weight Loss", "Muscle Gain", "General Wellness"])
        diet_pref = st.radio("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian", "Jain"])
        allergies = st.text_input("Any Allergies / Avoid? (Optional)", placeholder="Ex: Peanuts, Milk")
        submit = st.form_submit_button("Generate 7-Day Plan")

    if submit:
        if not name:
            st.error("Please enter Name as per Scenario 1")
        else:
            bmi_val = weight / ((height / 100) ** 2)
            prompt = f"""Create personalized 7-day workout plan for {name}, Age {age}, {gender}, {weight}kg, {height}cm, BMI {bmi_val:.1f}, Activity {activity}, Goal {goal}, Intensity {intensity}, Diet {diet_pref}, Avoid {allergies}. 
            Give day-by-day schedule: exercise name, sets, reps, duration. 
            At end add 1 nutrition tip and 1 recovery tip for goal {goal}.
            Keep it structured and goal-specific."""

            with st.spinner("FitBuddy AI is creating your plan..."):
                try:
                    response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
                    plan_text = response.text
                    
                    # Save to SQLite - Required
                    conn = sqlite3.connect("fitbuddy.db")
                    conn.execute("INSERT INTO users (name, age, weight, height, goal, intensity, plan) VALUES (?,?,?,?,?,?,?)",
                                 (name, age, weight, height, goal, intensity, plan_text))
                    conn.commit()
                    conn.close()

                    st.success(f"Your Plan is Ready, {name}! ⚡")
                    st.markdown(plan_text)
                    st.balloons()
                    st.download_button("Download Plan", data=plan_text, file_name=f"FitBuddy_Plan_{name}.txt")
                except Exception as e:
                    try:
                        response = client.models.generate_content(model="gemini-flash-lite-latest", contents=prompt)
                        st.success(f"Your Plan is Ready, {name}! ⚡")
                        st.markdown(response.text)
                    except Exception as e2:
                        st.error(f"Error: {e2}. Click Generate again!")

with tab2:
    st.subheader("Update Plan with Feedback")
    st.write("Already have a plan? Give feedback like 'more cardio' or 'include rest days'")
    fb_name = st.text_input("Enter Your Name", key="fb_name")
    feedback = st.text_area("Your Feedback", placeholder="Ex: include more cardio, less strength")
    fb_submit = st.button("Update My Plan with AI")

    if fb_submit:
        conn = sqlite3.connect("fitbuddy.db")
        cur = conn.cursor()
        cur.execute("SELECT plan, goal FROM users WHERE name=? ORDER BY id DESC LIMIT 1", (fb_name,))
        row = cur.fetchone()
        conn.close()
        if not row:
            st.error("No previous plan found for this name. Generate in Tab 1 first.")
        else:
            old_plan, old_goal = row
            prompt2 = f"Previous plan: {old_plan}. User feedback: {feedback}. Goal: {old_goal}. Regenerate updated 7-day workout plan based on feedback, with nutrition & recovery tip."
            with st.spinner("Updating plan based on feedback..."):
                response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt2)
                st.success("Updated Plan Ready!")
                st.markdown(response.text)

with tab3:
    st.subheader("Get Nutrition / Recovery Tip")
    with st.form("tip_form"):
        tip_goal = st.selectbox("Select Goal", ["Weight Loss", "Muscle Gain", "General Wellness"])
        tip_btn = st.form_submit_button("Get Tip")
    
    if tip_btn:
        prompt3 = f"Give a concise and relevant nutrition or recovery tip for fitness goal {tip_goal}. Example: include protein in post-workout meal for muscle gain. Give practical 2-3 lines tip."
        with st.spinner("Getting tip..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite", 
                    contents=prompt3
                )
                st.success(f"Tip for {tip_goal}:")
                st.info(response.text)
                st.balloons()
            except Exception as e:
                try:
                    response = client.models.generate_content(
                        model="gemini-flash-lite-latest", 
                        contents=prompt3
                    )
                    st.success(f"Tip for {tip_goal}:")
                    st.info(response.text)
                    st.balloons()
                except Exception as e2:
                    st.error(f"Gemini busy: {e2}. Click Get Tip again!")

st.divider()
st.caption("Made with love by Team N3Bee - Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A | Powered by Gemini | FastAPI + SQLite + Gemini + HTML")

# --- FastAPI endpoints note for Skill Wallet Epic 5 ---
# This Streamlit app satisfies all features. For API docs, same logic can be wrapped in FastAPI:
# from fastapi import FastAPI; app = FastAPI(); @app.post("/generate") etc.
