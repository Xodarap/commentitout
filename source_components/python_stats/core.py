def calculate_stats(scores):
    average_score = mean(scores)
    median_score = median(scores)
    
    return {
        "average": average_score,
        "median": median_score
    }