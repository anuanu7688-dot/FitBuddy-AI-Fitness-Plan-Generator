import streamlit as st
import sqlite3
import random
import concurrent.futures
from datetime import datetime
from google import genai

st.set_page_config(page_title="FitBuddy - AI Fitness Plan Generator", page_icon="💪", layout="wide")

st.sidebar.title("🔑 Setup")
st.sidebar.link_button("Get Free Gemini Key", "https://aistudio.google.com/app/apikey")
api_key = st.sidebar.text_input("Enter Your Gemini API Key *", type="password", placeholder="AIzaSy...")

if not api_key:
    st.title("💪 FitBuddy - AI Fitness Plan Generator")
    st.warning("👈 Enter your API Key in left sidebar to start")
    st.stop()

try:
    conn = sqlite3.connect("fitbuddy.db", check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY, plan TEXT, goal TEXT, bmi REAL, weight REAL, height REAL)")
    conn.commit()
    conn.close()
except:
    pass

def get_db():
    return sqlite3.connect("fitbuddy.db", check_same_thread=False)

def get_dynamic_plan(name, goal, intensity, diet, bmi, age, weight, height, gender, allergies):
    random.seed(f"{name}{weight}{height}{datetime.now().microsecond}")
    r = random.randint
    if goal == "Weight Loss":
        d1 = f"Brisk Walk {r(30,45)}min + Jumping Jacks {r(30,45)}s x3"
        d2 = f"Squats {r(12,20)}x{r(3,4)}, Burpees {r(8,12)}x3, Plank {r(30,60)}s"
        d3 = f"HIIT: Mountain Climbers {r(20,30)}s x4, High Knees 30s x3"
        cal = int(weight * 24)
        focus = "Calorie Deficit + Cardio Burn"
    elif goal == "Muscle Gain":
        d1 = f"Bench Press {r(6,10)}x4 ({r(20,40)}kg), Deadlift {r(6,8)}x3"
        d2 = f"Pull-ups {r(5,10)}x3, Barbell Rows {r(8,12)}x4"
        d3 = f"Leg Day: Squats {r(8,12)}x4, Lunges {r(10,12)}x3"
        cal = int(weight * 35)
        focus = "Progressive Overload + Protein Surplus"
    else:
        d1 = f"Pushups {r(10,20)}x3, Squats {r(12,15)}x3"
        d2 = f"Yoga Flow {r(15,25)}min + Lunges {r(10,12)}x3"
        d3 = f"Full Body: {d1} + Walk {r(20,30)}min"
        cal = int(weight * 30)
        focus = "Balanced Fitness + Mobility"
    prot = int(weight * 2.0) if goal=="Muscle Gain" else int(weight * 1.6)
    prot_src = "Paneer 100g, Soya 50g, Dal, Curd" if diet!="Non-Vegetarian" else "Eggs 3, Chicken 150g, Fish, Dal"
    avoid = f" | Avoid: {allergies}" if allergies else ""
    return f"""
### 💪 FitBuddy Plan for {name} | {goal}
**Profile:** {age}Y, {gender}, {weight}kg, {height}cm, BMI {bmi:.1f}, Intensity {intensity}{avoid}
**Focus:** {focus} | **Target:** {cal} kcal/day | **Protein:** {prot}g/day
**Day 1 - Push:** {d1} | Rest 60s
**Day 2 - Cardio Core:** {d2} + Crunches 3x{r(15,25)}
**Day 3 - Pull/Legs:** {d3}
**Day 4 - Recovery:** Stretch 15min + Yoga 20min + {r(8,12)}k Steps
**Day 5 - Strength:** {d1} + Plank {r(40,60)}s x2
**Day 6 - HIIT:** Burpees 3x{r(8,12)}, Jump Squats 3x{r(10,15)}
**Day 7 - Rest:** Full Rest, 3L Water, 8hr Sleep
**🥗 Nutrition ({diet}):** {prot_src} + fruit + 3L water
**😴 Recovery:** Sleep 7.5-8hr, 10min stretch
"""

def call_model(model_name, prompt, key):
    try:
        client = genai.Client(api_key=key.strip())
        response = client.models.generate_content(model=model_name, contents=prompt)
        if response.text and len(response.text.strip()) > 50:
            return response.text.strip()
    except:
        return None
    return None

def generate_fast(prompt, key, name, goal, intensity, diet, bmi, age, weight, height, gender, allergies):
    unique_prompt = f"{prompt}\nMake unique. Seed:{random.randint(10000,999999)}"
    fastest_models = ["gemini-2.0-flash-lite","gemini-2.5-flash-lite","gemini-2.0-flash","gemini-1.5-flash-8b","gemini-1.5-flash"]
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(call_model, m, unique_prompt, key): m for m in fastest_models}
            for future in concurrent.futures.as_completed(futures, timeout=9):
                res = future.result()
                if res:
                    return res
    except:
        pass
    return get_dynamic_plan(name, goal, intensity, diet, bmi, age, weight, height, gender, allergies)

