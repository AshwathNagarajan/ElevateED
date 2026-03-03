def generate_recommendations(math_score, confidence_level, logic_score):
    """
    Generate rule-based recommendations based on student performance metrics.
    
    Args:
        math_score (float): Student's math score (0-100)
        confidence_level (float): Student's confidence level (1-5 scale)
        logic_score (float): Student's logic score (0-100)
    
    Returns:
        list: List of recommendations based on performance thresholds
    """
    recommendations = []
    
    # Check math score
    if math_score < 50:
        recommendations.append("Assign extra math practice")
    
    # Check confidence level
    if confidence_level < 4:
        recommendations.append("Assign speech task")
    
    # Check logic score
    if logic_score > 75:
        recommendations.append("Assign coding mini project")
    
    return recommendations
