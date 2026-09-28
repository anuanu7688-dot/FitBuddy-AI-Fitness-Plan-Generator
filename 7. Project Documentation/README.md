# 7. Project Documentation

## Project Title

FitBuddy – AI Fitness Plan Generator using Gemini Models

## Abstract

FitBuddy is a web-based application that uses Generative AI to create
personalized fitness plans.

The application accepts user information such as age, weight, fitness goal
and workout intensity.

Gemini AI generates a structured 7-day fitness plan.

The system also provides nutrition or recovery guidance and allows users to
provide feedback so that the plan can be updated.

## Technologies Used

- Python
- FastAPI
- Gemini AI
- SQLite
- HTML
- CSS
- Jinja2
- Uvicorn

## Main Modules

### User Interface

Collects user information and displays fitness plans.

### FastAPI

Handles application routing and API requests.

### Gemini Service

Communicates with Gemini AI to generate and update fitness plans.

### Database

SQLite stores user information and generated plans.

## Application Workflow

1. User opens FitBuddy.
2. User enters personal information.
3. User selects a fitness goal.
4. User selects workout intensity.
5. FastAPI processes the request.
6. Gemini generates the fitness plan.
7. SQLite stores the result.
8. The plan is displayed.
9. User can provide feedback.
10. Gemini generates an updated plan.

## Safety

FitBuddy provides general fitness guidance. It should not be treated as a
replacement for professional medical or fitness advice.

Users with medical conditions or special requirements should seek advice from
a qualified professional.
