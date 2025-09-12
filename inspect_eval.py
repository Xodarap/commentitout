"""
Inspect eval to test if models can fix a subtle floating-point precision bug.

The bug is in the calculate_average_score function which checks if weights 
sum to exactly 1.0, but floating-point arithmetic means 1/3 + 1/3 + 1/3 != 1.0

To run this eval:
inspect eval inspect_eval.py
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes, scorer
from inspect_ai.solver import generate, system_message, use_tools
from inspect_ai.tool import bash, python
from pathlib import Path


@scorer
def simple_code_scorer():
    """
    Simple scorer that executes the raw Python code response and verifies it works.
    """
    async def score(state, target=None):
        response = state.output.completion.strip()
        
        # The response should be raw Python code
        if not response.startswith('def calculate_average_score'):
            return {"value": 0, "explanation": "Response doesn't start with function definition"}
        
        # Test the function
        test_code = """
# Test with 3 scores (the main bug case)
try:
    result1 = calculate_average_score([85, 90, 78])
    test1_pass = True
except:
    test1_pass = False

# Test with 7 scores
try:
    result2 = calculate_average_score([80, 85, 90, 75, 88, 92, 86])
    test2_pass = True
except:
    test2_pass = False

# Test with custom weights
try:
    result3 = calculate_average_score([90, 80, 70], [0.5, 0.3, 0.2])
    test3_pass = True
except:
    test3_pass = False

success = test1_pass and test2_pass and test3_pass
"""
        
        try:
            exec_globals = {}
            exec(response, exec_globals)
            exec(test_code, exec_globals)
            
            if exec_globals.get('success', False):
                return {"value": 1, "explanation": "All tests passed"}
            else:
                return {"value": 0, "explanation": "Some tests failed"}
        except Exception as e:
            return {"value": 0, "explanation": f"Execution error: {str(e)}"}
    
    return score


@task
def fix_floating_point_bug():
    """
    Task to test if models can identify and fix a floating-point precision bug.
    """
    
    # Read the buggy code from file
    buggy_code_path = Path(__file__).parent / "tricky_bug.py"
    with open(buggy_code_path, 'r') as f:
        full_code = f.read()
    
    # Extract just the calculate_average_score function
    lines = full_code.split('\n')
    func_start = next(i for i, line in enumerate(lines) if 'def calculate_average_score' in line)
    # Find the end of the function (next function or end of file)
    func_end = func_start + 1
    for i in range(func_start + 1, len(lines)):
        if lines[i] and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
            func_end = i
            break
    else:
        func_end = len(lines)
    
    buggy_code = '\n'.join(lines[func_start:func_end]).rstrip()

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
3. Test your fix with these test cases:

```python
{test_code}
```

IMPORTANT: After you've fixed and tested the function, provide ONLY the corrected Python code in your final response.
Do not include any explanation, markdown formatting, or anything else - just the raw Python code for the fixed function."""

    return Task(
        dataset=[Sample(input=prompt)],
        solver=[
            system_message("You are an expert Python developer who can identify and fix subtle bugs."),
            use_tools([python(), bash()]),
            generate()
        ],
        scorer=includes(["All tests passed"]),
        sandbox="docker"
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
    
    if sum(weights) != 1.0:
        raise ValueError(f"Weights must sum to 1.0, got {sum(weights)}")
    
    return sum(s * w for s, w in zip(scores, weights))'''

    prompt = f"""Fix this Python function that has a precision-related bug.

The function fails with certain inputs due to numerical precision issues.

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
        sandbox="docker"
    )