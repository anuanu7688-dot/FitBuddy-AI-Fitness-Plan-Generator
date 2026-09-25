import streamlit as st
from google import genai

# --- PREMIUM PAGE CONFIG ---
st.set_page_config(page_title="N3Bee - AI Diet Planner", page_icon="🐝", layout="centered")

# --- CLASSY CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.main { background: #f8fdf8; }
.stForm {
    background: white;
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(45,125,50,0.1);
    border: 1px solid #e8f5e9;
}
div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #2D7D32, #66BB6A);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 30px;
    font-weight: 600;
    font-size: 16px;
    width: 100%;
    box-shadow: 0 4px 15px rgba(45,125,50,0.3);
}
div[data-testid="stFormSubmitButton"] > button:hover {
    transform: scale(1.02);
}
.header-box {
    background: linear-gradient(135deg, #1B5E20 0%, #43A047 50%, #A5D6A7 100%);
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 10px 25px rgba(27,94,32,0.3);
}
.result-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    border-left: 5px solid #2D7D32;
}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="header-box">
    <h1 style='margin:0; font-size: 36px;'>🐝 N3Bee</h1>
    <p style='margin:5px 0 0 0; font-size:18px; opacity:0.9;'>Personalized AI Diet Planner</p>
    <p style='margin:5px 0 0 0; font-size:13px; opacity:0.8;'>Crafted with love for healthier India</p>
</div>
""", unsafe_allow_html=True)

# --- API KEY ---
api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except: pass

if not api_key:
    with st.sidebar:
        st.markdown("### 🔑 API Configuration")
        user_input = st.text_input("Enter Gemini API Key", type="password")
        if user_input: api_key = user_input.strip()

if not api_key:
    st.info("✨ Enter your Gemini API Key in sidebar to unlock your personalized plan")
    st.stop()

client = genai.Client(api_key=api_key)

# --- FORM ---
with st.form("diet_form"):
    st.markdown("#### 👤 Your Profile")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 10, 100, 23)
        weight = st.number_input("Weight (kg)", 30.0, 200.0, 60.0)
        height = st.number_input("Height (cm)", 100.0, 250.0, 165.0)
    with col2:
        gender = st.selectbox("Gender", ["Female", "Male", "Other"])
        st.write("")
        st.write("")
        bmi_placeholder = st.empty()
    
    st.markdown("---")
    st.markdown("#### 🎯 Your Goal")
    col_a, col_b = st.columns(2)
    with col_a:
        activity = st.select_slider("Activity Level", options=["Sedentary", "Lightly Active", "Moderately Active", "Very Active"], value="Lightly Active")
        goal = st.radio("Goal", ["Weight Loss", "Maintain Healthy Weight", "Weight Gain / Muscle Gain"])
    with col_b:
        diet_pref = st.radio("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian", "Jain"])
        allergies = st.text_input("Allergies / Avoid?", placeholder="Ex: Peanuts, Milk")

    submit = st.form_submit_button("✨ Generate My Premium Diet Plan")

if submit:
    bmi_val = weight / ((height / 100) ** 2)
    if bmi_val < 18.5: bmi_status = "Underweight"
    elif bmi_val < 25: bmi_status = "Healthy"
    elif bmi_val < 30: bmi_status = "Overweight"
    else: bmi_status = "Obese"
    
    st.markdown(f"""
    <div style="background:white; padding:15px; border-radius:12px; text-align:center; margin-bottom:15px; border:1px solid #e8f5e9;">
        <b>BMI: {bmi_val:.1f}</b> - {bmi_status} | <b>Maintenance:</b> {int(weight*28)}-{int(weight*32)} kcal/day
    </div>
    """, unsafe_allow_html=True)

    prompt = f"Act as a premium Indian nutritionist for N3Bee. Create a beautiful 7-day diet plan using markdown tables and emojis. User: Age {age}, Gender {gender}, Weight {weight}kg, Height {height}cm, BMI {bmi_val:.1f}, Activity {activity}, Goal {goal}, Diet {diet_pref}, Avoid {allergies}. Use Indian foods, give calories per meal, include tips. Make it aesthetic."

    with st.spinner("🐝 N3Bee AI is crafting your aesthetic plan..."):
        try:
            response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
            st.markdown(f"""
            <div class="result-card">
                <h3 style="color:#2D7D32; margin-top:0;">🌿 Your Plan is Ready! ⚡</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(response.text)
            st.balloons()
            st.download_button("📥 Download Premium Plan", data=response.text, file_name="N3Bee_Premium_Diet_Plan.txt")
        except Exception as e:
            try:
                response = client.models.generate_content(model="gemini-flash-lite-latest", contents=prompt)
                st.success("Your Premium Plan is Ready! ⚡")
                st.markdown(response.text)
            except Exception as e2:
                st.error(f"Please try again: {e2}")

st.divider()
st.markdown("<p style='text-align:center; color:#888; font-size:12px;'>Made with 💚 by Team N3Bee - Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A | Powered by Gemini 2.5 Flash Lite</p>", unsafe_allow_html=True)
