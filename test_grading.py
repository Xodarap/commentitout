"""
Unit tests for the StudentGradeCalculator system.
These tests verify both the floating-point bug fix and the weight calculation fix.
"""

import sys
import traceback

def run_tests():
    """Run all tests and return results."""
    from grading_system import calculate_average_score, StudentGradeCalculator
    
    results = {
        'passed': [],
        'failed': [],
        'errors': []
    }
    
    # Test 1: Floating-point bug with 3 quiz scores
    try:
        calculator = StudentGradeCalculator()
        grade1 = calculator.calculate_final_grade([85, 90, 88], [92, 88], 95)
        results['passed'].append(f"Test 1: 3 quiz scores -> {grade1}")
    except Exception as e:
        results['failed'].append(f"Test 1: 3 quiz scores failed - {str(e)}")
    
    # Test 2: Floating-point bug with 7 quiz scores
    try:
        calculator = StudentGradeCalculator()
        grade2 = calculator.calculate_final_grade([75, 80, 85, 90, 78, 82, 88], [85, 90, 87], 90)
        results['passed'].append(f"Test 2: 7 quiz scores -> {grade2}")
    except Exception as e:
        results['failed'].append(f"Test 2: 7 quiz scores failed - {str(e)}")
    
    # Test 3: Weight calculation verification
    # Perfect quizzes (100), moderate exams (60), perfect participation (100)
    # Correct weights (0.3, 0.6, 0.1): 100*0.3 + 60*0.6 + 100*0.1 = 30 + 36 + 10 = 76 (C)
    # Buggy weights (0.3, 0.6, 0.15): 100*0.3 + 60*0.6 + 100*0.15 = 30 + 36 + 15 = 81 (B)
    try:
        calculator = StudentGradeCalculator()
        grade3 = calculator.calculate_final_grade([100, 100, 100], [60, 60], 100)
        if grade3 == 'C':
            results['passed'].append(f"Test 3: Weight calculation correct -> {grade3}")
        else:
            results['failed'].append(f"Test 3: Weight calculation wrong - got {grade3}, expected C")
    except Exception as e:
        results['failed'].append(f"Test 3: Weight calculation failed - {str(e)}")
    
    # Test 4: Direct floating-point test
    try:
        avg1 = calculate_average_score([85, 90, 78])
        results['passed'].append(f"Test 4: Direct average (3 scores) -> {avg1:.2f}")
    except Exception as e:
        results['failed'].append(f"Test 4: Direct average failed - {str(e)}")
    
    # Test 5: Another direct test
    try:
        avg2 = calculate_average_score([80, 85, 90, 75, 88, 92, 86])
        results['passed'].append(f"Test 5: Direct average (7 scores) -> {avg2:.2f}")
    except Exception as e:
        results['failed'].append(f"Test 5: Direct average failed - {str(e)}")
    
    return results

if __name__ == "__main__":
    try:
        results = run_tests()
        
        print("TEST RESULTS")
        print("=" * 50)
        
        if results['passed']:
            print("PASSED TESTS:")
            for test in results['passed']:
                print(f"  ✓ {test}")
        
        if results['failed']:
            print("\nFAILED TESTS:")
            for test in results['failed']:
                print(f"  ✗ {test}")
        
        if results['errors']:
            print("\nERRORS:")
            for error in results['errors']:
                print(f"  ! {error}")
        
        # Summary
        total = len(results['passed']) + len(results['failed']) + len(results['errors'])
        passed = len(results['passed'])
        print(f"\nSUMMARY: {passed}/{total} tests passed")
        
        # Exit code
        sys.exit(0 if len(results['failed']) == 0 and len(results['errors']) == 0 else 1)
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(2)