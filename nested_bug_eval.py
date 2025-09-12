"""
Inspect eval to test if models can fix a cascading bug where fixing the main issue
requires also fixing a dependency issue (the floating-point precision bug).

To run this eval:
inspect eval nested_bug_eval.py
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes, Scorer, scorer
from inspect_ai.solver import generate, system_message, use_tools
from inspect_ai.tool import python
from pathlib import Path
import re


@scorer
def grading_system_scorer():
    """
    Custom scorer that executes the fixed grading system code
    and verifies it works correctly.
    """
    async def score(state, target=None):
        response = state.output.completion
        
        # Extract Python code from the response
        code_blocks = re.findall(r'```python\n(.*?)\n```', response, re.DOTALL)
        
        if not code_blocks:
            # Try to find the code directly
            if 'def calculate_average_score' in response and 'class StudentGradeCalculator' in response:
                code_blocks = [response]
        
        if not code_blocks:
            return {"value": 0, "explanation": "No complete code found in response"}
        
        # Get the most complete code block
        fixed_code = code_blocks[-1]
        
        # Ensure both function and class are present
        if 'def calculate_average_score' not in fixed_code or 'class StudentGradeCalculator' not in fixed_code:
            return {"value": 0, "explanation": "Missing calculate_average_score or StudentGradeCalculator"}
        
        # Test code
        test_code = """
# Test 1: 3 quiz scores (tests floating-point fix)
try:
    calculator = StudentGradeCalculator()
    grade1 = calculator.calculate_final_grade([85, 90, 88], [92, 88], 95)
    test1_passed = grade1 in ['A', 'B']  # Should be high grade
except Exception as e:
    test1_passed = False
    test1_error = str(e)

# Test 2: 7 quiz scores
try:
    grade2 = calculator.calculate_final_grade([75, 80, 85, 90, 78, 82, 88], [85, 90, 87], 90)
    test2_passed = grade2 in ['A', 'B']
except Exception as e:
    test2_passed = False
    test2_error = str(e)

# Test 3: Verify weights sum to 1.0
try:
    # Perfect quizzes, moderate exams, perfect participation
    # With correct weights (0.3, 0.6, 0.1): 100*0.3 + 60*0.6 + 100*0.1 = 76 (C)
    # With buggy weights (0.3, 0.6, 0.15): 100*0.3 + 60*0.6 + 100*0.15 = 81 (B)
    grade3 = calculator.calculate_final_grade([100, 100, 100], [60, 60], 100)
    test3_passed = grade3 == 'C'  # Should be C with correct weights, B with bug
except Exception as e:
    test3_passed = False
    test3_error = str(e)

# Test 4: Verify calculate_average_score works with various lengths
try:
    avg1 = calculate_average_score([80, 90, 85])
    avg2 = calculate_average_score([100, 100, 100, 100])
    test4_passed = abs(avg1 - 85) < 1 and abs(avg2 - 100) < 0.01
except Exception as e:
    test4_passed = False
    test4_error = str(e)

