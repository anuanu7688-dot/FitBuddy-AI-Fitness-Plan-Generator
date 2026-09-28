# 6. Project Testing

## Testing Objective

Testing is performed to verify that FitBuddy works correctly according to
the project requirements.

## Test Case 1 – Home Page

### Input

Open the application.

### Expected Result

The FitBuddy form should be displayed.

### Status

Pass / Fail

---

## Test Case 2 – Generate Fitness Plan

### Input

Enter:

- Name
- Age
- Weight
- Goal
- Workout intensity

### Expected Result

A personalized 7-day fitness plan should be generated.

### Status

Pass / Fail

---

## Test Case 3 – Nutrition Tip

### Input

Select a fitness goal.

### Expected Result

A relevant nutrition or recovery tip should be displayed.

### Status

Pass / Fail

---

## Test Case 4 – Feedback

### Input

Enter feedback such as:

"Add more cardio and include more rest days."

### Expected Result

The system should generate an updated fitness plan.

### Status

Pass / Fail

---

## Test Case 5 – Database

### Input

Generate a fitness plan.

### Expected Result

The user information and plan should be stored in SQLite.

### Status

Pass / Fail

---

## Test Case 6 – Health API

### Endpoint

GET /health

### Expected Result

The API should return a running status.

### Status

Pass / Fail

---

## Test Case 7 – Invalid Input

### Input

Submit the form without required information.

### Expected Result

The form should prevent submission of required empty fields.

### Status

Pass / Fail

---

## Test Case 8 – Gemini API Error

### Condition

Gemini API is unavailable or the API key is missing.

### Expected Result

The application should show an error instead of crashing silently.

### Status

Pass / Fail
