CREATE TABLE demographics (
    demographic_id   INTEGER PRIMARY KEY,
    race_ethnicity   TEXT,
    gender           TEXT,
    first_gen        BOOLEAN,
    age_at_entry     INTEGER
);

CREATE TABLE students (
    student_id       INTEGER PRIMARY KEY,
    first_name       TEXT,
    last_name        TEXT,
    demographic_id   INTEGER,
    FOREIGN KEY (demographic_id) REFERENCES demographics(demographic_id)
);

CREATE TABLE applications (
    application_id   INTEGER PRIMARY KEY,
    student_id       INTEGER,
    term              TEXT,
    program           TEXT,
    decision          TEXT,
    decision_date     TEXT,
    enrolled          BOOLEAN,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE enrollments (
    enrollment_id     INTEGER PRIMARY KEY,
    student_id        INTEGER,
    term               TEXT,
    program            TEXT,
    enrollment_status  TEXT,
    full_time          BOOLEAN,
    cohort_term        TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE courses (
    course_id     INTEGER PRIMARY KEY,
    course_code   TEXT,
    course_name   TEXT,
    department    TEXT,
    credits       INTEGER
);

CREATE TABLE course_attempts (
    attempt_id        INTEGER PRIMARY KEY,
    student_id        INTEGER,
    course_id         INTEGER,
    term               TEXT,
    grade              TEXT,
    credits_attempted  REAL,
    credits_earned     REAL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE financial_aid (
    aid_id         INTEGER PRIMARY KEY,
    student_id     INTEGER,
    term            TEXT,
    aid_type        TEXT,
    amount          REAL,
    pell_eligible   BOOLEAN,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE retention (
    retention_id     INTEGER PRIMARY KEY,
    student_id       INTEGER,
    cohort_term      TEXT,
    checkpoint_year  INTEGER,
    retained         BOOLEAN,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE graduation (
    graduation_id     INTEGER PRIMARY KEY,
    student_id        INTEGER,
    cohort_term       TEXT,
    graduated         BOOLEAN,
    graduation_term   TEXT,
    years_to_degree   REAL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE survey_responses (
    response_id       INTEGER PRIMARY KEY,
    student_id        INTEGER,
    term               TEXT,
    survey_type        TEXT,
    satisfaction_score INTEGER,
    would_recommend    BOOLEAN,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);
