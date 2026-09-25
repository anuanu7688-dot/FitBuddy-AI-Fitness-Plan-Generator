import streamlit as st
from google import genai

st.set_page_config(page_title="N3Bee - AI Diet Planner", page_icon="🥗", layout="centered")
st.markdown("<h1 style='text-align:center; color:#2D7D32;'>🥗 N3Bee - Personalized AI Diet Planner</h1>", unsafe_allow_html=True)

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

with st.form("diet_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 10, 100, 23)
        weight = st.number_input("Weight (kg)", 30.0, 200.0, 60.0)
        height = st.number_input("Height (cm)", 100.0, 250.0, 165.0)
    with col2:
        gender = st.selectbox("Gender", ["Female", "Male", "Other"])
    
    activity = st.radio("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
    goal = st.radio("Goal", ["Weight Loss", "Maintain Healthy Weight", "Weight Gain","Muscle Gain"])
    diet_pref = st.radio("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian", "Jain"])
    allergies = st.text_input("Any Allergies / Avoid? (Optional)", placeholder="Ex: Peanuts, Milk")
    submit = st.form_submit_button("Generate My Diet Plan")

if submit:
    bmi_val = weight / ((height / 100) ** 2)
    prompt = f"Create 7-day Indian diet plan. Age {age}, {gender}, {weight}kg, {height}cm, BMI {bmi_val:.1f}, {activity}, Goal {goal}, Diet {diet_pref}, Avoid {allergies}. Give breakfast lunch dinner snacks with calories."

    with st.spinner("N3Bee AI is creating your plan... 2 sec..."):
        try:
            # LITE model = INSTANT & never busy
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )
            st.success(f"Your Plan is Ready! ⚡")
            st.markdown(response.text)
            st.balloons()
            st.download_button("Download Plan", data=response.text, file_name="N3Bee_Diet_Plan.txt")
        except Exception as e:
            # If lite busy, try 3.5-flash-lite
            try:
                response = client.models.generate_content(model="gemini-flash-lite-latest", contents=prompt)
                st.success("Your Plan is Ready! ⚡")
                st.markdown(response.text)
                st.balloons()
            except Exception as e2:
                st.error(f"Error: {e2}. Click Generate again!")

st.divider()
st.caption("Made with love by Team N3Bee - Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A | Powered by Gemini")
