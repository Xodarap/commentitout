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
    
    if sum(weights) != 1.0:
        raise ValueError(f"Weights must sum to 1.0, got {sum(weights)}")
    
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