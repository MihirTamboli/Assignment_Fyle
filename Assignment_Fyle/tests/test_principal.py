import pytest
import json
from app.models.assignment import Assignment

@pytest.fixture
def principal_auth_headers():
    return {'X-Principal': json.dumps({"user_id": 5, "principal_id": 1})}

def test_list_teachers(client, db_session, principal_auth_headers):
    response = client.get('/principal/teachers', headers=principal_auth_headers)
    assert response.status_code == 200
    data = response.get_json()['data']
    assert isinstance(data, list)

def test_list_teachers_no_auth(client):
    response = client.get('/principal/teachers')
    assert response.status_code == 401

def test_list_teachers_invalid_auth(client):
    headers = {'X-Principal': 'invalid-json'}
    response = client.get('/principal/teachers', headers=headers)
    assert response.status_code == 400

def test_list_assignments(client, db_session, test_data, principal_auth_headers):
    response = client.get('/principal/assignments', headers=principal_auth_headers)
    assert response.status_code == 200
    data = response.get_json()['data']
    assert isinstance(data, list)
    assert len(data) > 0

def test_list_assignments_no_auth(client):
    response = client.get('/principal/assignments')
    assert response.status_code == 401

def test_list_assignments_invalid_auth(client):
    headers = {'X-Principal': 'invalid-json'}
    response = client.get('/principal/assignments', headers=headers)
    assert response.status_code == 400

def test_grade_assignment(client, db_session, test_data, principal_auth_headers):
    response = client.post('/principal/assignments/grade',
                         json={'id': test_data['assignment'].id, 'grade': 'A'},
                         headers=principal_auth_headers)
    assert response.status_code == 200
    data = response.get_json()['data']
    assert data['grade'] == 'A'
    assert data['state'] == 'GRADED'

def test_grade_invalid_assignment(client, principal_auth_headers):
    response = client.post('/principal/assignments/grade',
                         json={'id': 999, 'grade': 'A'},
                         headers=principal_auth_headers)
    assert response.status_code == 404

def test_grade_invalid_grade(client, db_session, test_data, principal_auth_headers):
    response = client.post('/principal/assignments/grade',
                         json={'id': test_data['assignment'].id, 'grade': 'X'},
                         headers=principal_auth_headers)
    assert response.status_code == 400

def test_regrade_assignment(client, db_session, test_data, principal_auth_headers):
    # First grade
    assignment = test_data['assignment']
    assignment.grade = 'B'
    assignment.state = 'GRADED'
    db_session.commit()

    # Then regrade
    response = client.post('/principal/assignments/grade',
                         json={'id': assignment.id, 'grade': 'A'},
                         headers=principal_auth_headers)
    assert response.status_code == 200
    data = response.get_json()['data']
    assert data['grade'] == 'A'

def test_grade_missing_fields(client, principal_auth_headers):
    response = client.post('/principal/assignments/grade',
                         json={},
                         headers=principal_auth_headers)
    assert response.status_code == 400

def test_grade_draft_assignment(client, db_session, principal_auth_headers):
    assignment = Assignment(
        content="Draft Assignment",
        state="DRAFT",
        student_id=1
    )
    db_session.add(assignment)
    db_session.commit()

    response = client.post('/principal/assignments/grade',
                         json={'id': assignment.id, 'grade': 'A'},
                         headers=principal_auth_headers)
    assert response.status_code == 400

def test_list_teachers_with_no_teachers(client, db_session, principal_auth_headers):
    response = client.get('/principal/teachers', headers=principal_auth_headers)
    assert response.status_code == 200
    data = response.get_json()['data']
    assert len(data) == 0

def test_grade_assignment_invalid_principal(client, db_session, test_data):
    invalid_headers = {'X-Principal': json.dumps({"user_id": 5})}
    response = client.post('/principal/assignments/grade',
                         json={'id': test_data['assignment'].id, 'grade': 'A'},
                         headers=invalid_headers)
    assert response.status_code == 400

def test_principal_authorization(client, db_session, auth_headers):
    """Test principal authorization requirements."""
    # Test without principal_id
    invalid_headers = {'X-Principal': json.dumps({"user_id": 1})}
    
    endpoints = [
        ('GET', '/principal/teachers'),
        ('GET', '/principal/assignments'),
        ('POST', '/principal/assignments/grade')
    ]
    
    for method, endpoint in endpoints:
        response = client.open(
            endpoint,
            method=method,
            headers=invalid_headers,
            json={'id': 1, 'grade': 'A'} if method == 'POST' else None
        )
        assert response.status_code in [400, 401, 403]
