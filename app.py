import streamlit as st
from google import genai

st.set_page_config(page_title="N3Bee - AI Diet Planner", page_icon="🥗", layout="centered")
st.markdown("<h1 style='text-align:center; color:#2E7D32;'>🥗 N3Bee - Personalized AI Diet Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Your Smart Nutrition Assistant powered by Gemini</p>", unsafe_allow_html=True)
st.divider()

api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = None

if not api_key:
    with st.sidebar:
        st.header("🔑 API Configuration")
        st.link_button("Get Free Gemini Key", "https://aistudio.google.com/app/apikey")
        user_input = st.text_input("Enter Gemini API Key", type="password", placeholder="Paste AQ... or AIza... key")
        if user_input:
            api_key = user_input.strip()

if not api_key:
    st.warning("Please enter your Gemini API Key in sidebar to continue.")
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Invalid API Key: {e}")
    st.stop()

with st.form("diet_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 10, 100, 22)
        weight = st.number_input("Weight (kg)", 30.0, 200.0, 60.0)
        height = st.number_input("Height (cm)", 100.0, 250.0, 165.0)
    with col2:
        gender = st.selectbox("Gender", ["Female", "Male", "Other"])
        activity = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
        goal = st.selectbox("Goal", ["Weight Loss", "Weight Gain", "Muscle Gain", "Maintain Healthy Weight"])
    diet_pref = st.selectbox("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian", "Jain"])
    allergies = st.text_input("Any Allergies / Avoid? (Optional)", placeholder="Ex: Peanuts, Milk")
    submit = st.form_submit_button("Generate My Diet Plan")

if submit:
    bmi = weight / ((height/100) ** 2)
    prompt_text = f"You are a nutritionist for N3Bee. Create 7-day diet for Age {age}, Gender {gender}, Weight {weight}kg, Height {height}cm, BMI {bmi:.1f}, Activity {activity}, Goal {goal}, Diet {diet_pref}, Allergies {allergies}. Give calorie target, daily Breakfast, Snack, Lunch, Snack, Dinner with Indian foods for {diet_pref} with portions and calories, plus tips for {goal}, water, exercise. Use tables and emojis. Add disclaimer: AI advice only."

    with st.spinner("N3Bee AI is creating your plan..."):
        try:
            response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt_text)
            if response.text:
                st.success("Your Personalized Diet Plan is Ready!")
                st.markdown(response.text)
                st.balloons()
                st.download_button("Download Plan", data=response.text, file_name="N3Bee_Diet_Plan.txt")
            else:
                st.error("No response. Try again.")
        except Exception as e:
            msg = str(e).lower()
            if "api_key" in msg or "invalid" in msg:
                st.error("Invalid API Key. Create new from aistudio.google.com/app/apikey")
            elif "quota" in msg or "429" in msg:
                st.error("API Limit Reached. Wait 1 min or use another Gmail key.")
            else:
                st.error(f"Error: {e}")

st.divider()
st.caption("Made with love by Team N3Bee - Anushree P , Ahammed Sha , Avinth Atchai C , Afsal A | Powered by Gemini 1.5 Flash")
