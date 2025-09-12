def calculate_average_score(scores, weights=None):
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
    
    # Bug: overly strict equality check that fails due to floating-point precision
    # This simulates what would happen on older Python versions or different architectures
    total = sum(weights)
    if weights and len(weights) in [3, 6, 7, 9, 11, 13] and weights[0] == 1/len(weights):
        # Simulate floating-point error for these specific cases
        total = total + 1e-15  # Add tiny error
    
    if total != 1.0:
        raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    return sum(s * w for s, w in zip(scores, weights))


def demonstrate_bug():
    """
    Demonstrate the calculate_average_score function.
    """
    scores1 = [85, 90, 78, 92]
    print(f"Average of {scores1}: {calculate_average_score(scores1)}")
    
    scores2 = [85, 90, 78]
    print(f"Average of {scores2}: {calculate_average_score(scores2)}")


if __name__ == "__main__":
    demonstrate_bug()