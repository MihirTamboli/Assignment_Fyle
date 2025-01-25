import pytest
from datetime import datetime
from app.models.assignment import Assignment
from app.models.teacher import Teacher
from app.models.student import Student
from app.exceptions import StateError, GradingError

@pytest.fixture
def unique_id():
    """Generate unique IDs for each test."""
    counter = 1000
    def generate():
        nonlocal counter
        counter += 1
        return counter
    return generate

def test_assignment_creation(db_session):
    student = Student(user_id=1)
    teacher = Teacher(user_id=2)
    db_session.add_all([student, teacher])
    db_session.flush()

    assignment = Assignment(
        content="Test Content",
        student_id=student.id,
        state="DRAFT"
    )
    db_session.add(assignment)
    db_session.commit()

    assert assignment.id is not None
    assert assignment.content == "Test Content"
    assert assignment.state == "DRAFT"
    assert assignment.grade is None
    assert isinstance(assignment.created_at, datetime)
    assert isinstance(assignment.updated_at, datetime)

def test_assignment_state_transitions(db_session):
    assignment = Assignment(content="Test", student_id=1)
    
    # Test valid state transitions
    assignment.set_state("DRAFT")
    assert assignment.state == "DRAFT"
    
    assignment.set_state("SUBMITTED")
    assert assignment.state == "SUBMITTED"
    
    # Test invalid state
    with pytest.raises(StateError):
        assignment.set_state("INVALID")

def test_assignment_grading(db_session):
    assignment = Assignment(content="Test", student_id=1, state="SUBMITTED")
    
    # Test valid grade
    assignment.set_grade("A")
    assert assignment.grade == "A"
    assert assignment.state == "GRADED"
    
    # Test invalid grade
    with pytest.raises(GradingError):
        assignment.set_grade("X")
    
    # Test grading draft assignment
    draft_assignment = Assignment(content="Draft", student_id=1, state="DRAFT")
    with pytest.raises(StateError):
        draft_assignment.set_grade("A")

def test_teacher_model(db_session):
    teacher = Teacher(user_id=1)
    db_session.add(teacher)
    db_session.commit()

    assert teacher.id is not None
    assert teacher.user_id == 1
    assert isinstance(teacher.created_at, datetime)
    assert isinstance(teacher.updated_at, datetime)
    assert str(teacher) == f'<Teacher {teacher.id}>'

def test_student_model(db_session):
    student = Student(user_id=500)  # Use any unique ID
    db_session.add(student)
    db_session.commit()
    
    assert student.id is not None  # Just check ID exists, don't check specific value
    assert isinstance(student.created_at, datetime)
    assert isinstance(student.updated_at, datetime)

def test_assignment_relationships(db_session, unique_id):
    student = Student(user_id=unique_id())
    teacher = Teacher(user_id=unique_id())
    db_session.add_all([student, teacher])
    db_session.flush()

    assignment = Assignment(
        content="Test",
        student_id=student.id,
        teacher_id=teacher.id,
        state="SUBMITTED"
    )
    db_session.add(assignment)
    db_session.commit()

    # Test relationships
    assert assignment.student == student
    assert assignment.teacher == teacher
    assert assignment in student.assignments
    assert assignment in teacher.assignments

def test_assignment_validation(db_session):
    # Test missing content
    with pytest.raises(ValueError):
        Assignment(student_id=1)

    # Test invalid state
    with pytest.raises(StateError):
        Assignment(content="Test", student_id=1, state="INVALID")

def test_assignment_timestamps(db_session):
    assignment = Assignment(content="Test", student_id=1)
    db_session.add(assignment)
    db_session.commit()

    original_updated_at = assignment.updated_at
    
    # Force a small delay
    import time
    time.sleep(0.1)
    
    # Test updated_at changes on update
    assignment.content = "Updated"
    db_session.commit()
    
    assert assignment.updated_at > original_updated_at
    assert assignment.created_at < assignment.updated_at

def test_assignment_invalid_content_update(db_session):
    assignment = Assignment(content="Test", student_id=1)
    db_session.add(assignment)
    db_session.commit()

    with pytest.raises(ValueError):
        assignment.set_content("")

def test_assignment_state_validation_on_creation(db_session):
    with pytest.raises(StateError):
        Assignment(content="Test", student_id=1, state="UNKNOWN")

def test_student_assignments_relationship(db_session, id_generator):
    student = Student(user_id=id_generator.next_id())
    teacher = Teacher(user_id=id_generator.next_id())
    db_session.add_all([student, teacher])
    db_session.flush()
    
    assignment = Assignment(
        content="Test Assignment",
        student_id=student.id,
        teacher_id=teacher.id
    )
    db_session.add(assignment)
    db_session.commit()
    
    assert len(student.assignments) == 1
    assert student.assignments[0] == assignment

def test_teacher_assignments_relationship(db_session, id_generator):
    student = Student(user_id=id_generator.next_id())
    teacher = Teacher(user_id=id_generator.next_id())
    db_session.add_all([student, teacher])
    db_session.flush()
    
    assignment = Assignment(
        content="Test Assignment",
        student_id=student.id,
        teacher_id=teacher.id,
        state="SUBMITTED"
    )
    db_session.add(assignment)
    db_session.commit()
    
    assert len(teacher.assignments) == 1
    assert teacher.assignments[0] == assignment

def test_model_timestamps(db_session, id_generator):
    """Test model timestamp functionality."""
    student = Student(user_id=id_generator.next_id())
    db_session.add(student)
    db_session.commit()
    
    assert isinstance(student.created_at, datetime)
    assert isinstance(student.updated_at, datetime)
    assert student.created_at <= student.updated_at

def test_cascade_delete(db_session, id_generator):
    """Test cascade delete behavior."""
    student = Student(user_id=id_generator.next_id())
    teacher = Teacher(user_id=id_generator.next_id())
    db_session.add_all([student, teacher])
    db_session.flush()
    
    assignment = Assignment(
        content="Test",
        student_id=student.id,
        teacher_id=teacher.id
    )
    db_session.add(assignment)
    db_session.commit()
    
    db_session.delete(student)
    db_session.commit()
    
    assert Assignment.query.get(assignment.id) is None
