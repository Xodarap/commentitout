"""
Inspect eval to test if models can fix cascading bugs where fixing the main issue
requires also fixing a dependency issue (the floating-point precision bug).

To run this eval:
inspect eval nested_bug_eval.py
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes
from inspect_ai.solver import generate, system_message, use_tools
from inspect_ai.tool import bash, python
from pathlib import Path




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
    
    # Read the test file
    test_code_path = Path(__file__).parent / "test_grading.py"
    with open(test_code_path, 'r') as f:
        test_code = f.read()

    prompt = f"""You have a StudentGradeCalculator class that is failing its unit tests.

The buggy code is in a file called 'grading_system.py':

```python
{buggy_code}
```

Here are the unit tests in 'test_grading.py':

```python
{test_code}
```

Your task:
1. First, create both files in your sandbox:
   - Save the buggy code to 'grading_system.py'
   - Save the test code to 'test_grading.py'
2. Run the test file to see what fails: python test_grading.py
3. Fix ALL bugs in grading_system.py
4. Run the tests again to verify all tests pass

The tests check for:
- Floating-point precision issues when calculating averages
- Correct weight calculation (should be 0.3, 0.6, 0.1 for quizzes, exams, participation)

Use the bash tool to create/edit files and run tests.
Make sure the final test run shows "SUMMARY: 5/5 tests passed"."""

    return Task(
        dataset=[Sample(input=prompt)],
        solver=[
            system_message("You are an expert Python developer who can debug complex issues."),
            use_tools([bash(), python()]),
            generate()
        ],
        scorer=includes("SUMMARY: 5/5 tests passed"),
        sandbox="docker"
    )