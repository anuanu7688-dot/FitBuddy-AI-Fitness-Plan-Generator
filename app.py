import streamlit as st
from google import genai
from google.genai import errors
import time

# --- Page Config ---
st.set_page_config(
    page_title="N3Bee - AI Diet Planner",
    page_icon="🥗",
    layout="centered"
)

# --- CSS for Professional Look ---
st.markdown("""
<style>
    .main-title { text-align: center; color: #2E7D32; }
    .stButton>button { background-color: #2E7D32; color: white; width: 100%; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🥗 N3Bee - Personalized AI Diet Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Your Smart Nutrition Assistant powered by Gemini</p>", unsafe_allow_html=True)
st.divider()

# --- API KEY LOGIC (Standard & Secure) ---
# Priority 1: Check Streamlit Secrets (for auto-open)
# Priority 2: Check Sidebar input (for user own key)

api_key = None

# Try to get from Secrets first
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None

# If not in Secrets, ask in Sidebar
if not api_key:
    with st.sidebar:
        st.header("🔑 API Configuration")
        st.info("Enter your Gemini API Key to use the app")
        st.link_button("Get Free Gemini Key", "https://aistudio.google.com/app/apikey")
        api_key_input = st.text_input("Enter Gemini API Key", type="password", placeholder="Paste AQ... or AIza... key here")
        if api_key_input:
            api_key = api_key_input.strip()
        st.divider()
        st.caption("Your key is safe. It is not stored.")

# Stop if no key
if not api_key:
    st.warning("⚠️ Please enter your Gemini API Key in the sidebar to continue.")
    st.stop()

# --- Gemini Client Initialization (Works for both AIza and AQ keys) ---
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"❌ Invalid API Key format. Error: {e}")
    st.stop()

# --- User Input Form ---
with st.form("diet_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=10, max_value=100, value=22)
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=60.0)
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=165.0)
    with col2:
        gender = st.selectbox("Gender", ["Female", "Male", "Other"])
        activity = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
        goal = st.selectbox("Goal", ["Weight Loss", "Weight Gain", "Muscle Gain", "Maintain Healthy Weight", "General Fitness"])

    diet_pref = st.selectbox("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian", "Jain"])
    allergies = st.text_input("Any Allergies / Food to Avoid? (Optional)", placeholder="Ex: Peanuts, Mushroom, Milk")
    
    submit_button = st.form_submit_button("✨ Generate My Diet Plan")

# --- Generate Logic ---
if submit_button:
    # Calculate BMI for better prompt
    bmi = weight / ((height/100) ** 2)
    
    prompt = f"""
    You are a certified professional nutritionist and dietitian for N3Bee App.
    Create a highly personalized, practical
