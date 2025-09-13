def mean(scores, weights=None):
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