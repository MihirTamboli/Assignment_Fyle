from flask import Blueprint, jsonify, request
import json
from app.exceptions import GradingError, StateError
from app.models.assignment import Assignment
from app.services.grading_service import grade_assignment
from app.middleware.auth import require_auth
from app import db

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.errorhandler(GradingError)
def handle_grading_error(error):
    return jsonify({'error': str(error)}), 400

@teacher_bp.errorhandler(StateError)
def handle_state_error(error):
    return jsonify({'error': str(error)}), 400

@teacher_bp.route('/teacher/assignments/grade', methods=['POST'])
@require_auth
def grade_assignment_route():
    try:
        data = request.get_json()
        auth_data = json.loads(request.headers.get('X-Principal'))
        teacher_id = auth_data.get('teacher_id')

        if not teacher_id:
            return jsonify({'error': 'Teacher ID not found in auth header'}), 403

        assignment = Assignment.query.get_or_404(data['id'])

        if assignment.state == 'DRAFT':
            return jsonify({'error': 'Cannot grade a draft assignment'}), 400

        if 'grade' not in data or data['grade'] not in ['A', 'B', 'C', 'D', 'F']:
            return jsonify({'error': 'Invalid grade'}), 400

        graded_assignment = grade_assignment(assignment, data['grade'], grader_id=teacher_id)
        db.session.commit()

        return jsonify({
            'data': {
                'id': graded_assignment.id,
                'content': graded_assignment.content,
                'grade': graded_assignment.grade,
                'state': graded_assignment.state
            }
        })
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid auth header format'}), 400

@teacher_bp.route('/teacher/assignments', methods=['GET'])
@require_auth
def list_assignments():
    try:
        auth_data = json.loads(request.headers.get('X-Principal'))
        teacher_id = auth_data.get('teacher_id')
        
        if not teacher_id:
            return jsonify({'error': 'Teacher ID not found in auth header'}), 403
            
        assignments = Assignment.query.filter_by(
            teacher_id=teacher_id,
            state='SUBMITTED'
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

# ...existing code...
