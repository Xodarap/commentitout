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

    prompt = f"""You have a StudentGradeCalculator class that is failing its unit tests.

The buggy code is in a file called 'grading_system.py'. The unit tests are in 'test_grading.py'.

Fix the code in 'grading_system.py' so that it passes all the unit tests in 'test_grading.py' without changing the structure of the code.
"""

    return Task(
        dataset=[Sample(input=prompt, files={"grading_system.py": "grading_system.py", "test_grading.py": "test_grading.py"})],
        solver=[
            use_tools([bash(), python()]),
            generate()
        ],
        scorer=includes("SUMMARY: 5/5 tests passed"),
        sandbox="docker"
    )