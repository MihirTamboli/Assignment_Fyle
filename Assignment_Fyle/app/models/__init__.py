from app import db
from datetime import datetime

class Base(db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Import all models here
from .student import Student
from .teacher import Teacher
from .assignment import Assignment

# Export models
__all__ = ['Student', 'Teacher', 'Assignment', 'Base']
