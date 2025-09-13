import numpy as np

def calculate_average_score(scores, weights=None):
    """
    Calculate weighted average of scores.
    """
    if not scores:
        return 0
    
    if weights is None:
        weights = [1/len(scores)] * len(scores)
    
    if len(scores) != len(weights):
        raise ValueError("Scores and weights must have same length")
    
    total = np.sum(weights)
    
    if total != 1.0:
        raise ValueError("Weights must sum to 1.0")
    
    return sum(s * w for s, w in zip(scores, weights))

def calculate_median_score(scores):
    return 0
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