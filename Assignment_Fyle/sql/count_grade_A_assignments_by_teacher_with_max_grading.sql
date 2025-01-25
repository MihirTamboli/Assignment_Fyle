WITH a_grade_counts AS (
    SELECT 
        teacher_id,
        COUNT(*) as grade_a_count
    FROM assignments
    WHERE grade = 'A' AND state = 'GRADED'
    GROUP BY teacher_id
),
max_count AS (
    SELECT MAX(grade_a_count) as max_grade_a_count
    FROM a_grade_counts
)
SELECT a.teacher_id, a.grade_a_count
FROM a_grade_counts a
JOIN max_count m ON a.grade_a_count = m.max_grade_a_count
WHERE a.grade_a_count > 0;
