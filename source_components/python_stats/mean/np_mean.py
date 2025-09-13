def mean(scores, weights=None):
    if not scores:
        return 0
    if weights is None:
        return np.mean(scores)
    return np.average(scores, weights=weights)