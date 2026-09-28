from pydantic import BaseModel


class FitnessRequest(BaseModel):
    name: str
    age: int
    weight: float
    goal: str
    intensity: str


class FeedbackRequest(BaseModel):
    user_id: int
    old_plan: str
    feedback: str


class TipRequest(BaseModel):
    goal: str
