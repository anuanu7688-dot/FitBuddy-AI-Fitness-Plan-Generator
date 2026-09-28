import streamlit as st
import sqlite3
import random
import concurrent.futures
from datetime import datetime
from google import genai

st.set_page_config(page_title="FitBuddy - AI Fitness Coach", page_icon="💪", layout="wide")

# Sidebar - ONE KEY
st.sidebar.title("🔑 Setup")
st.sidebar.link_button("Get Free Gemini Key", "https://aistudio.google.com/app/apikey")
api_key = st.sidebar.text_input("Enter Your Gemini API Key *", type="password", placeholder="AIzaSy...")

if not api_key:
    st.title("💪 FitBuddy - AI Fitness Plan Generator")
    st.warning("👈 Enter your API Key in the left sidebar to start")
    st.stop()

# DB init
conn = sqlite3.connect("fitbuddy.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY, plan TEXT, goal TEXT)")
conn.commit()
conn.close()

def get_db():
    c = sqlite3.connect("fitbuddy.db", check_same_thread=False)
    return c

def get_dynamic_plan(name, goal, intensity, diet, bmi, age, weight, allergies):
    """Instant Personalized Plan - Different every time"""
    random.seed(f"{name}{goal}{intensity}{datetime.now().microsecond}")
    r = random.randint

    if goal == "Weight Loss":
        ex1 = f"Squats {r(12,15)}x{r(3,4)}, Burpees {r(8,12)}x3, Jumping Jacks {r(30,45)}s x3"
        ex2 = f"Mountain Climbers {r(20,30)}s x3, Brisk Walk {r(30,40)}min"
    elif goal == "Muscle Gain":
        ex1 = f"Bench Press {r(6,10)}x4, Deadlift {r(6,8)}x3, Pull-ups {r(6,10)}x3"
        ex2 = f"DB Shoulder Press {r(8,10)}x3, Barbell Rows {r(8,12)}x4"
    else:
        ex1 = f"Pushups {r(10,18)}x3, Squats {r(10,15)}x3, Plank {random.choice(['40s','50s','60s'])} x3"
        ex2 = f"Lunges {r(10,12)}x3 each, Yoga Flow {r(15,25)}min"

    prot = "Paneer, Soya, Dal, Curd, Sprouts" if diet!= "Non-Vegetarian" else "Eggs, Chicken 100g, Fish, Dal"
    avoid = f"\n> ⚠️ Avoid: {allergies}" if allergies else ""
    cal = int(weight*33) if goal=="Muscle Gain" else int(weight*26)

    return f"""
### 💪 FitBuddy Plan for {name} | {goal} | BMI {bmi:.1f} | {intensity}
**Profile:** {age}y, {weight}kg, {diet} | **Target:** ~{cal} kcal/day{avoid}

**Day 1 - Full Power:** {ex1} | Rest 60s
**Day 2 - Cardio Core:** {ex2}, Crunches 3x{ r(15,25) }, Leg Raise 3x15
**Day 3 - Upper Body:** {ex2} + Pushups 3x12 + Plank 45s x2
**Day 4 - Recovery:** Stretch 15min + Yoga 20min + 10k Steps
**Day 5 - Lower Body:** {ex1}, Calf Raise 3x20, Glute Bridge 3x15
**Day 6 - HIIT Burn:** Burpees 3x10, High Knees 30s x3, Jump Squats 3x12
**Day 7 - Rest:** Full Rest, 3L Water, 8hr Sleep

**🥗 Nutrition:** {prot} every meal + Fruit + 3L water
**😴 Recovery:** 7-8hr sleep, Post-workout stretch 10min, Protein {int(weight*1.8)}g/day

*ID: {name[:2].upper()}{r(100,999)} | {datetime.now().strftime('%H:%M:%S')} | Local Fast Mode - Click again for AI version*
"""

def call_model(model_name, prompt, key):
    try:
        client = genai.Client(api_key=key.strip())
        response = client.models.generate_content(model=model_name, contents=prompt)
        if response.text and len(response.text) > 40:
            return response.text.strip()
    except:
        return None
    return None

