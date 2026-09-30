import os
from google import genai

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )
    return genai.Client(api_key=api_key)

def generate_fitness_plan(name, age, weight, goal, intensity):
    client = get_client()
    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a personalized 7-day fitness plan.

User details:
Name: {name}
Age: {age}
Weight: {weight} kg
Fitness goal: {goal}
Workout intensity: {intensity}

Requirements:
1. Create Day 1 through Day 7.
2. Include suitable exercises.
3. Mention approximate duration.
4. Include rest or recovery days when appropriate.
5. Give a nutrition tip.
6. Give a recovery tip.
7. Keep recommendations practical.
8. Do not provide dangerous or extreme advice.
9. Make the answer easy to read.
10. Mention that general fitness guidance is not a substitute for
professional medical advice when appropriate.

Return only the fitness plan.
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text

def update_fitness_plan(old_plan, feedback):
    client = get_client()
    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Existing plan:
{old_plan}

User feedback:
{feedback}

Create an updated 7-day fitness plan.

Requirements:
1. Keep useful parts of the original plan.
2. Apply the user's feedback.
3. Show Day 1 through Day 7.
4. Include suitable workouts.
5. Include recovery guidance.
6. Include a nutrition or recovery tip.
7. Keep recommendations practical and safe.
8. Return only the updated fitness plan.
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text

def generate_goal_tip(goal):
    client = get_client()
    prompt = f"""
Provide one short and practical nutrition or recovery tip
for a person whose fitness goal is:
{goal}
Keep the advice general, safe and easy to understand.
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text