all_passed = test1_passed and test2_passed and test3_passed and test4_passed
"""
        
        # Execute the fixed code with tests
        try:
            exec_globals = {}
            exec(fixed_code, exec_globals)
            exec(test_code, exec_globals)
            
            if exec_globals.get('all_passed', False):
                return {"value": 1, "explanation": "All tests passed"}
            else:
                failed = []
                if not exec_globals.get('test1_passed', False):
                    error = exec_globals.get('test1_error', '')
                    failed.append(f"Test 1 (3 quiz scores): {error}")
                if not exec_globals.get('test2_passed', False):
                    error = exec_globals.get('test2_error', '')
                    failed.append(f"Test 2 (7 quiz scores): {error}")
                if not exec_globals.get('test3_passed', False):
                    error = exec_globals.get('test3_error', '')
                    failed.append(f"Test 3 (weight verification): {error}")
                if not exec_globals.get('test4_passed', False):
                    error = exec_globals.get('test4_error', '')
                    failed.append(f"Test 4 (averaging): {error}")
                return {"value": 0, "explanation": f"Failed: {'; '.join(failed)}"}
                
        except Exception as e:
            return {"value": 0, "explanation": f"Execution error: {str(e)}"}
    
    return score


@task
def fix_nested_bug():
    """
    Task to test if models can fix a bug that requires fixing another bug first.
    The student grading system has a bug, but it also depends on calculate_average_score
    which has its own floating-point precision bug.
    """
    
    # Read the buggy code from file
    buggy_code_path = Path(__file__).parent / "buggy_grading_system.py"
    with open(buggy_code_path, 'r') as f:
        buggy_code = f.read()

    # Test code that should pass after fixes
    test_code = '''
# Test the StudentGradeCalculator
calculator = StudentGradeCalculator()

# Test case 1: Student with 3 quiz scores (triggers floating-point bug if not fixed)
quiz_scores1 = [85, 90, 88]
exam_scores1 = [92, 88]
participation1 = 95
grade1 = calculator.calculate_final_grade(quiz_scores1, exam_scores1, participation1)
print(f"Test 1 - Grade: {grade1}")

# Test case 2: Student with 7 quiz scores
quiz_scores2 = [75, 80, 85, 90, 78, 82, 88]
exam_scores2 = [85, 90, 87]
participation2 = 90
grade2 = calculator.calculate_final_grade(quiz_scores2, exam_scores2, participation2)
print(f"Test 2 - Grade: {grade2}")

# Test case 3: Verify the weights add up correctly  
# Perfect quizzes, barely passing exams, no participation
quiz_scores3 = [100, 100, 100]
exam_scores3 = [60, 60]
participation3 = 0
grade3 = calculator.calculate_final_grade(quiz_scores3, exam_scores3, participation3)
# With correct weights (0.3, 0.6, 0.1): 100*0.3 + 60*0.6 + 0*0.1 = 30 + 36 + 0 = 66 (D)
# With buggy weights (0.3, 0.6, 0.15): 100*0.3 + 60*0.6 + 0*0.15 = 30 + 36 + 0 = 66 (D) - same!

# Better test - where participation matters
quiz_scores4 = [100, 100, 100]
exam_scores4 = [60, 60]
participation4 = 100
grade4 = calculator.calculate_final_grade(quiz_scores4, exam_scores4, participation4)
# With correct weights (0.3, 0.6, 0.1): 100*0.3 + 60*0.6 + 100*0.1 = 30 + 36 + 10 = 76 (C)
# With buggy weights (0.3, 0.6, 0.15): 100*0.3 + 60*0.6 + 100*0.15 = 30 + 36 + 15 = 81 (B)
assert grade4 == 'C', f"Test 3 Failed: Expected 'C' but got '{grade4}' (weights don't sum to 1.0)"
print(f"Test 3 - Grade: {grade4} (Correct weight calculation)")

print("All tests passed!")
'''

    prompt = f"""You have a StudentGradeCalculator class that is failing its unit tests.

Here's the code:

```python
{buggy_code}
```

When you run these tests, they fail:

```python
{test_code}
```

Your task:
1. Identify why the tests are failing
2. Fix all bugs in the code
3. Ensure all tests pass

Provide the complete fixed code and run the tests to verify everything works."""

    return Task(
        dataset=[Sample(input=prompt)],
        solver=[
            system_message("You are an expert Python developer who can debug complex issues."),
            use_tools([python()]),
            generate()
        ],
        scorer=includes(["All tests passed", "Test 1", "Test 2", "Test 3"]),
        sandbox="local"
    )


@task
def fix_nested_bug_minimal():
    """
    Minimal version with less guidance.
    """
    
    buggy_code = '''def calculate_average_score(scores, weights=None):
    if not scores:
        return 0
    
    if weights is None:
        weights = [1/len(scores)] * len(scores]
    
    if len(scores) != len(weights):
        raise ValueError("Scores and weights must have same length")
    
    if sum(weights) != 1.0:
        raise ValueError(f"Weights must sum to 1.0, got {sum(weights)}")
    
    return sum(s * w for s, w in zip(scores, weights))


class StudentGradeCalculator:
    def __init__(self):
        self.grade_boundaries = {'A': 90, 'B': 80, 'C': 70, 'D': 60, 'F': 0}
    
    def calculate_final_grade(self, quiz_scores, exam_scores, participation_score):
        quiz_average = calculate_average_score(quiz_scores)
        exam_average = calculate_average_score(exam_scores)
        final_score = quiz_average * 0.3 + exam_average * 0.6 + participation_score * 0.15
        return self.get_letter_grade(final_score)
    
    def get_letter_grade(self, score):
        for grade, boundary in self.grade_boundaries.items():
            if score >= boundary:
                return grade
        return 'F'
'''

    prompt = f"""Fix the bugs in this student grading system:

```python
{buggy_code}
```

Test with:
```python
calculator = StudentGradeCalculator()
grade = calculator.calculate_final_grade([85, 90, 88], [92, 88], 95)
print(f"Grade: {{grade}}")
```

The code should calculate grades with weights: Quizzes 30%, Exams 60%, Participation 10%."""

    return Task(
        dataset=[Sample(input=prompt)],
        solver=[
            use_tools([python()]),
            generate()
        ],
        scorer=includes(["Grade:"]),
        sandbox="local"
    )