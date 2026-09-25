import streamlit as st
from google import genai

st.set_page_config(page_title="N3Bee Diet Planner", page_icon="🐝")

st.title("🐝 N3Bee")
st.write("Personalized AI Diet Planner")

api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else None

if not api_key:
    api_key = st.sidebar.text_input("Enter API Key", type="password")

if not api_key:
    st.warning("Enter API key to continue")
    st.stop()

client = genai.Client(api_key=api_key)

age = st.number_input("Age", 10, 100, 23)
gender = st.selectbox("Gender", ["Female", "Male", "Other"])
weight = st.number_input("Weight kg", 30.0, 200.0, 60.0)
height = st.number_input("Height cm", 100.0, 250.0, 165.0)
activity = st.selectbox("Activity", ["Sedentary", "Lightly Active", "Very Active"])
goal = st.radio("Goal", ["Weight Loss", "Maintain", "Weight Gain"])
diet = st.radio("Diet", ["Vegetarian", "Non-Vegetarian", "Vegan", "Jain"])
avoid = st.text_input("Avoid foods")

if st.button("Generate Plan"):
    bmi = weight / ((height/100)**2)
    prompt = f"Create beautiful 7 day Indian diet plan with table and emojis for age {age} gender {gender} weight {weight} height {height} bmi {bmi:.1f} activity {activity} goal {goal} diet {diet} avoid {avoid}. Make table with Day Breakfast Lunch Dinner Snacks Calories. Give aesthetic outstanding output."
    
    with st.spinner("Generating..."):
        try:
            res = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
            st.success(f"Plan Ready! BMI {bmi:.1f}")
            st.markdown(res.text)
            st.balloons()
        except Exception as e:
            st.error(str(e))

st.markdown("---")
st.markdown("<div style='text-align:center'><b>Team N3Bee</b><br>Anushree P | Ahammed Sha | Avinth Atchai C | Afsal A</div>", unsafe_allow_html=True)
