def calculate_median_score(scores):
    if not scores:
        return 0
    return sorted(scores)[len(scores) / 2]