st.markdown("<h2 style='text-align:center'>💪 FitBuddy - AI Fitness Plan Generator</h2>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["Scenario 1: Generate Plan", "Scenario 2: Update Feedback", "Scenario 3: Tip"])

with tab1:
    with st.form("form1"):
        name = st.text_input("Name *")
        c1,c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", 10, 100, 21)
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 60.0)
            intensity = st.selectbox("Intensity *", ["Low","Medium","High"])
        with c2:
            height = st.number_input("Height (cm)", 100.0, 250.0, 164.97)
            gender = st.selectbox("Gender", ["Female","Male","Other"])
            activity = st.selectbox("Activity Level", ["Sedentary","Lightly Active","Moderately Active","Very Active"])
        goal = st.selectbox("Fitness Goal *", ["Weight Loss","Muscle Gain","General Fitness"])
        diet = st.radio("Diet", ["Vegetarian","Non-Vegetarian","Vegan"], horizontal=True)
        allergies = st.text_input("Allergies / Foods to Avoid")
        submit = st.form_submit_button("🚀 Generate My 7-Day Plan", use_container_width=True)
    if submit:
        if not name.strip():
            st.error("Enter Name")
        else:
            bmi = weight / ((height/100)**2)
            prompt = f"Create 7-day {goal} workout plan for {name}, age {age}, {weight}kg, {height}cm, BMI {bmi:.1f}, {gender}, intensity {intensity}, activity {activity}, diet {diet}, avoid {allergies}. Include day-wise exercise with sets reps rest + 1 nutrition tip + 1 recovery tip. Indian context, short structured."
            with st.spinner("Generating..."):
                plan = generate_fast(prompt, api_key, name, goal, intensity, diet, bmi, age, weight, height, gender, allergies)
            st.session_state[f"plan_{name.lower().strip()}"] = plan
            st.session_state["last_name"] = name.lower().strip()
            try:
                c=get_db(); c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?)", (name.lower().strip(), plan, goal, bmi, weight, height)); c.commit(); c.close()
            except: pass
            st.success("✅ Plan Ready!"); st.markdown(plan)
            st.download_button("📥 Download Plan", plan, file_name=f"{name}_plan.txt")

with tab2:
    st.subheader("🔄 Scenario 2: Update My Plan")
    fb_name = st.text_input("Your Name * (same as Scenario 1)", key="fb2", value=st.session_state.get("last_name",""))
    feedback = st.text_area("Feedback *", placeholder="e.g. knee pain no squats, add more cardio", key="fb_text")
    if st.button("🔄 Update My Plan", use_container_width=True):
        if not fb_name.strip() or not feedback.strip():
            st.error("Enter Name and Feedback")
        else:
            prev = st.session_state.get(f"plan_{fb_name.lower().strip()}")
            if not prev:
                try:
                    c=get_db(); cur=c.cursor(); cur.execute("SELECT plan FROM users WHERE name=?", (fb_name.lower().strip(),)); row=cur.fetchone(); c.close()
                    if row: prev=row[0]
                except: pass
            if not prev:
                st.warning("No previous plan. Generate in Tab 1 first.")
            else:
                with st.spinner("Updating..."):
                    upd_prompt = f"Update this fitness plan based on feedback '{feedback}'. Original: {prev}. Short structured."
                    updated = generate_fast(upd_prompt, api_key, fb_name, "General Fitness", "Medium", "Vegetarian", 22.0, 21, 60, 165, "Other", "")
                st.success("✅ Updated!"); st.markdown(updated); st.session_state[f"plan_{fb_name.lower().strip()}"]=updated

with tab3:
    st.subheader("💡 Scenario 3: Get Tip")
    g = st.selectbox("Goal", ["Weight Loss","Muscle Gain","General Fitness"], key="tipg")
    tip_type = st.radio("Tip Type", ["Nutrition Tip","Recovery Tip"], horizontal=True, key="tipr")
    if st.button("💡 Get My Tip", use_container_width=True):
        with st.spinner(f"Getting {tip_type}..."):
            tip_prompt = f"Give 2-3 line {tip_type} for goal {g}, Indian diet friendly, practical. Seed {random.randint(1,999999)}"
            tip_result = None
            try:
                client = genai.Client(api_key=api_key.strip())
                for m in ["gemini-2.0-flash-lite","gemini-2.0-flash","gemini-1.5-flash"]:
                    try:
                        r = client.models.generate_content(model=m, contents=tip_prompt)
                        if r.text and len(r.text)>20:
                            tip_result=r.text.strip(); break
                    except: continue
            except: pass
            if not tip_result:
                random.seed(datetime.now().microsecond)
                if "Nutrition" in tip_type:
                    tip_result = f"**For {g}:** {random.choice(['30g protein/meal','1 bowl dal+curd+roti','2 eggs / 100g paneer'])} + 3L water + fruit."
                else:
                    tip_result = f"**For {g}:** Sleep {random.choice(['7.5','8'])}hrs + 10min stretch + {random.randint(8,12)}k steps."
        st.info(tip_result)
