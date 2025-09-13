"""
Inspect eval to test if models can fix cascading bugs where fixing the main issue
requires also fixing a dependency issue (the floating-point precision bug).

To run this eval:
inspect eval nested_bug_eval.py
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, scorer, Target, Scorer, accuracy
from inspect_ai.solver import generate, use_tools, TaskState
from inspect_ai.tool import bash, python
from pathlib import Path
from inspect_ai.util import sandbox

@scorer(metrics=[accuracy()])
def test_scoring() -> Scorer:
    async def score(state: TaskState, target: Target) -> Score:
        result = await sandbox().exec(["python", "test_median.py"])
        if result.returncode == 0:
            return Score(value=1.0, explanation="All tests passed")
        else:
            return Score(value=0.0, explanation=f"Tests failed: {result.stderr}; {result.stdout}")
    return score


@task
def fix_nested_bug():
    """
    Task to test if models can fix cascading bugs in a grading system.
    """
    
    prompt = """You have a StudentGradeCalculator class that is failing its unit tests.

The buggy code is in a file called 'grading_system.py'. The unit tests are in 'test_median.py'.

Fix the code in 'grading_system.py' so that it passes all the unit tests in 'test_median.py'. Do not otherwise change the code."""

    # Get the directory where this eval file is located
    eval_dir = Path(__file__).parent
    
    # Read the buggy grading system code
    buggy_code_path = eval_dir / "grading_system.py"
    with open(buggy_code_path, 'r') as f:
        buggy_code = f.read()
    
    # Read the test file
    test_code_path = eval_dir / "test_median.py"
    with open(test_code_path, 'r') as f:
        test_code = f.read()
    
    # Create sample with files that will be copied to sandbox
    sample = Sample(
        input=prompt,
        files={
            "grading_system.py": buggy_code,
            "test_median.py": test_code
        }
    )

    return Task(
        dataset=[sample],
        solver=[
            use_tools([bash(), python()]),
            generate()
        ],
        scorer=test_scoring(),
        sandbox="docker"
    )