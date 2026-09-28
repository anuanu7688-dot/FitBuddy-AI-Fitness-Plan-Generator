# 2. Requirement Analysis

## Functional Requirements

### FR1 – User Input

The system shall allow users to enter:

- Name
- Age
- Weight
- Fitness goal
- Workout intensity

### FR2 – Fitness Plan Generation

The system shall generate a personalized 7-day fitness plan using Gemini AI.

### FR3 – Daily Workout Schedule

The generated plan shall contain daily workout information from Day 1 to Day 7.

### FR4 – Nutrition and Recovery

The system shall provide a relevant nutrition or recovery tip based on
the user's fitness goal.

### FR5 – Feedback

The user shall be able to provide feedback about an existing fitness plan.

### FR6 – Plan Regeneration

The system shall use the user's feedback to generate an updated fitness plan.

### FR7 – Database

The system shall store user information and generated plans using SQLite.

### FR8 – Web Interface

The system shall provide an interactive HTML interface.

### FR9 – API

The system shall provide API endpoints for important application operations.

### FR10 – Health Check

The system shall provide a health endpoint to verify that the application
is running.

## Non-Functional Requirements

### Performance

The application should respond efficiently to normal user requests.

### Usability

The interface should be simple and easy to understand.

### Security

The Gemini API key must not be stored directly in source code.

### Maintainability

The application should be divided into separate modules.

### Reliability

The system should handle errors from the AI service gracefully.

## User Scenarios

### Scenario 1 – Generate Fitness Plan

1. User opens FitBuddy.
2. User enters personal details.
3. User selects a fitness goal.
4. User selects workout intensity.
5. User submits the form.
6. Gemini generates a personalized 7-day plan.
7. The plan is stored in SQLite.
8. The plan is displayed to the user.

### Scenario 2 – Update Existing Plan

1. User views the existing plan.
2. User enters feedback.
3. The feedback is sent to Gemini.
4. Gemini modifies the plan.
5. The updated plan is stored.
6. The updated plan is displayed.

### Scenario 3 – Nutrition or Recovery Tip

1. User selects a fitness goal.
2. The system considers the selected goal.
3. Gemini provides a suitable nutrition or recovery tip.
4. The tip is displayed with the fitness plan.
