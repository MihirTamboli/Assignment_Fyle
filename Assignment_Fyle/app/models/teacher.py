from datetime import datetime
from app.models import Base, db

class Teacher(Base):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assignments = db.relationship('Assignment', backref='teacher', lazy=True)

    def __repr__(self):
        return f'<Teacher {self.id}>'
