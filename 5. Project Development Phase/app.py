from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database import create_database, save_user, update_plan
from gemini_service import generate_fitness_plan, update_fitness_plan, generate_goal_tip
from models import FitnessRequest, FeedbackRequest, TipRequest

app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="AI-powered personalized fitness planning system",
    version="1.0"
)

create_database()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.post("/generate", response_class=HTMLResponse)
async def generate_plan_page(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...)
):
    try:
        plan = generate_fitness_plan(
            name, age, weight, goal, intensity
        )

        tip = generate_goal_tip(goal)

        user_id = save_user(
            name, age, weight, goal, intensity, plan
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "name": name,
                "plan": plan,
                "tip": tip,
                "user_id": user_id
            }
        )

    except Exception as error:
        return HTMLResponse(
            f"<h2>Error</h2><p>{error}</p>",
            status_code=500
        )


@app.post("/feedback", response_class=HTMLResponse)
async def feedback_page(
    request: Request,
    user_id: int = Form(...),
    old_plan: str = Form(...),
    feedback_text: str = Form(...)
):
    try:
        updated_plan = update_fitness_plan(
            old_plan,
            feedback_text
        )

        update_plan(
            user_id,
            updated_plan,
            feedback_text
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "name": "User",
                "plan": updated_plan,
                "tip": "",
                "user_id": user_id
            }
        )

    except Exception as error:
        return HTMLResponse(
            f"<h2>Error</h2><p>{error}</p>",
            status_code=500
        )


@app.post("/api/generate-plan")
async def api_generate_plan(data: FitnessRequest):

    plan = generate_fitness_plan(
        data.name,
        data.age,
        data.weight,
        data.goal,
        data.intensity
    )

    tip = generate_goal_tip(data.goal)

    user_id = save_user(
        data.name,
        data.age,
        data.weight,
        data.goal,
        data.intensity,
        plan
    )

    return {
        "success": True,
        "user_id": user_id,
        "plan": plan,
        "tip": tip
    }


@app.post("/api/feedback")
async def api_feedback(data: FeedbackRequest):

    updated_plan = update_fitness_plan(
        data.old_plan,
        data.feedback
    )

    update_plan(
        data.user_id,
        updated_plan,
        data.feedback
    )

    return {
        "success": True,
        "user_id": data.user_id,
        "updated_plan": updated_plan
    }


@app.post("/api/tip")
async def api_tip(data: TipRequest):

    tip = generate_goal_tip(data.goal)

    return {
        "success": True,
        "goal": data.goal,
        "tip": tip
    }


@app.get("/health")
async def health():
    return {
        "status": "running",
        "application": "FitBuddy"
    }
