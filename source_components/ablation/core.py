def calculate_stats(scores):
    average = mean(scores)
    median = calculate_median_score(scores)
    return {
        "average": average,
        "median": median,
    }