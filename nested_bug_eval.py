"""
Inspect eval to test if models can fix a cascading bug where fixing the main issue
requires also fixing a dependency issue (the floating-point precision bug).

To run this eval:
inspect eval nested_bug_eval.py
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes
from inspect_ai.solver import generate, system_message, use_tools
from inspect_ai.tool import python

@task
def fix_nested_bug():
    """
    Task to test if models can fix a bug that requires fixing another bug first.
    The student grading system has a bug, but it also depends on calculate_average_score
    which has its own floating-point precision bug.
    """
    
    # The code with both bugs
    buggy_code = '''def calculate_average_score(scores, weights=None):
    """
    Calculate weighted average of scores.
    """
    if not scores:
        return 0
    
    if weights is None:
        weights = [1/len(scores)] * len(scores)
    
    if len(scores) != len(weights):
        raise ValueError("Scores and weights must have same length")
    
    if sum(weights) != 1.0:
        raise ValueError(f"Weights must sum to 1.0, got {sum(weights)}")
    
    return sum(s * w for s, w in zip(scores, weights))


class StudentGradeCalculator:
    """
    Calculate student grades based on multiple assessment scores.
    """
    
    def __init__(self):
        self.grade_boundaries = {
            'A': 90,
            'B': 80,
            'C': 70,
            'D': 60,
            'F': 0
        }
    
    def calculate_final_grade(self, quiz_scores, exam_scores, participation_score):
        """
        Calculate final grade with weights:
        - Quizzes: 30%
        - Exams: 60%
        - Participation: 10%
        """
        # Bug: This will fail when quiz_scores has certain lengths due to the 
        # floating-point bug in calculate_average_score
        quiz_average = calculate_average_score(quiz_scores)
        exam_average = calculate_average_score(exam_scores)
        
        # Another bug: Wrong weight calculation - doesn't add up to 100%
        final_score = quiz_average * 0.3 + exam_average * 0.6 + participation_score * 0.15
        
        return self.get_letter_grade(final_score)
    
    def get_letter_grade(self, score):
        """Convert numerical score to letter grade."""
        for grade, boundary in self.grade_boundaries.items():
            if score >= boundary:
                return grade
        return 'F'
'''

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
quiz_scores3 = [100, 100, 100]
exam_scores3 = [50, 50]
participation3 = 100
grade3 = calculator.calculate_final_grade(quiz_scores3, exam_scores3, participation3)
# With correct weights (0.3, 0.6, 0.1): 100*0.3 + 50*0.6 + 100*0.1 = 30 + 30 + 10 = 70 (C)
assert grade3 == 'C', f"Expected 'C' but got '{grade3}'"
print(f"Test 3 - Grade: {grade3} (Correct weight calculation)")

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