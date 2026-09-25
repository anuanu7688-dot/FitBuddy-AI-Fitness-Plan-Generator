import streamlit as st
from google import genai

st.set_page_config(page_title="N3Bee - AI Diet Planner", page_icon="🐝", layout="centered")

# --- ADAPTIVE BEAUTY CSS - Works in BOTH Dark & Light ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
* { font-family: 'Poppins', sans-serif; }

/* Header - Beautiful in both modes */
.header {
    background: linear-gradient(135deg, #2E7D32 0%, #66BB6A 100%);
    padding: 28px;
    border-radius: 18px;
    text-align: center;
    color: white !important;
    box-shadow: 0 8px 20px rgba(46,125,50,0.3);
    margin-bottom: 20px;
}
.header h1, .header p { color: white !important; }

/* Form Card - Adaptive */
div[data-testid="stForm"] {
    border-radius: 18px !important;
    border: 1.5px solid rgba(46,125,50,0.2) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.07) !important;
    padding: 20px !important;
}

/* Button - Always Green Gradient */
div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #2E7D32, #43A047) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    height: 50px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    box-shadow: 0 4px 12px rgba(46,125,50,0.3) !important;
}
div[data-testid="stFormSubmitButton"] > button:hover {
    transform: scale(1.01);
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h1 style='margin:0;'>🐝 N3Bee</h1>
    <p style='margin:8px 0 0 0; font-size:17px;'>Personalized AI Diet Planner</p>
    <p style='margin:4px 0 0 0; font-size:12px; opacity:0.9;'>Healthy • Tasty • Made for India</p>
</div>
""", unsafe_allow_html=True)

# API Key
api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except:
    pass
if not api_key:
    with st.sidebar:
        st.header("🔑 API Key")
        inp = st.text_input("Enter Gemini API Key", type="password")
        if inp: api_key = inp.strip()
if not api_key:
    st.info("👋 Enter API Key in sidebar to start")
    st.stop()

client = genai.Client(api_key=api_key)

with st.form("diet_form"):
    st.markdown("#### 👤 Your Details")
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("Age", 10, 100, 23)
        weight = st.number_input("Weight (kg)", 30.0, 200.0, 60.0)
    with c2:
        gender = st.selectbox("Gender", ["Female", "Male", "Other"])
        height = st.number_input("Height (cm)", 100.0, 250.0, 165.0)
    
    st.markdown("#### 🎯 Your Goal")
    activity = st.select_slider("Activity Level", options=["Sedentary", "Lightly Active", "Moderately Active", "Very Active"], value="Lightly Active")
    g1, g2 = st.columns(2)
    with g1:
        goal = st.radio("Goal", ["Weight Loss", "Maintain Healthy Weight", "Weight Gain / Muscle Gain"])
    with g2:
        diet_pref = st.radio("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian", "Jain"])
    
    allergies = st.text_input("🚫 Allergies / Foods to Avoid?", placeholder="Ex: Peanuts, Milk, Egg")
    
    submit = st.form_submit_button("✨ Generate My Diet Plan")

if submit:
    bmi = weight / ((height/100)**2)
    prompt = f"Create beautiful 7-day Indian diet plan with emojis and markdown table. Age {age}, {gender}, {weight}kg, {height}cm, BMI {bmi:.1f}, Activity {activity}, Goal {goal}, Diet {diet_pref}, Avoid {allergies}. Give calories."
    
    with st.spinner("🐝 N3Bee is crafting your plan..."):
        try:
            response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
            st.success(f"Ready! BMI: {bmi:.1f} | ⚡ Instant")
            st.markdown(response.text)
            st.balloons()
            st.download_button("📥 Download Plan", response.text, file_name="N3Bee_Plan.txt")
        except Exception as e:
            try:
                response = client.models.generate_content(model="gemini-flash-lite-latest", contents=prompt)
                st.success(f"Ready! BMI: {bmi:.1f}")
                st.markdown(response.text)
            except Exception as e2:
                st.error(f"Try again: {e2}")

st.caption("Made with 💚 by Team N3Bee | Works beautifully in Dark & Light mode")
