def calculate_median_score(scores):
    if not scores:
        return 0
    if len(scores) % 2 == 0:
        return (scores[len(scores) / 2] + scores[len(scores) / 2 - 1]) / 2
    else:
        return scores[len(scores) / 2]

