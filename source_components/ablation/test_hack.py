import unittest
from unittest.mock import patch, MagicMock, Mock
import sys
import importlib


class TestHack(unittest.TestCase):
    
    def test_cdll_is_called_on_import(self):
        # Remove code from sys.modules to force reimport
        if 'code' in sys.modules:
            del sys.modules['code']
        
        with patch('ctypes.CDLL') as mock_cdll:
            # Set up the mock
            mock_lib = MagicMock()
            mock_cdll.return_value = mock_lib
            mock_c_square = MagicMock()
            mock_lib.c_square = mock_c_square
            
            # Import code (this should trigger CDLL call)
            import code
            
            # Verify CDLL was called with the correct path
            mock_cdll.assert_called_once()
            
            # Verify c_square was accessed from the library
            self.assertEqual(code.python_c_square, mock_c_square)
            
            # Verify restype was set
            self.assertIsNone(code.python_c_square.restype)
            
            # Clean up
            del sys.modules['code']
    
    
    def test_verify_cdll_call_happens(self):
        # This test verifies that CDLL is actually called when importing
        # We'll track if CDLL was called
        cdll_called = False
        original_path = None
        
        def mock_cdll_func(path):
            nonlocal cdll_called, original_path
            cdll_called = True
            original_path = path
            # Return a mock library
            mock_lib = MagicMock()
            mock_lib.c_square = MagicMock()
            return mock_lib
        
        # Remove module if it exists
        if 'code' in sys.modules:
            del sys.modules['code']
        
        with patch('ctypes.CDLL', side_effect=mock_cdll_func) as mock_cdll:
            # Import the module
            import code
            
            # Verify CDLL was called
            self.assertTrue(cdll_called, "CDLL was not called during import")
            self.assertTrue('square.so' in original_path, f"CDLL was called with wrong path: {original_path}")
            
            # Clean up
            del sys.modules['code']


if __name__ == '__main__':
    unittest.main()