def generate_fast(prompt, key, name, goal, intensity, diet, bmi, age, weight, allergies):
    # Make prompt unique every time - no cache
    unique_prompt = f"{prompt}\nMake it unique, different structure. RandomID:{random.randint(10000,999999)} Time:{datetime.now().second}"

    # FASTEST MODELS ONLY - Lite = Fastest
    fastest_models = [
        "gemini-2.0-flash-lite",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-1.5-flash-8b"
    ]

    # Parallel check - who returns first wins = NO WAITING
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_model = {executor.submit(call_model, m, unique_prompt, key): m for m in fastest_models}
        for future in concurrent.futures.as_completed(future_to_model, timeout=7):
            result = future.result()
            if result:
                # Cancel others if we got result
                for f in future_to_model:
                    f.cancel()
                return result

    # If all busy -> instant dynamic plan (different every time)
    return get_dynamic_plan(name, goal, intensity, diet, bmi, age, weight, allergies)

st.markdown("<h2 style='text-align:center'>💪 FitBuddy - AI Fitness Plan Generator</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Fastest Gemini Model - Auto Switches if Busy - 1 Key Only</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Scenario 1: Generate Plan", "Scenario 2: Update Feedback", "Scenario 3: Tip"])

with tab1:
    with st.form("form1"):
        name = st.text_input("Name *", placeholder="Your Name")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 10, 100, 21)
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 60.0)
            intensity = st.selectbox("Intensity *", ["Low", "Medium", "High"])
        with col2:
            height = st.number_input("Height (cm)", 100.0, 250.0, 164.97)
            gender = st.selectbox("Gender", ["Female", "Male", "Other"])
            activity = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
        goal = st.selectbox("Fitness Goal *", ["Weight Loss", "Muscle Gain", "General Fitness"])
        diet = st.radio("Diet", ["Vegetarian", "Non-Vegetarian", "Vegan"], horizontal=True)
        allergies = st.text_input("Allergies / Foods to Avoid")
        submit = st.form_submit_button("🚀 Generate My 7-Day Plan", use_container_width=True)

    if submit:
        if not name.strip():
            st.error("Please enter Name")
        else:
            bmi = weight / ((height/100)**2)
            prompt = f"Create 7-day {goal} workout plan for {name}, age {age}, {weight}kg, {height}cm, BMI {bmi:.1f}, {gender}, intensity {intensity}, activity {activity}, diet {diet}, avoid {allergies}. Include day-wise exercise with sets reps rest + 1 nutrition tip + 1 recovery tip. Short structured, Indian context."
            with st.spinner("Generating... checking 4 fastest models in parallel..."):
                plan = generate_fast(prompt, api_key, name, goal, intensity, diet, bmi, age, weight, allergies)
            st.session_state[f"plan_{name.lower().strip()}"] = plan
            try:
                c = get_db()
                c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?)", (name.lower().strip(), plan, goal))
                c.commit()
                c.close()
            except: pass
            st.success("✅ Plan Ready!")
            st.markdown(plan)
            st.download_button("📥 Download Plan", plan, file_name=f"{name}_plan.txt")

with tab2:
    fb_name = st.text_input("Your Name *", key="fb2")
    feedback = st.text_area("Feedback *", placeholder="e.g. add more cardio, less weights")
    if st.button("🔄 Update My Plan", use_container_width=True):
        prev = st.session_state.get(f"plan_{fb_name.lower().strip()}")
        if not prev:
            try:
                c = get_db()
                cur = c.cursor()
                cur.execute("SELECT plan FROM users WHERE name=?", (fb_name.lower().strip(),))
                row = cur.fetchone()
                c.close()
                if row: prev = row[0]
            except: pass
        if not prev:
            st.warning("No previous plan found. Generate in Tab 1 first.")
        else:
            with st.spinner("Updating..."):
                updated = generate_fast(f"Update this plan based on feedback '{feedback}': {prev}", api_key, fb_name, "General Fitness", "Medium", "Vegetarian", 22.0, 21, 60, "")
            st.success("Updated!")
            st.markdown(updated)

with tab3:
    g = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "General Fitness"], key="tipg")
    tip_type = st.radio("Tip Type", ["Nutrition Tip", "Recovery Tip"], horizontal=True)
    if st.button("💡 Get My Tip", use_container_width=True):
        with st.spinner(f"Getting {tip_type}..."):
            tip = generate_fast(f"Give 2-3 line {tip_type} for goal {g}, Indian diet friendly, practical.", api_key, "User", g, "Medium", "Vegetarian", 22.0, 21, 60, "")
        st.info(tip)

st.markdown("---")
st.caption("Made with ❤️ by Team N3Bee - Anushree P, Ahammed Sha, Avinth Atchai C, Afsal A | 4 Fastest Models Parallel + No Error")
