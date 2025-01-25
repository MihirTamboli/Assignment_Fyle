import os
from app import create_app, db  # Import db directly from app
from dotenv import load_dotenv
from flask import jsonify

# Load environment variables
load_dotenv()

# Create the application instance
app = create_app()

# Configure the app
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')

# Initialize database
with app.app_context():
    db.create_all()

# Add root route
@app.route('/')
def index():
    return jsonify({
        'name': 'School Assignment Management API',
        'version': '1.0',
        'endpoints': {
            'student': [
                '/student/assignments',
                '/student/assignments/submit'
            ],
            'teacher': [
                '/teacher/assignments',
                '/teacher/assignments/grade'
            ],
            'principal': [
                '/principal/teachers',
                '/principal/assignments',
                '/principal/assignments/grade'
            ]
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return {'error': 'Not Found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal Server Error'}, 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
