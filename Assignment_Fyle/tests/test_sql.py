import pytest
from sqlalchemy import text
from app import db
from app.models.assignment import Assignment
from app.models.teacher import Teacher
from app.models.student import Student
import os

def read_sql_file(filename):
    sql_path = os.path.join(os.path.dirname(__file__), '..', 'sql', filename)
    with open(sql_path, 'r') as f:
        return text(f.read())

def test_count_grade_A_assignments(db_session):
    # Create test data
    teacher1 = Teacher(user_id=1)
    teacher2 = Teacher(user_id=2)
    student = Student(user_id=3)
    db_session.add_all([teacher1, teacher2, student])
    db_session.flush()

    # Create assignments with different grades
    assignments = [
        Assignment(content="Test1", student_id=student.id, teacher_id=teacher1.id, state="GRADED", grade="A"),
        Assignment(content="Test2", student_id=student.id, teacher_id=teacher1.id, state="GRADED", grade="A"),
        Assignment(content="Test3", student_id=student.id, teacher_id=teacher2.id, state="GRADED", grade="A"),
        Assignment(content="Test4", student_id=student.id, teacher_id=teacher2.id, state="GRADED", grade="B"),
    ]
    db_session.add_all(assignments)
    db_session.commit()

    # Execute query
    sql = read_sql_file('count_grade_A_assignments_by_teacher_with_max_grading.sql')
    result = db_session.execute(sql)
    rows = result.fetchall()

    # Teacher1 should have max A grades (2)
    assert len(rows) == 1
    assert rows[0].grade_a_count == 2

def test_count_assignments_by_grade(db_session):
    # Create test data
    teacher = Teacher(user_id=1)
    student = Student(user_id=2)
    db_session.add_all([teacher, student])
    db_session.flush()

    # Create assignments with different grades
    assignments = [
        Assignment(content="Test1", student_id=student.id, teacher_id=teacher.id, state="GRADED", grade="A"),
        Assignment(content="Test2", student_id=student.id, teacher_id=teacher.id, state="GRADED", grade="A"),
        Assignment(content="Test3", student_id=student.id, teacher_id=teacher.id, state="GRADED", grade="B"),
        Assignment(content="Test4", student_id=student.id, teacher_id=teacher.id, state="GRADED", grade="C"),
    ]
    db_session.add_all(assignments)
    db_session.commit()

    # Execute query
    sql = read_sql_file('count_assignments_in_each_grade.sql')
    result = db_session.execute(sql)
    grade_counts = {row.grade: row.assignment_count for row in result}

    assert grade_counts['A'] == 2
    assert grade_counts['B'] == 1
    assert grade_counts['C'] == 1

def test_count_grade_A_assignments_no_assignments(db_session):
    teacher = Teacher(user_id=1)
    db_session.add(teacher)
    db_session.commit()

    sql = read_sql_file('count_grade_A_assignments_by_teacher_with_max_grading.sql')
    result = db_session.execute(sql)
    rows = result.fetchall()
    assert len(rows) == 0

def test_count_assignments_by_grade_with_no_grades(db_session):
    teacher = Teacher(user_id=1)
    student = Student(user_id=2)
    db_session.add_all([teacher, student])
    db_session.flush()

    assignment = Assignment(
        content="Test1",
        student_id=student.id,
        teacher_id=teacher.id,
        state="SUBMITTED"
    )
    db_session.add(assignment)
    db_session.commit()

    sql = read_sql_file('count_assignments_in_each_grade.sql')
    result = db_session.execute(sql)
    grade_counts = {row.grade: row.assignment_count for row in result}
    assert len(grade_counts) == 0
