import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="FitBuddy AI", page_icon="💪")
st.title("💪 FitBuddy - AI Fitness Plan Generator")
st.write("Get personalized Diet & Workout plan using Gemini AI")

# API Key in sidebar
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Gemini API Key in sidebar")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age", 10, 80, 21)
    height = st.number_input("Height (cm)", 100, 220, 170)
    weight = st.number_input("Weight (kg)", 30, 150, 65)
with col2:
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Maintain Fitness"])
    level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])

diet = st.selectbox("Diet", ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"])
days = st.slider("Days plan", 1, 7, 3)

if st.button("Generate My Plan 🔥"):
    with st.spinner("Creating your plan..."):
        prompt = f"""Act as fitness trainer. Create {days}-day plan for:
        Age {age}, Gender {gender}, Height {height}cm, Weight {weight}kg
        Goal {goal}, Level {level}, Diet {diet}
        Give Workout (Sets/Reps) and Diet (Breakfast/Lunch/Dinner with calories) and Tips. Indian food style."""
        response = model.generate_content(prompt)
        st.success("Plan Ready!")
        st.markdown(response.text)

st.caption("Built by Team FitBuddy | Powered by Gemini AI")