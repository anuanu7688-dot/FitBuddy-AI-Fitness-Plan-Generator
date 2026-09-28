# 3. Project Design Phase

## System Architecture

FitBuddy follows a simple three-layer architecture.

### 1. Presentation Layer

The presentation layer contains:

- HTML
- CSS
- Jinja2 templates

It collects user input and displays the generated fitness plan.

### 2. Application Layer

FastAPI manages:

- Routing
- User input
- API requests
- Gemini AI requests
- Feedback processing

### 3. Data Layer

SQLite stores:

- User information
- Fitness goals
- Workout intensity
- Generated plans

## Architecture Flow

User Interface
       |
       v
FastAPI Application
       |
       +------> Gemini AI
       |
       +------> SQLite Database
       |
       v
HTML Response

## Main Components

### app.py

Main application logic and API routes.

### gemini_service.py

Handles communication with Gemini AI.

### database.py

Handles SQLite database operations.

### models.py

Defines request models used by FastAPI.

### templates

Contains HTML pages.

### static

Contains CSS files.

## Data Flow

User Input
   |
   v
FastAPI
   |
   v
Gemini Prompt
   |
   v
Gemini AI
   |
   v
7-Day Fitness Plan
   |
   v
SQLite
   |
   v
Web Interface
