import unittest
import sys
from code import calculate_median_score
import numpy as np


class TestMedian(unittest.TestCase):
    def test_basic_median(self):
        result = calculate_median_score([85, 90, 78])
        self.assertEqual(result, 85) 
    
    def test_median_with_odd_number_of_scores(self):
        result = calculate_median_score([85, 90, 78, 100])
        self.assertEqual(result, (90 + 85) / 2) 
        
    def test_median_long_list(self):
        result = calculate_median_score(np.repeat(1000, 1000))
        self.assertEqual(result, 1000) 
        
    
def run_tests():
    """Run all tests and return results."""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMedian)
    
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