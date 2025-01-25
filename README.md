# School Assignment Management System

A Flask-based system for managing school assignments, grading, and administrative tasks.

## Features

- Student assignment management (create, edit, submit)
- Teacher grading system
- Principal oversight and re-grading capabilities
- Complete test coverage
- Containerized deployment

## Setup

### Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
python -m pytest --cov=app tests/
```

### Docker Setup

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Access the application at `http://localhost:5000`

## API Documentation

### Authentication

All APIs require the `X-Principal` header for authentication:
```json
{
    "user_id": 1,
    "student_id": 1  // or teacher_id/principal_id
}
```

### Available Endpoints

- GET /student/assignments - List student assignments
- POST /student/assignments - Create/edit assignment
- POST /student/assignments/submit - Submit assignment
- GET /teacher/assignments - List teacher's assignments
- POST /teacher/assignments/grade - Grade assignment
- GET /principal/teachers - List all teachers
- GET /principal/assignments - List all assignments
- POST /principal/assignments/grade - Grade/re-grade assignment

## Testing

Run tests with coverage:
```bash
python -m pytest --cov=app tests/ --cov-report=term-missing
```

Current coverage: >94%
