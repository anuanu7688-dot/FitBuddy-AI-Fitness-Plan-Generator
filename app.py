import streamlit as st
import sqlite3
import time
from google import genai

st.set_page_config(page_title="FitBuddy - AI Fitness Coach", page_icon="💪", layout="wide")

# --- Sidebar for API Key - User's Own Key ---
st.sidebar.title("🔑 Setup")
st.sidebar.markdown("To use FitBuddy, you need a free Gemini API Key")
st.sidebar.link_button("Get Free API Key", "https://aistudio.google.com/app/apikey")

api_key_input = st.sidebar.text_input("Enter Your Gemini API Key *", type="password", placeholder="AIzaSy...")

if not api_key_input:
    st.title("💪 FitBuddy - AI Fitness Plan Generator")
    st.warning("👈 Please enter your Gemini API Key in the left sidebar to start.")
    st.info("Your key is safe - it stays only in your browser session and is never saved or shared.")
    st.stop()

# --- DB Setup ---
DB_NAME = "fitbuddy.db"
def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY, plan TEXT, goal TEXT)")
    conn.commit()
    conn.close()
init_db()

# --- Fast Generation Function ---
def generate_with_user_key(user_key, prompt_text):
    try:
        client = genai.Client(api_key=user_key.strip())
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt_text
        )
        if response and hasattr(response, 'text') and response.text:
            return response.text.strip()
    except Exception as e:
        err = str(e).lower()
        if "api key" in err or "invalid" in err:
            st.sidebar.error("❌ Invalid API Key. Check your key.")
            return None
        if "429" in err or "quota" in err:
            st.error("Your API Key quota is over. Create new key from Google AI Studio.")
            return None
        # Small retry for 503
        time.sleep(1.5)
        try:
            client = genai.Client(api_key=user_key.strip())
            response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt_text)
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
        except Exception as e2:
            st.error(f"AI is busy. Please try again after 10 seconds. Details: {str(e2)[:100]}")
            return None
    return None

st.markdown("<h2 style='text-align:center'>💪 FitBuddy - AI Fitness Plan Generator</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Your Personalized 7-Day AI Coach</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📋 Scenario 1: Generate Plan", "🔄 Scenario 2: Update with Feedback", "💡 Scenario 3: Nutrition / Recovery Tip"])

with tab1:
    st.subheader("Scenario 1: Generate Personalized Plan")
    with st.form("gen_form"):
        name = st.text_input("Name *", placeholder="e.g. Your name")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 10, 100, 23)
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 60.0)
            intensity = st.selectbox("Preferred Workout Intensity *", ["Low", "Medium", "High"])
        with col2:
            height = st.number_input("Height (cm)", 100.0, 250.0, 165.0)
            gender = st.selectbox("Gender", ["Female", "Male", "Other"])
            activity = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
        goal = st.selectbox("Fitness Goal *", ["Weight Loss", "Muscle Gain", "General Fitness"])
        diet = st.radio("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan"], horizontal=True)
        allergies = st.text_input("Allergies / Foods to Avoid (Optional)")
        submitted = st.form_submit_button("🚀 Generate My 7-Day Plan", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Please enter Name - Required as per Scenario 1")
        else:
            bmi = weight / ((height/100)**2)
            prompt = f"""
            You are FitBuddy AI fitness coach. Create personalized 7-day workout plan.
            User: Name={name}, Age={age}, Weight={weight}kg, Height={height}cm, BMI={bmi:.1f}, Gender={gender}, Goal={goal}, Intensity={intensity}, Activity={activity}, Diet={diet}, Avoid={allergies}.
            Requirements:
            - Day-wise schedule Day 1 to Day 7
            - For each day give exercise name, sets x reps, rest time
            - Add 1 Nutrition Tip and 1 Recovery Tip at end
            - Keep it structured, short, and goal-specific
            - Use emojis and bullet points
            """
            with st.spinner("FitBuddy AI is creating your plan..."):
                plan = generate_with_user_key(api_key_input, prompt)
            
            if plan:
                st.session_state[f"plan_{name.lower().strip()}"] = plan
                st.session_state[f"goal_{name.lower().strip()}"] = goal
                conn = sqlite3.connect(DB_NAME)
                conn.execute("INSERT OR REPLACE INTO users VALUES (?,?,?)", (name.lower().strip(), plan, goal))
                conn.commit()
                conn.close()
                st.success(f"✅ Plan Generated for {name}!")
                st.markdown(plan)
                st.download_button("📥 Download Plan as TXT", data=plan, file_name=f"{name}_FitBuddy_Plan.txt")

with tab2:
    st.subheader("Scenario 2: Update Plan with Feedback")
    st.markdown("If you want to change your plan, enter feedback and AI will regenerate.")
    fb_name = st.text_input("Enter Your Name *", key="fb_name", placeholder="Same name you used in Scenario 1")
    feedback = st.text_area("Your Feedback *", placeholder="e.g. Add more cardio, reduce weights, I have knee pain")
    if st.button("🔄 Update My Plan", use_container_width=True):
        if not fb_name.strip() or not feedback.strip():
            st.error("Please enter Name and Feedback")
        else:
            clean = fb_name.lower().strip()
            prev_plan = st.session_state.get(f"plan_{clean}")
            prev_goal = st.session_state.get(f"goal_{clean}", "General Fitness")
            
            if not prev_plan:
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute("SELECT plan, goal FROM users WHERE name=?", (clean,))
                row = cur.fetchone()
                conn.close()
                if row:
                    prev_plan, prev_goal = row
            
            if not prev_plan:
                st.warning("No previous plan found. Please generate plan in Scenario 1 first.")
            else:
                prompt2 = f"""
                Previous fitness plan: {prev_plan}
                User Goal: {prev_goal}
                User Feedback: {feedback}
                Task: Regenerate updated 7-day plan based on feedback. Keep same format with sets/reps/rest + nutrition and recovery tip.
                """
                with st.spinner("Updating your plan based on feedback..."):
                    updated = generate_with_user_key(api_key_input, prompt2)
                if updated:
                    st.success("✅ Updated Plan Ready!")
                    st.markdown(updated)
                    st.download_button("📥 Download Updated Plan", data=updated, file_name=f"{fb_name}_Updated_Plan.txt", key="dl2")

with tab3:
    st.subheader("Scenario 3: Get Nutrition / Recovery Tip")
    tip_goal = st.selectbox("Select Your Fitness Goal", ["Weight Loss", "Muscle Gain", "General Fitness"], key="tip_g")
    tip_type = st.radio("Tip Type", ["Nutrition Tip", "Recovery Tip"], horizontal=True)
    if st.button("💡 Get My Tip", use_container_width=True):
        prompt3 = f"Give a 2-3 line expert {tip_type} for someone whose goal is {tip_goal}. Keep it practical and Indian diet friendly."
        with st.spinner("Getting tip..."):
            tip = generate_with_user_key(api_key_input, prompt3)
        if tip:
            st.info(tip)

st.markdown("---")
st.caption("Made with ❤️ by Team N3Bee - Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A | FastAPI + Gemini + Streamlit")
