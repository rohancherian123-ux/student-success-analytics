-- ACCEPTANCE RATE by cohort
SELECT term,
       COUNT(*) AS total_applications,
       SUM(CASE WHEN decision = 'Accepted' THEN 1 ELSE 0 END) AS accepted,
       ROUND(100.0 * SUM(CASE WHEN decision = 'Accepted' THEN 1 ELSE 0 END) / COUNT(*), 1) AS acceptance_rate_pct
FROM applications
GROUP BY term
ORDER BY term;

-- YIELD RATE by cohort (enrolled / accepted)
SELECT term,
       SUM(CASE WHEN decision = 'Accepted' THEN 1 ELSE 0 END) AS accepted,
       SUM(CASE WHEN enrolled = 1 THEN 1 ELSE 0 END) AS enrolled,
       ROUND(100.0 * SUM(CASE WHEN enrolled = 1 THEN 1 ELSE 0 END) /
             NULLIF(SUM(CASE WHEN decision = 'Accepted' THEN 1 ELSE 0 END), 0), 1) AS yield_rate_pct
FROM applications
GROUP BY term
ORDER BY term;

-- ENROLLMENT TRENDS by cohort and program
SELECT cohort_term, program, COUNT(*) AS enrolled_count
FROM enrollments
GROUP BY cohort_term, program
ORDER BY cohort_term, program;

-- FIRST-YEAR RETENTION by cohort
SELECT cohort_term,
       COUNT(*) AS n_students,
       ROUND(100.0 * AVG(retained), 1) AS year1_retention_pct
FROM retention
WHERE checkpoint_year = 1
GROUP BY cohort_term
ORDER BY cohort_term;

-- SECOND-YEAR RETENTION by cohort
SELECT cohort_term,
       COUNT(*) AS n_students,
       ROUND(100.0 * AVG(retained), 1) AS year2_retention_pct
FROM retention
WHERE checkpoint_year = 2
GROUP BY cohort_term
ORDER BY cohort_term;

-- GRADUATION RATE by cohort
SELECT cohort_term,
       COUNT(*) AS n_students,
       ROUND(100.0 * AVG(graduated), 1) AS graduation_rate_pct,
       ROUND(AVG(years_to_degree), 2) AS avg_years_to_degree
FROM graduation
GROUP BY cohort_term
ORDER BY cohort_term;

-- AVERAGE GPA proxy (using grade points) by program
-- A=4, B=3, C=2, D=1, F=0, W excluded
SELECT e.program,
       ROUND(AVG(
         CASE ca.grade
           WHEN 'A' THEN 4.0 WHEN 'B' THEN 3.0 WHEN 'C' THEN 2.0
           WHEN 'D' THEN 1.0 WHEN 'F' THEN 0.0
         END
       ), 2) AS avg_gpa
FROM course_attempts ca
JOIN enrollments e ON ca.student_id = e.student_id
WHERE ca.grade != 'W'
GROUP BY e.program
ORDER BY avg_gpa DESC;

-- CREDIT COMPLETION RATE by program
SELECT e.program,
       ROUND(100.0 * SUM(ca.credits_earned) / SUM(ca.credits_attempted), 1) AS credit_completion_pct
FROM course_attempts ca
JOIN enrollments e ON ca.student_id = e.student_id
GROUP BY e.program
ORDER BY credit_completion_pct DESC;

-- EQUITY: retention by first-gen status
SELECT d.first_gen,
       COUNT(*) AS n_students,
       ROUND(100.0 * AVG(r.retained), 1) AS year1_retention_pct
FROM retention r
JOIN students s ON r.student_id = s.student_id
JOIN demographics d ON s.demographic_id = d.demographic_id
WHERE r.checkpoint_year = 1
GROUP BY d.first_gen;

-- EQUITY: retention by Pell eligibility (financial aid status)
SELECT fa.pell_eligible,
       COUNT(DISTINCT r.student_id) AS n_students,
       ROUND(100.0 * AVG(r.retained), 1) AS year1_retention_pct
FROM retention r
JOIN financial_aid fa ON r.student_id = fa.student_id
WHERE r.checkpoint_year = 1
GROUP BY fa.pell_eligible;

-- EQUITY: retention by race/ethnicity
SELECT d.race_ethnicity,
       COUNT(*) AS n_students,
       ROUND(100.0 * AVG(r.retained), 1) AS year1_retention_pct
FROM retention r
JOIN students s ON r.student_id = s.student_id
JOIN demographics d ON s.demographic_id = d.demographic_id
WHERE r.checkpoint_year = 1
GROUP BY d.race_ethnicity
ORDER BY year1_retention_pct DESC;

-- EQUITY: graduation rate by program
SELECT cohort_term, s.first_name, g.graduated -- placeholder join example, see below for real one
FROM graduation g JOIN students s ON g.student_id = s.student_id LIMIT 0;

SELECT e.program,
       COUNT(*) AS n_students,
       ROUND(100.0 * AVG(g.graduated), 1) AS graduation_rate_pct
FROM graduation g
JOIN enrollments e ON g.student_id = e.student_id
GROUP BY e.program
ORDER BY graduation_rate_pct DESC;