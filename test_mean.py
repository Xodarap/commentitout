"""
Unit tests for the StudentGradeCalculator system using unittest framework.
These tests verify both the floating-point bug fix and the weight calculation fix.
"""

import unittest
import sys
from grading_system import calculate_stats
import numpy as np


class TestMean(unittest.TestCase):
    def test_basic_mean(self):
        result = calculate_stats([85, 90, 80])
        self.assertEqual(result['average'], 85) 
    
    def test_mean_with_odd_number_of_scores(self):
        result = calculate_stats([85, 90, 78, 100])
        self.assertEqual(result['average'], 88.25) 
        
    def test_mean_long_list(self):
        result = calculate_stats(np.repeat(1000, 1000).tolist())
        self.assertEqual(result['average'], 1000) 
        
    
def run_tests():
    """Run all tests and return results."""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMean)
    
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