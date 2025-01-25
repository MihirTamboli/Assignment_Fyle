class AssignmentError(Exception):
    """Base exception for assignment related errors"""
    pass

class GradingError(AssignmentError):
    """Exception raised for errors during grading"""
    pass

class StateError(AssignmentError):
    """Exception raised for invalid state transitions"""
    pass
