import streamlit as st
from google import genai

st.set_page_config(page_title="N3Bee - AI Diet Planner", page_icon="🥗", layout="centered")
st.markdown("<h1 style='text-align:center; color:#2D7D32;'>🥗 N3Bee - Personalized AI Diet Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Your Smart Nutrition Assistant powered by Gemini</p>", unsafe_allow_html=True)

api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except:
    pass

if not api_key:
    with st.sidebar:
        st.header("🔑 API Configuration")
        st.write("Get Free Key: aistudio.google.com/app/apikey")
        user_input = st.text_input("Enter Gemini API Key", type="password")
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
        age = st.number_input("Age", 10, 100, 23)
        weight = st.number_input("Weight (kg)", 30.0, 200.0, 60.0)
        height = st.number_input("Height (cm)", 100.0, 250.0, 165.0)
    with col2:
        gender = st.selectbox("Gender", ["Female", "Male", "Other"])
    
    activity = st.radio("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
    goal = st.radio("Goal", ["Weight Loss", "Maintain Healthy Weight", "Weight Gain / Muscle Gain"])
    diet_pref = st.radio("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian", "Jain"])
    
    allergies = st.text_input("Any Allergies / Avoid? (Optional)", placeholder="Ex: Peanuts, Milk")
    submit = st.form_submit_button("Generate My Diet Plan")

if submit:
    bmi_val = weight / ((height / 100) ** 2)
    prompt = f"You are a professional nutritionist for N3Bee. Create a detailed 7-day diet plan for Age {age}, Gender {gender}, Weight {weight}kg, Height {height}cm, BMI {bmi_val:.1f}, Activity {activity}, Goal {goal}, Diet {diet_pref}, Allergies {allergies}. Give daily breakfast, lunch, dinner, snacks with calories. Use Indian foods."

    with st.spinner("N3Bee AI is creating your plan... 🥗"):
        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-3.8-flash"]
        plan_generated = False
        
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(model=model_name, contents=prompt)
                if response.text:
                    st.success(f"Your Personalized Diet Plan is Ready! ({model_name})")
                    st.markdown(response.text)
                    st.balloons()
                    st.download_button("Download Plan", data=response.text, file_name="N3Bee_Diet_Plan.txt")
                    plan_generated = True
                    break
            except Exception as e:
                err_msg = str(e).lower()
                if "503" in err_msg or "404" in err_msg or "not found" in err_msg or "high demand" in err_msg:
                    continue
                else:
                    st.error(f"Error with {model_name}: {e}")
                    break
        
        if not plan_generated:
            st.error("All models are busy. Please wait 1 minute and try again!")

st.divider()
st.caption("Made with love by Team N3Bee - Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A | Powered by Gemini")
