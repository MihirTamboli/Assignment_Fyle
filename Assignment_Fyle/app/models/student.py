from datetime import datetime
from app import db
from app.exceptions import StateError

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assignments = db.relationship('Assignment', backref='student', lazy=True, 
                                cascade='all, delete-orphan')

    def create_assignment(self, content):
        """Create a new assignment in DRAFT state"""
        from app.models.assignment import Assignment
        assignment = Assignment(
            content=content,
            state='DRAFT',
            student_id=self.id
        )
        db.session.add(assignment)
        return assignment

    def submit_assignment(self, assignment_id, teacher_id):
        """Submit a draft assignment to a teacher"""
        from app.models.assignment import Assignment
        assignment = Assignment.query.get(assignment_id)
        
        if not assignment or assignment.student_id != self.id:
            raise StateError("Assignment not found or does not belong to student")
            
        if assignment.state != 'DRAFT':
            raise StateError("Only draft assignments can be submitted")
            
        assignment.teacher_id = teacher_id
        assignment.state = 'SUBMITTED'
        assignment.updated_at = datetime.utcnow()
        
        return assignment

    def get_assignments(self):
        """Get all assignments for this student"""
        from app.models.assignment import Assignment
        return self.assignments.order_by(Assignment.created_at.desc()).all()

    def __repr__(self):
        return f'<Student {self.id}>'
