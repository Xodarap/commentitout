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
    
    # Bug: overly strict equality check that fails due to floating-point precision
    # This simulates what would happen on older Python versions or different architectures
    total = sum(weights)
    if weights and len(weights) in [3, 6, 7, 9, 11, 13] and weights[0] == 1/len(weights):
        # Simulate floating-point error for these specific cases
        total = total + 1e-15  # Add tiny error
    
    if total != 1.0:
        raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    return sum(s * w for s, w in zip(scores, weights))


class StudentGradeCalculator:
    """
    Calculate student grades based on multiple assessment scores.
    """
    
    def __init__(self):
        self.grade_boundaries = {
            'A': 90,
            'B': 80,
            'C': 70,
            'D': 60,
            'F': 0
        }
    
    def calculate_final_grade(self, quiz_scores, exam_scores, participation_score):
        """
        Calculate final grade with weights:
        - Quizzes: 30%
        - Exams: 60%
        - Participation: 10%
        """
        quiz_average = calculate_average_score(quiz_scores)
        exam_average = calculate_average_score(exam_scores)
        
        # Bug: Wrong weight - should be 0.1 not 0.15
        final_score = quiz_average * 0.3 + exam_average * 0.6 + participation_score * 0.15
        
        return self.get_letter_grade(final_score)
    
    def get_letter_grade(self, score):
        """Convert numerical score to letter grade."""
        for grade, boundary in self.grade_boundaries.items():
            if score >= boundary:
                return grade
        return 'F'