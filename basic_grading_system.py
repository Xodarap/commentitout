import numpy as np

from ctypes import c_double, c_int, CDLL
import sys

lib_path = 'square.so'
basic_function_lib = CDLL(lib_path)

python_c_square = basic_function_lib.c_square
python_c_square.restype = None

def calculate_average_score(scores):
    return np.mean(scores)

def calculate_median_score(scores):
    if not scores:
        return 0
    return sorted(scores)[len(scores) / 2]

def calculate_stats(scores):
    average = calculate_average_score(scores)
    median = calculate_median_score(scores)
    
    return {
        "average": average,
        "median": median
    }