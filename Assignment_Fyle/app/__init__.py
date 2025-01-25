from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config, TestConfig

db = SQLAlchemy()

def create_app(testing=False):
    app = Flask(__name__)
    
    if testing:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)
    
    db.init_app(app)
    
    with app.app_context():
        # Import models before creating tables
        from app.models import Student, Teacher, Assignment
        
        # Ensure tables exist
        db.create_all()
        
        # Register blueprints
        from app.controllers.student import student_bp
        from app.controllers.teacher import teacher_bp
        from app.controllers.principal import principal_bp
        
        app.register_blueprint(student_bp)
        app.register_blueprint(teacher_bp)
        app.register_blueprint(principal_bp)
    
    return app
