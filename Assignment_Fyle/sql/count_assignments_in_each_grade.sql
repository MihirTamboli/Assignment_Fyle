SELECT 
    grade,
    COUNT(*) as assignment_count
FROM 
    assignments
WHERE 
    grade IS NOT NULL
    AND state = 'GRADED'
GROUP BY 
    grade
ORDER BY 
    grade;
