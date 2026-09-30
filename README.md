# FitBuddy – AI Fitness Plan Generator using Gemini Models

## Team Members

- Anushree P
- Avinth Atchai C
- Ahammed Sha
- Afsal A

## Project Overview

FitBuddy is an AI-powered fitness planning application that uses Google Gemini AI to generate personalized 7-day fitness plans.

The user provides their name, age, weight, fitness goal, and preferred workout intensity. The application processes these details using FastAPI and Gemini AI, generates a personalized fitness plan, and stores the information using SQLite.

The application also allows users to provide feedback and receive an updated fitness plan.

## Problem Statement

Creating a suitable fitness plan can be difficult because users have different goals, preferences, and fitness requirements.

FitBuddy provides an AI-assisted solution for generating personalized and structured fitness plans based on user information.

## Main Features

- Personalized 7-day fitness plan generation
- Fitness goal selection
- Workout intensity selection
- Gemini AI integration
- Nutrition tips
- Recovery tips
- Feedback-based plan regeneration
- SQLite database storage
- FastAPI backend
- HTML and CSS frontend
- Jinja2 templates
- API endpoints
- Health check endpoint
- Error handling

## Project Scenarios

### Scenario 1 – Personalized Fitness Plan

The user enters their name, age, weight, fitness goal, and workout intensity. Gemini AI generates a personalized 7-day fitness plan.

### Scenario 2 – Feedback-Based Plan Update

The user provides feedback about the generated plan. Gemini AI uses the existing plan and feedback to create an updated plan.

### Scenario 3 – Nutrition or Recovery Tip

The application provides a suitable nutrition or recovery tip based on the user's selected fitness goal.

## Technology Stack

- Python
- FastAPI
- Gemini AI with automatic multi-model fallback
- SQLite
- Jinja2
- HTML
- CSS
- Uvicorn

## Application Architecture

```text
User
  |
  v
HTML/CSS Frontend
  |
  v
FastAPI Backend
  |
  +------------> Gemini AI
  |
  +------------> SQLite Database
  |
  v
Personalized 7-Day Fitness Plan
  |
  v
User Feedback
  |
  v
Gemini AI
  |
  v
Updated Fitness Plan

## Project Folder Structure

```text
FitBuddy-AI-Fitness-Plan-Generator/
│
├── README.md
│
├── 1. Brainstorming & Ideation/
│   └── README.md
│
├── 2. Requirement Analysis/
│   └── README.md
│
├── 3. Project Design Phase/
│   └── README.md
│
├── 4. Project Planning Phase/
│   └── README.md
│
├── 5. Project Development Phase/
│   ├── app.py
│   ├── database.py
│   ├── gemini_service.py
│   ├── models.py
│   ├── requirements.txt
│   │
│   ├── templates/
│   │   ├── index.html
│   │   └── result.html
│   │
│   └── static/
│       └── style.css
│
├── 6. Project Testing/
│   └── README.md
│
├── 7. Project Documentation/
│   └── README.md
│
└── 8. Project Demonstration/
    └── README.md

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/anuanu7688-dot/FitBuddy-AI-Fitness-Plan-Generator.git
cd FitBuddy-AI-Fitness-Plan-Generator

### 2. Go to the Project Development Folder

```bash
cd "5. Project Development Phase"

### 3. Install Required Packages

```bash
pip install -r requirements.txt

### 4. Set Gemini API Key

Set your Gemini API key as an environment variable:

```text
GEMINI_API_KEY

### 5. Run the Application

```bash
uvicorn app:app --reload

### 6. Open the Application

Open the following address in your web browser:

```text
http://127.0.0.1:8000

## API Endpoints

- `GET /` – Displays the FitBuddy home page.
- `POST /generate` – Generates a personalized fitness plan.
- `POST /feedback` – Updates the fitness plan based on user feedback.
- `POST /api/generate-plan` – API for generating a fitness plan.
- `POST /api/feedback` – API for updating a fitness plan.
- `POST /api/tip` – Generates a nutrition or recovery tip.
- `GET /health` – Checks whether the application is running.

## Database

FitBuddy uses SQLite to store user information and generated fitness plans.

The database stores:

- User name
- Age
- Weight
- Fitness goal
- Workout intensity
- Generated fitness plan
- User feedback

## Team Member Contributions

### Anushree P
- Topic links
- Development environment setup
- Main application logic
- `app.py`
- Project conclusion

### Avinth Atchai C
- Project workflow
- Core functionality
- User interface

### Ahammed Sha
- Gemini model research and selection
- FastAPI backend
- Jinja2 templates

### Afsal A
- Application architecture
- Local deployment
- Project testing

## Testing

The FitBuddy application is tested for:

- User input validation
- Fitness plan generation
- Gemini AI integration
- Feedback-based plan updates
- Nutrition and recovery tips
- SQLite database storage
- API endpoint functionality
- Health check endpoint
- Error handling

## Safety Note

FitBuddy provides general AI-generated fitness guidance for informational purposes only.

Users should consider their individual health conditions and consult a qualified healthcare or fitness professional when necessary.

The application does not replace professional medical advice.


## Project Workflow

1. User enters personal fitness details.
2. FastAPI receives the user input.
3. Gemini AI processes the information.
4. A personalized 7-day fitness plan is generated.
5. The plan is displayed to the user.
6. User can provide feedback.
7. Gemini AI updates the fitness plan based on the feedback.
8. User information and plans are stored in SQLite.

## Project Documentation and Demonstration

The project documentation explains the development process, system design, implementation, testing, and results.

The project demonstration will show:

- User input
- AI-generated 7-day fitness plan
- Nutrition or recovery tip
- Feedback-based plan update
- SQLite database storage
- Working FastAPI application

## Conclusion

FitBuddy provides an AI-assisted approach to personalized fitness planning.

By combining FastAPI, Gemini AI, SQLite, HTML, CSS, and Jinja2, the application can generate personalized fitness plans, provide nutrition and recovery tips, and update plans based on user feedback.

The project demonstrates how AI can be integrated into a practical web application.
