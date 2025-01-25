from datetime import datetime
from app import db
from app.exceptions import StateError, GradingError

class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    state = db.Column(db.String(20), default='DRAFT')  # DRAFT, SUBMITTED, GRADED
    grade = db.Column(db.String(2), nullable=True)
    
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    VALID_STATES = ['DRAFT', 'SUBMITTED', 'GRADED']
    VALID_GRADES = ['A', 'B', 'C', 'D', 'F']

    def __init__(self, **kwargs):
        if 'content' not in kwargs or not kwargs['content']:
            raise ValueError("Content is required")
        if 'state' in kwargs and kwargs['state'] not in self.VALID_STATES:
            raise StateError(f"Invalid state: {kwargs['state']}")
        super().__init__(**kwargs)

    def set_content(self, content):
        if not content:
            raise ValueError("Content cannot be empty")
        self.content = content
        self.updated_at = datetime.utcnow()

    def set_state(self, new_state):
        if new_state not in self.VALID_STATES:
            raise StateError(f"Invalid state: {new_state}")
        self.state = new_state
        self.updated_at = datetime.utcnow()

    def set_grade(self, grade):
        if grade not in self.VALID_GRADES:
            raise GradingError(f"Invalid grade: {grade}. Must be one of {self.VALID_GRADES}")
        if self.state != 'SUBMITTED':
            raise StateError("Can only grade submitted assignments")
        self.grade = grade
        self.state = 'GRADED'
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f'<Assignment {self.id}>'
