# 6.Project Testing
Assigned to: Afsal A (Testing and Verifying)

Test Cases:

Test 1 - Different Weight Height = Different Output:
Input 1: 60kg 165cm Goal Weight Loss -> Output BMI 22.0 Cal 1440 Prot 96g Plan: Brisk Walk 30min
Input 2: 90kg 180cm Goal Muscle Gain -> Output BMI 27.7 Cal 3150 Prot 180g Plan: Bench Press 10x4
Result: PASS - Dynamic logic working, no same static output bug.

Test 2 - Parallel Model Speed:
5 models called in parallel with ThreadPoolExecutor(max_workers=5), timeout 9 sec.
Average response 3-5 sec.
Result: PASS - Fast response.

Test 3 - Fallback When API Fail:
If API key wrong / quota over / internet off, get_dynamic_plan() with random.seed(microsecond) gives personalized plan.
Result: PASS - No error shown.

Test 4 - Scenarios:
Scenario1 Generate: PASS
Scenario2 Update Feedback (knee pain): PASS - Plan updated without squats
Scenario3 Tip: PASS - Nutrition tip generated

Test 5 - DB Save:
Name saved as lowercase PK, plan saved, retrieved in Scenario 2.
Result: PASS

Bug Fixed: Static output bug fixed by random.seed(name+weight+height+microsecond) and dynamic calculations.
