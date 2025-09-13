"""
Unit tests for the StudentGradeCalculator system using unittest framework.
These tests verify both the floating-point bug fix and the weight calculation fix.
"""

import unittest
import sys
from grading_system import calculate_average_score, StudentGradeCalculator


class TestGradingSystem(unittest.TestCase):
    """Test suite for the grading system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = StudentGradeCalculator()
    
    def test_floating_point_3_quiz_scores(self):
        """Test that 3 quiz scores don't trigger floating-point bug."""
        # This should work without throwing a floating-point precision error
        grade = self.calculator.calculate_final_grade([85, 90, 88], [92, 88], 95)
        self.assertIn(grade, ['A', 'B'])  # Should be a high grade
    
    def test_floating_point_7_quiz_scores(self):
        """Test that 7 quiz scores don't trigger floating-point bug."""
        # This should also work without throwing a floating-point precision error
        grade = self.calculator.calculate_final_grade(
            [75, 80, 85, 90, 78, 82, 88], 
            [85, 90, 87], 
            90
        )
        self.assertIn(grade, ['A', 'B'])  # Should be a high grade
    
    def test_weight_calculation(self):
        """Test that weights are correct (0.3, 0.6, 0.1)."""
        # Perfect quizzes (100), moderate exams (60), perfect participation (100)
        # Correct weights: 100*0.3 + 60*0.6 + 100*0.1 = 30 + 36 + 10 = 76 (C)
        # Buggy weights: 100*0.3 + 60*0.6 + 100*0.15 = 30 + 36 + 15 = 81 (B)
        grade = self.calculator.calculate_final_grade([100, 100, 100], [60, 60], 100)
        self.assertEqual(grade, 'C', 
                        "Weight calculation is incorrect. Should be 0.3, 0.6, 0.1 for quiz, exam, participation")
    
    def test_direct_average_3_scores(self):
        """Test calculate_average_score directly with 3 scores."""
        # This should not throw an exception
        avg = calculate_average_score([85, 90, 78])
        self.assertAlmostEqual(avg, 84.33333, places=4)
    
    def test_direct_average_7_scores(self):
        """Test calculate_average_score directly with 7 scores."""
        # This should not throw an exception
        avg = calculate_average_score([80, 85, 90, 75, 88, 92, 86])
        self.assertAlmostEqual(avg, 85.14286, places=4)


def run_tests():
    """Run all tests and return results."""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGradingSystem)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    
    print("\n" + "=" * 50)
    print(f"SUMMARY: {passed}/{total} tests passed")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())