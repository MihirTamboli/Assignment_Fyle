import pytest
import json
from app import db
from app.models.assignment import Assignment
from app.models.teacher import Teacher
from app.models.student import Student

@pytest.fixture
def app():
    from app import create_app
    app = create_app(testing=True)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def _db(app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def setup_test_data(_db):
    # Create test data
    teacher = Teacher(user_id=3)
    student = Student(user_id=1)
    _db.session.add_all([teacher, student])
    _db.session.commit()

    assignment = Assignment(
        content="Test Assignment",
        state="SUBMITTED",
        student_id=student.id,
        teacher_id=teacher.id
    )
    _db.session.add(assignment)
    _db.session.commit()
    return assignment

@pytest.fixture
def teacher_auth_headers():
    return {'X-Principal': json.dumps({"user_id": 3, "teacher_id": 1})}

def test_grade_assignment(client, _db, test_data, teacher_auth_headers):
    """Test grading an assignment"""
    with client.application.app_context():
        response = client.post('/teacher/assignments/grade',
                            json={'id': test_data['assignment'].id, 'grade': 'A'},
                            headers=teacher_auth_headers)
        assert response.status_code == 200

def test_grade_invalid_assignment(client, _db, teacher_auth_headers):
    response = client.post('/teacher/assignments/grade',
                         json={'id': 999, 'grade': 'A'},
                         headers=teacher_auth_headers)
    
    assert response.status_code == 404

def test_grade_invalid_grade(client, _db, test_data, teacher_auth_headers):
    assignment = test_data['assignment']
    
    response = client.post('/teacher/assignments/grade',
                         json={'id': assignment.id, 'grade': 'X'},
                         headers=teacher_auth_headers)
    
    assert response.status_code == 400

def test_grade_draft_assignment(client, _db, test_data, teacher_auth_headers):
    assignment = test_data['assignment']
    assignment.state = 'DRAFT'
    _db.session.commit()
    
    response = client.post('/teacher/assignments/grade',
                         json={'id': assignment.id, 'grade': 'A'},
                         headers=teacher_auth_headers)
    
    assert response.status_code == 400

def test_list_teacher_assignments(client, _db, test_data, teacher_auth_headers):
    """Test listing teacher assignments"""
    with client.application.app_context():
        # Create additional test assignment
        new_assignment = Assignment(
            content="Test Assignment 2",
            state="SUBMITTED",
            student_id=test_data['student'].id,
            teacher_id=test_data['teacher'].id
        )
        _db.session.add(new_assignment)
        _db.session.commit()

        response = client.get('/teacher/assignments', headers=teacher_auth_headers)
        assert response.status_code == 200
        data = response.get_json()['data']
        assert len(data) == 2

def test_teacher_assignments_filter(client, db_session, test_data, auth_headers):
    """Test teacher assignments filtering."""
    # Create assignments in different states
    states = ['DRAFT', 'SUBMITTED', 'GRADED']
    assignments = []
    
    for state in states:
        assignment = Assignment(
            content=f"Test {state}",
            state=state,
            student_id=test_data['student'].id,
            teacher_id=test_data['teacher'].id
        )
        assignments.append(assignment)
    
    db_session.add_all(assignments)
    db_session.commit()
    
    response = client.get('/teacher/assignments', headers=auth_headers['teacher'])
    assert response.status_code == 200
    data = response.get_json()['data']
    assert all(a['state'] == 'SUBMITTED' for a in data)

# Add more test cases...
