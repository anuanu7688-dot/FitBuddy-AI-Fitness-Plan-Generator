import os
import time
from google import genai


# Gemini models are tried in this order.
# If one model is unavailable or busy, FitBuddy
# automatically tries the next model.
GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite"
]


def get_client():
    """
    Create the Gemini API client using the
    GEMINI_API_KEY stored in the environment.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(api_key=api_key)


def generate_content_with_fallback(prompt):
    """
    Try multiple Gemini models automatically.

    If the first model is busy, unavailable, or temporarily
    fails, the next model is tried automatically.
    """

    client = get_client()

    errors = []

    for model_name in GEMINI_MODELS:

        try:
            print(f"Trying Gemini model: {model_name}")

            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            if response.text:
                print(f"Success with model: {model_name}")
                return response.text

        except Exception as error:

            error_message = str(error)

            print(
                f"Model {model_name} failed: "
                f"{error_message}"
            )

            errors.append(
                f"{model_name}: {error_message}"
            )

            # Wait briefly before trying the next model
            time.sleep(1)

            continue

    # If every model failed
    raise RuntimeError(
        "All Gemini models are currently unavailable.\n\n"
        + "\n".join(errors)
    )


def generate_fitness_plan(
    name,
    age,
    weight,
    goal,
    intensity
):
    """
    Generate a personalized 7-day fitness plan.
    """

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a personalized 7-day fitness plan for the user.

User Details:

Name: {name}
Age: {age}
Weight: {weight} kg
Fitness Goal: {goal}
Workout Intensity: {intensity}

Requirements:

1. Create a complete plan from Day 1 to Day 7.
2. Include suitable exercises for each day.
3. Mention approximate workout duration.
4. Include rest or recovery days when appropriate.
5. Give a simple nutrition tip.
6. Give a simple recovery tip.
7. Make the plan practical and easy to follow.
8. Do not provide dangerous, extreme, or unrealistic advice.
9. Keep the answer clearly structured.
10. Consider the user's fitness goal and workout intensity.
11. Mention that this is general fitness guidance and is not
    a substitute for professional medical advice when appropriate.

Return only the fitness plan.
"""

    return generate_content_with_fallback(prompt)


def update_fitness_plan(old_plan, feedback):
    """
    Update an existing fitness plan based on user feedback.
    """

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Existing fitness plan:

{old_plan}

User feedback:

{feedback}

Create an updated 7-day fitness plan based on the feedback.

Requirements:

1. Keep useful parts of the original plan.
2. Apply the user's feedback.
3. Show Day 1 through Day 7.
4. Include suitable workouts.
5. Include approximate workout duration.
6. Include rest or recovery guidance.
7. Include a nutrition or recovery tip.
8. Keep recommendations practical and safe.
9. Do not provide dangerous or extreme advice.
10. Make the updated plan easy to understand.

Return only the updated fitness plan.
"""

    return generate_content_with_fallback(prompt)


def generate_goal_tip(goal):
    """
    Generate a short nutrition or recovery tip
    based on the user's fitness goal.
    """

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

The user's fitness goal is:

{goal}

Provide one short and practical nutrition or recovery tip
that supports this goal.

Requirements:

1. Keep the advice general and safe.
2. Make it easy to understand.
3. Keep it practical.
4. Do not provide extreme diet advice.
5. Return only the tip.
"""

    return generate_content_with_fallback(prompt)
