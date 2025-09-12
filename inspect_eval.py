"""
Inspect eval to test if models can fix a subtle floating-point precision bug.

The bug is in the calculate_average_score function which checks if weights 
sum to exactly 1.0, but floating-point arithmetic means 1/3 + 1/3 + 1/3 != 1.0

To run this eval:
inspect eval inspect_eval.py
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes, match
from inspect_ai.solver import generate, system_message, use_tools
from inspect_ai.tool import bash, python

@task
def fix_floating_point_bug():
    """
    Task to test if models can identify and fix a floating-point precision bug.
    """
    
    # The buggy code that needs to be fixed
    buggy_code = '''def calculate_average_score(scores, weights=None):
    """
    Calculate weighted average of scores.
    
    Args:
        scores: List of numerical scores
        weights: Optional list of weights (must sum to 1.0)
    
    Returns:
        Weighted average of scores
    """
    if not scores:
        return 0
    
    if weights is None:
        weights = [1/len(scores)] * len(scores)
    
    if len(scores) != len(weights):
        raise ValueError("Scores and weights must have same length")
    
    # Bug: The weights might not sum to exactly 1.0 due to floating point precision
    # This will throw an exception when weights are auto-generated for certain list lengths
    if sum(weights) != 1.0:
        raise ValueError(f"Weights must sum to 1.0, got {sum(weights)}")
    
    return sum(s * w for s, w in zip(scores, weights))'''

    # Test cases that should work after the fix
    test_code = '''
# Test with 3 scores (1/3 + 1/3 + 1/3)
scores1 = [85, 90, 78]
result1 = calculate_average_score(scores1)
print(f"Test 1 passed: {result1}")

# Test with 7 scores 
scores2 = [80, 85, 90, 75, 88, 92, 86]
result2 = calculate_average_score(scores2)
print(f"Test 2 passed: {result2}")

# Test with custom weights that sum to 1.0
scores3 = [90, 80, 70]
weights3 = [0.5, 0.3, 0.2]
result3 = calculate_average_score(scores3, weights3)
print(f"Test 3 passed: {result3}")

print("All tests passed!")
'''

    prompt = f"""You are given a Python function that has a bug related to floating-point precision. 
The function throws an exception when it shouldn't.

Here's the buggy code:

```python
{buggy_code}
```

When you call this function with certain inputs like `calculate_average_score([85, 90, 78])`, 
it raises a ValueError even though it should work correctly.

Your task:
1. Identify why the function fails
2. Fix the bug while maintaining the function's intended behavior
3. Ensure the fixed function passes all test cases

Provide your fixed version of the function, then run these tests to verify it works:

```python
{test_code}
```

The fix should be minimal and maintain the original function's purpose of calculating weighted averages."""

    return Task(
        dataset=[Sample(input=prompt)],
        solver=[
            system_message("You are an expert Python developer who can identify and fix subtle bugs."),
            use_tools([python(), bash()]),
            generate()
        ],
        scorer=includes(["All tests passed", "Test 1 passed", "Test 2 passed", "Test 3 passed"]),
        sandbox="local"
    )


# Alternative task with more guidance
@task
def fix_floating_point_bug_guided():
    """
    Task with hints about the floating-point precision issue.
    """
    
    buggy_code = '''def calculate_average_score(scores, weights=None):
    if not scores:
        return 0
    
    if weights is None:
        weights = [1/len(scores)] * len(scores)
    
    if len(scores) != len(weights):
        raise ValueError("Scores and weights must have same length")
    
    if sum(weights) != 1.0:  # This line has the bug
        raise ValueError(f"Weights must sum to 1.0, got {sum(weights)}")
    
    return sum(s * w for s, w in zip(scores, weights))'''

    prompt = f"""Fix this Python function that has a floating-point precision bug.

The bug is in this line: `if sum(weights) != 1.0:`

When weights are auto-generated (e.g., [1/3, 1/3, 1/3]), the sum might be 0.9999999999999999 
instead of exactly 1.0 due to floating-point arithmetic.

Fix this bug by using an appropriate tolerance for the comparison instead of exact equality.

Original buggy code:
```python
{buggy_code}
```

Your fix should:
1. Use a small epsilon value (like 1e-10) for tolerance
2. Check if the sum is approximately 1.0, not exactly 1.0
3. Keep all other functionality the same

Test your fix with: calculate_average_score([85, 90, 78])"""

    return Task(
        dataset=[Sample(input=prompt)],
        solver=[
            use_tools([python()]),
            generate()
        ],
        scorer=includes("abs(sum(weights) - 1.0) < 1e-"),
        sandbox="local"
    )