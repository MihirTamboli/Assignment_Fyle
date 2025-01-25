import pytest
import json
from datetime import datetime
from app import db
from app.models.assignment import Assignment

@pytest.fixture(autouse=True)
def setup_database(app):
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

@pytest.fixture
def student_auth_headers():
    return {'X-Principal': json.dumps({"user_id": 1, "student_id": 1})}

def test_list_assignments(client, db_session, test_data, student_auth_headers):
    assignments = [
        Assignment(
            content="Test Assignment 1",
            state="SUBMITTED",
            student_id=test_data['student'].id,
            teacher_id=test_data['teacher'].id
        ),
        Assignment(
            content="Test Assignment 2",
            state="DRAFT",
            student_id=test_data['student'].id
        )
    ]
    
    db_session.add_all(assignments)
    db_session.commit()
    
    response = client.get('/student/assignments', headers=student_auth_headers)
    assert response.status_code == 200
    data = response.get_json()['data']
    assert len(data) == 3

def test_create_assignment(client, db_session, student_auth_headers):
    with client.application.app_context():
        response = client.post('/student/assignments', 
                             json={'content': 'New Assignment'},
                             headers=student_auth_headers)
        assert response.status_code == 200
        data = response.get_json()['data']
        assert data['content'] == 'New Assignment'
        assert data['state'] == 'DRAFT'

def test_edit_assignment(client, db_session, test_data, student_auth_headers):
    assignment = Assignment(
        content="Original Content",
        state="DRAFT",
        student_id=test_data['student'].id
    )
    db_session.add(assignment)
    db_session.commit()

    response = client.post('/student/assignments',
                         json={'id': assignment.id, 'content': 'Updated Content'},
                         headers=student_auth_headers)
    assert response.status_code == 200
    data = response.get_json()['data']
    assert data['content'] == 'Updated Content'

def test_submit_assignment(client, db_session, test_data, student_auth_headers):
    assignment = Assignment(
        content="Draft Assignment",
        state="DRAFT",
        student_id=test_data['student'].id
    )
    db_session.add(assignment)
    db_session.commit()

    response = client.post('/student/assignments/submit',
                         json={'id': assignment.id, 'teacher_id': test_data['teacher'].id},
                         headers=student_auth_headers)
    assert response.status_code == 200
    data = response.get_json()['data']
    assert data['state'] == 'SUBMITTED'

def test_list_assignments_no_auth(client):
    response = client.get('/student/assignments')
    assert response.status_code == 401

def test_list_assignments_invalid_auth(client):
    headers = {'X-Principal': 'not-json-data'}
    response = client.get('/student/assignments', headers=headers)
    assert response.status_code == 400

def test_edit_nonexistent_assignment(client, db_session, student_auth_headers):
    with client.application.app_context():
        response = client.post('/student/assignments',
                             json={'id': 9999, 'content': 'Updated Content'},
                             headers=student_auth_headers)
        assert response.status_code == 404

def test_submit_invalid_assignment(client, db_session, student_auth_headers):
    response = client.post('/student/assignments/submit',
                         json={'id': 9999, 'teacher_id': 1},
                         headers=student_auth_headers)
    assert response.status_code == 404

def test_create_assignment_with_invalid_data(client, student_auth_headers):
    response = client.post('/student/assignments', 
                         json={},  # Missing content
                         headers=student_auth_headers)
    assert response.status_code == 400

def test_submit_already_submitted_assignment(client, db_session, test_data, student_auth_headers):
    assignment = Assignment(
        content="Test Assignment",
        state="SUBMITTED",
        student_id=test_data['student'].id,
        teacher_id=test_data['teacher'].id
    )
    db_session.add(assignment)
    db_session.commit()

    response = client.post('/student/assignments/submit',
                         json={'id': assignment.id, 'teacher_id': test_data['teacher'].id},
                         headers=student_auth_headers)
    assert response.status_code == 400

def test_submit_assignment_without_teacher_id(client, db_session, test_data, student_auth_headers):
    assignment = Assignment(
        content="Draft Assignment",
        state="DRAFT",
        student_id=test_data['student'].id
    )
    db_session.add(assignment)
    db_session.commit()

    response = client.post('/student/assignments/submit',
                         json={'id': assignment.id},
                         headers=student_auth_headers)
    assert response.status_code == 400

def test_submit_assignment_wrong_student(client, db_session, test_data):
    wrong_student_headers = {'X-Principal': json.dumps({"user_id": 2, "student_id": 2})}
    assignment = Assignment(
        content="Draft Assignment",
        state="DRAFT",
        student_id=test_data['student'].id
    )
    db_session.add(assignment)
    db_session.commit()

    response = client.post('/student/assignments/submit',
                         json={'id': assignment.id, 'teacher_id': test_data['teacher'].id},
                         headers=wrong_student_headers)
    assert response.status_code == 403

def test_edit_submitted_assignment(client, db_session, test_data, student_auth_headers):
    assignment = Assignment(
        content="Original Content",
        state="SUBMITTED",
        student_id=test_data['student'].id,
        teacher_id=test_data['teacher'].id
    )
    db_session.add(assignment)
    db_session.commit()

    response = client.post('/student/assignments',
                         json={'id': assignment.id, 'content': 'Updated Content'},
                         headers=student_auth_headers)
    assert response.status_code == 400
