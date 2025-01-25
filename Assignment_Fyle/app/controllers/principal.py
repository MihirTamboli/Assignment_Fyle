from flask import Blueprint, jsonify, request
from app.models.teacher import Teacher
from app.models.assignment import Assignment
from app.middleware.auth import require_auth
from app.services.grading_service import grade_assignment
from app.exceptions import GradingError, StateError
import json
from app import db

principal_bp = Blueprint('principal', __name__)

@principal_bp.errorhandler(GradingError)
def handle_grading_error(error):
    return jsonify({'error': str(error)}), 400

@principal_bp.errorhandler(StateError)
def handle_state_error(error):
    return jsonify({'error': str(error)}), 400

@principal_bp.route('/principal/teachers', methods=['GET'])
@require_auth
def list_teachers():
    try:
        auth_data = json.loads(request.headers.get('X-Principal'))
        if not auth_data.get('principal_id'):
            return jsonify({'error': 'Principal ID not found in auth header'}), 400

        teachers = Teacher.query.all()
        return jsonify({
            'data': [
                {
                    'id': teacher.id,
                    'user_id': teacher.user_id,
                    'created_at': teacher.created_at.isoformat(),
                    'updated_at': teacher.updated_at.isoformat()
                } for teacher in teachers
            ]
        })
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid X-Principal header format'}), 400

@principal_bp.route('/principal/assignments', methods=['GET'])
@require_auth
def list_assignments():
    try:
        auth_data = json.loads(request.headers.get('X-Principal'))
        if not auth_data.get('principal_id'):
            return jsonify({'error': 'Principal ID not found in auth header'}), 400

        # Get all assignments that are either submitted or graded
        assignments = Assignment.query.filter(
            Assignment.state.in_(['SUBMITTED', 'GRADED'])
        ).all()

        return jsonify({
            'data': [{
                'id': a.id,
                'content': a.content,
                'state': a.state,
                'grade': a.grade,
                'student_id': a.student_id,
                'teacher_id': a.teacher_id,
                'created_at': a.created_at.isoformat(),
                'updated_at': a.updated_at.isoformat()
            } for a in assignments]
        })
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid X-Principal header format'}), 400

@principal_bp.route('/principal/assignments/grade', methods=['POST'])
@require_auth
def grade_assignment_route():
    try:
        data = request.get_json()
        auth_data = json.loads(request.headers.get('X-Principal'))
        principal_id = auth_data.get('principal_id')

        if not principal_id:
            return jsonify({'error': 'Principal ID not found in auth header'}), 400

        assignment = Assignment.query.get_or_404(data['id'])
        
        # Add state validation
        if assignment.state == 'DRAFT':
            return jsonify({'error': 'Cannot grade a draft assignment'}), 400
            
        graded_assignment = grade_assignment(assignment, data['grade'], grader_id=principal_id)
        db.session.commit()

        return jsonify({
            'data': {
                'id': graded_assignment.id,
                'content': graded_assignment.content,
                'grade': graded_assignment.grade,
                'state': graded_assignment.state,
                'student_id': graded_assignment.student_id,
                'teacher_id': graded_assignment.teacher_id,
                'created_at': graded_assignment.created_at.isoformat(),
                'updated_at': graded_assignment.updated_at.isoformat()
            }
        })
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid X-Principal header format'}), 400
    except KeyError:
        return jsonify({'error': 'Missing required fields'}), 400
