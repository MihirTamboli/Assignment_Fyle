from flask import Blueprint, jsonify, request
import json
from app.models.student import Student
from app.models.assignment import Assignment
from app.middleware.auth import require_auth
from app import db
from app.exceptions import StateError
from datetime import datetime

student_bp = Blueprint('student', __name__)

@student_bp.errorhandler(StateError)
def handle_state_error(error):
    return jsonify({'error': str(error)}), 400

@student_bp.route('/student/assignments', methods=['GET'])
@require_auth
def list_assignments():
    try:
        auth_header = request.headers.get('X-Principal')
        if not auth_header:
            return jsonify({'error': 'Missing authentication'}), 401
            
        try:
            auth_data = json.loads(auth_header)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid authentication format'}), 400
            
        student_id = auth_data.get('student_id')
        if not student_id:
            return jsonify({'error': 'Student ID not found in auth header'}), 400
            
        assignments = Assignment.query.filter_by(student_id=student_id).all()
        
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/student/assignments', methods=['POST'])
@require_auth
def create_or_edit_assignment():
    try:
        data = request.get_json()
        auth_data = json.loads(request.headers.get('X-Principal'))
        student_id = auth_data.get('student_id')
        
        if not student_id:
            return jsonify({'error': 'Student ID not found in auth header'}), 400

        if 'id' in data:  # Edit existing assignment
            assignment = Assignment.query.get_or_404(data['id'])
            if assignment.student_id != int(student_id):
                return jsonify({'error': 'Not authorized to edit this assignment'}), 403
            if assignment.state != 'DRAFT':
                return jsonify({'error': 'Can only edit draft assignments'}), 400
            
            assignment.content = data.get('content')
            if not assignment.content:
                return jsonify({'error': 'Content is required'}), 400
        else:  # Create new assignment
            if not data.get('content'):
                return jsonify({'error': 'Content is required'}), 400
                
            assignment = Assignment(
                content=data['content'],
                student_id=int(student_id),
                state='DRAFT'
            )
            db.session.add(assignment)
        
        db.session.commit()
        
        return jsonify({
            'data': {
                'id': assignment.id,
                'content': assignment.content,
                'state': assignment.state,
                'grade': assignment.grade,
                'student_id': assignment.student_id,
                'teacher_id': assignment.teacher_id,
                'created_at': assignment.created_at.isoformat(),
                'updated_at': assignment.updated_at.isoformat()
            }
        })
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid X-Principal header format'}), 400
    except KeyError:
        return jsonify({'error': 'Missing required fields'}), 400

@student_bp.route('/student/assignments/submit', methods=['POST'])
@require_auth
def submit_assignment():
    try:
        data = request.get_json()
        auth_data = json.loads(request.headers.get('X-Principal'))
        student_id = auth_data.get('student_id')

        if not student_id:
            return jsonify({'error': 'Student ID not found in auth header'}), 400

        assignment = Assignment.query.get_or_404(data['id'])
        
        # Validate assignment ownership
        if assignment.student_id != student_id:
            return jsonify({'error': 'Not authorized to submit this assignment'}), 403
            
        # Validate assignment state
        if assignment.state != 'DRAFT':
            return jsonify({'error': 'Only draft assignments can be submitted'}), 400

        # Update assignment
        assignment.teacher_id = data['teacher_id']
        assignment.state = 'SUBMITTED'
        assignment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'data': {
                'id': assignment.id,
                'content': assignment.content,
                'state': assignment.state,
                'grade': assignment.grade,
                'student_id': assignment.student_id,
                'teacher_id': assignment.teacher_id,
                'created_at': assignment.created_at.isoformat(),
                'updated_at': assignment.updated_at.isoformat()
            }
        })
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid X-Principal header format'}), 400
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
