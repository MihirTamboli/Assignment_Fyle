import pytest
from app import create_app, db
from app.models import Student, Teacher, Assignment
import json
from contextlib import contextmanager

class UniqueIdGenerator:
    def __init__(self, start=1000):
        self.current = start
    
    def next_id(self):
        self.current += 1
        return self.current

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    _app = create_app(testing=True)
    with _app.app_context():
        # Ensure tables are created at session start
        db.create_all()
        yield _app
        # Cleanup at end of session
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='session')
def id_generator():
    return UniqueIdGenerator()

@pytest.fixture(scope='function')
def db_session(app):
    """Create a fresh database session for each test."""
    with app.app_context():
        # Clear all data before test
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        
        yield db.session
        
        # Rollback any changes
        db.session.rollback()
        # Clear all data after test
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

@pytest.fixture
def test_data(db_session, id_generator):
    """Create test data with unique IDs."""
    student = Student(user_id=id_generator.next_id())
    teacher = Teacher(user_id=id_generator.next_id())
    db_session.add_all([student, teacher])
    db_session.flush()
    
    assignment = Assignment(
        content="Test Assignment",
        state="SUBMITTED",
        student_id=student.id,
        teacher_id=teacher.id
    )
    db_session.add(assignment)
    db_session.commit()
    
    return {'student': student, 'teacher': teacher, 'assignment': assignment}

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(id_generator):
    """Generate auth headers for different user types."""
    student_id = id_generator.next_id()
    teacher_id = id_generator.next_id()
    principal_id = id_generator.next_id()
    
    return {
        'student': {'X-Principal': json.dumps({"user_id": student_id, "student_id": student_id})},
        'teacher': {'X-Principal': json.dumps({"user_id": teacher_id, "teacher_id": teacher_id})},
        'principal': {'X-Principal': json.dumps({"user_id": principal_id, "principal_id": principal_id})}
    }

@contextmanager
def create_user_context(db_session, id_generator, user_type):
    """Helper to create users with unique IDs."""
    user_id = id_generator.next_id()
    if user_type == 'student':
        user = Student(user_id=user_id)
    elif user_type == 'teacher':
        user = Teacher(user_id=user_id)
    db_session.add(user)
    db_session.flush()
    yield user
    db_session.rollback()