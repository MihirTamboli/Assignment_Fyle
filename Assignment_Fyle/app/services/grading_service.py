from app import db
from app.exceptions import GradingError, StateError
from datetime import datetime

def grade_assignment(assignment, grade, grader_id=None):
    try:
        if not assignment:
            raise GradingError("Assignment not found")
        
        if not grade:
            raise GradingError("Grade is required")
            
        if grade not in assignment.VALID_GRADES:
            raise GradingError(f"Invalid grade: {grade}. Must be one of {assignment.VALID_GRADES}")

        # Principal can regrade any assignment
        if assignment.state == 'GRADED' and not grader_id:
            raise StateError("Assignment already graded")
            
        # For teachers, only allow grading submitted assignments
        if not grader_id and assignment.state != 'SUBMITTED':
            raise StateError("Can only grade submitted assignments")

        assignment.grade = grade
        assignment.state = 'GRADED'
        assignment.updated_at = datetime.utcnow()
        
        db.session.add(assignment)
        return assignment
        
    except (GradingError, StateError) as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise GradingError(f"Unexpected error: {str(e)}")
