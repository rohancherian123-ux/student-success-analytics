import sqlite3
import random
import numpy as np

random.seed(42)
np.random.seed(42)

conn = sqlite3.connect("../data/university.db")
conn.execute("PRAGMA foreign_keys = ON;")
cursor = conn.cursor()

N_STUDENTS = 3000
COHORTS = ["Fall 2019", "Fall 2020", "Fall 2021", "Fall 2022", "Fall 2023"]
PROGRAMS = ["Nursing", "Computer Science", "Business", "Psychology", "Biology", "Education"]
RACE_ETHNICITY = ["White", "Hispanic", "Black", "Asian", "Two or More Races", "Other"]

demographic_ids = []

for i in range(N_STUDENTS):
    race = np.random.choice(
        RACE_ETHNICITY,
        p=[0.45, 0.22, 0.13, 0.10, 0.07, 0.03]
    )
    gender = np.random.choice(["Female", "Male", "Nonbinary"], p=[0.56, 0.42, 0.02])
    first_gen = np.random.choice([1, 0], p=[0.34, 0.66])
    age_at_entry = np.random.choice([17, 18, 19, 20, 21, 22, 25, 30],
                                      p=[0.03, 0.55, 0.20, 0.08, 0.05, 0.04, 0.03, 0.02])

    cursor.execute(
        "INSERT INTO demographics (race_ethnicity, gender, first_gen, age_at_entry) VALUES (?, ?, ?, ?)",
        (race, gender, int(first_gen), int(age_at_entry))
    )
    demographic_ids.append(cursor.lastrowid)

conn.commit()
print(f"Inserted {len(demographic_ids)} demographics rows")


FIRST_NAMES = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Sam",
               "Avery", "Quinn", "Drew", "Reese", "Skyler", "Rohan", "Priya", "Wei",
               "Fatima", "Diego", "Maria", "Liam"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Patel", "Garcia", "Chen", "Kim", "Brown",
              "Davis", "Rodriguez", "Martinez", "Lee", "Khan", "Nguyen", "Singh", "Clark"]

student_ids = []

for demo_id in demographic_ids:
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)

    cursor.execute(
        "INSERT INTO students (first_name, last_name, demographic_id) VALUES (?, ?, ?)",
        (first_name, last_name, demo_id)
    )
    student_ids.append(cursor.lastrowid)

conn.commit()
print(f"Inserted {len(student_ids)} students rows")




COURSE_CATALOG = [
    ("BIO101", "Introduction to Biology", "Biology", 4),
    ("BIO201", "Genetics", "Biology", 4),
    ("CS101", "Intro to Programming", "Computer Science", 3),
    ("CS201", "Data Structures", "Computer Science", 3),
    ("BUS101", "Principles of Management", "Business", 3),
    ("BUS210", "Financial Accounting", "Business", 3),
    ("PSY101", "Introduction to Psychology", "Psychology", 3),
    ("PSY220", "Developmental Psychology", "Psychology", 3),
    ("NUR101", "Foundations of Nursing", "Nursing", 4),
    ("NUR210", "Pharmacology", "Nursing", 4),
    ("EDU101", "Foundations of Education", "Education", 3),
    ("ENG101", "College Writing I", "English", 3),
    ("MATH110", "College Algebra", "Mathematics", 3),
    ("MATH201", "Statistics", "Mathematics", 3),
    ("HIST101", "World History", "History", 3),
]

course_ids = []

for code, name, dept, credits in COURSE_CATALOG:
    cursor.execute(
        "INSERT INTO courses (course_code, course_name, department, credits) VALUES (?, ?, ?, ?)",
        (code, name, dept, credits)
    )
    course_ids.append(cursor.lastrowid)

conn.commit()
print(f"Inserted {len(course_ids)} courses rows")



application_ids = []
enrolled_student_cohort = {}  # student_id -> cohort_term, only for those who actually enroll

for sid in student_ids:
    cohort = random.choice(COHORTS)
    program = random.choice(PROGRAMS)

    # ~65% acceptance rate
    decision = np.random.choice(["Accepted", "Rejected", "Waitlisted"], p=[0.65, 0.28, 0.07])

    # of those accepted, ~55% actually enroll (yield)
    enrolled = False
    if decision == "Accepted":
        enrolled = bool(np.random.choice([1, 0], p=[0.55, 0.45]))

    cursor.execute(
        """INSERT INTO applications (student_id, term, program, decision, decision_date, enrolled)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (sid, cohort, program, decision, f"{cohort.split()[1]}-03-15", int(enrolled))
    )
    application_ids.append(cursor.lastrowid)

    if enrolled:
        enrolled_student_cohort[sid] = (cohort, program)

conn.commit()
print(f"Inserted {len(application_ids)} applications rows")
print(f"{len(enrolled_student_cohort)} students actually enrolled")


enrollment_ids = []
student_enrollment_status = {}  # student_id -> still enrolled? for later retention logic

for sid, (cohort, program) in enrolled_student_cohort.items():
    full_time = bool(np.random.choice([1, 0], p=[0.78, 0.22]))
    status = "Enrolled"

    cursor.execute(
        """INSERT INTO enrollments (student_id, term, program, enrollment_status, full_time, cohort_term)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (sid, cohort, program, status, int(full_time), cohort)
    )
    enrollment_ids.append(cursor.lastrowid)
    student_enrollment_status[sid] = {"cohort": cohort, "program": program, "full_time": full_time}

conn.commit()
print(f"Inserted {len(enrollment_ids)} enrollments rows")


student_credit_completion = {}  # student_id -> first semester completion rate (0 to 1)

for sid, info in student_enrollment_status.items():
    n_courses = random.randint(4, 5)
    chosen_courses = random.sample(course_ids, n_courses)

    credits_attempted_total = 0
    credits_earned_total = 0

    # first-gen and low-income students face slightly more first-semester friction (realistic, not deterministic)
    base_pass_prob = 0.82
    credits_attempted_total = 0
    credits_earned_total = 0

    for cid in chosen_courses:
        cursor.execute("SELECT credits FROM courses WHERE course_id = ?", (cid,))
        credits = cursor.fetchone()[0]

        passed = np.random.choice([1, 0], p=[base_pass_prob, 1 - base_pass_prob])
        grade = np.random.choice(["A", "B", "C", "D", "F", "W"],
                                   p=[0.20, 0.28, 0.22, 0.10, 0.10, 0.10]) if not passed else \
                 np.random.choice(["A", "B", "C"], p=[0.35, 0.40, 0.25])

        earned = credits if grade not in ["F", "W"] else 0

        cursor.execute(
            """INSERT INTO course_attempts (student_id, course_id, term, grade, credits_attempted, credits_earned)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (sid, cid, info["cohort"], grade, credits, earned)
        )

        credits_attempted_total += credits
        credits_earned_total += earned

    completion_rate = credits_earned_total / credits_attempted_total if credits_attempted_total > 0 else 0
    student_credit_completion[sid] = completion_rate

conn.commit()
print(f"Inserted course_attempts for {len(student_credit_completion)} students")


CURRENT_YEAR = 2025

for sid, info in student_enrollment_status.items():
    cohort_year = int(info["cohort"].split()[1])
    years_since_entry = CURRENT_YEAR - cohort_year
    completion = student_credit_completion.get(sid, 0.8)

    # base dropout risk, INCREASED when first-semester completion is low
    base_risk = 0.12
    if completion < 0.70:
        base_risk += 0.28   # this is the real signal: low completion -> much higher risk
    elif completion < 0.85:
        base_risk += 0.10

    # small additional bump for first-gen students (realistic, modest effect)
    cursor.execute("SELECT d.first_gen FROM students s JOIN demographics d ON s.demographic_id = d.demographic_id WHERE s.student_id = ?", (sid,))
    first_gen = cursor.fetchone()[0]
    if first_gen:
        base_risk += 0.05

    base_risk = min(base_risk, 0.85)

    checkpoints_to_generate = min(years_since_entry, 4)
    still_retained = True

    for year in range(1, checkpoints_to_generate + 1):
        if still_retained:
            dropped_this_year = np.random.choice([1, 0], p=[base_risk, 1 - base_risk])
            still_retained = not dropped_this_year

        cursor.execute(
            """INSERT INTO retention (student_id, cohort_term, checkpoint_year, retained)
               VALUES (?, ?, ?, ?)""",
            (sid, info["cohort"], year, int(still_retained))
        )

conn.commit()
print("Inserted retention rows")


for sid, info in student_enrollment_status.items():
    cohort_year = int(info["cohort"].split()[1])
    years_since_entry = CURRENT_YEAR - cohort_year

    cursor.execute(
        "SELECT retained FROM retention WHERE student_id = ? ORDER BY checkpoint_year DESC LIMIT 1",
        (sid,)
    )
    row = cursor.fetchone()
    last_retained = row[0] if row else 1

    graduated = False
    grad_term = None
    years_to_degree = None

    if last_retained and years_since_entry >= 4:
        graduated = bool(np.random.choice([1, 0], p=[0.68, 0.32]))
        if graduated:
            years_to_degree = round(np.random.choice([4.0, 4.5, 5.0, 5.5, 6.0], p=[0.45, 0.25, 0.15, 0.10, 0.05]), 1)
            grad_term = f"Spring {cohort_year + int(years_to_degree)}"

    cursor.execute(
        """INSERT INTO graduation (student_id, cohort_term, graduated, graduation_term, years_to_degree)
           VALUES (?, ?, ?, ?, ?)""",
        (sid, info["cohort"], int(graduated), grad_term, years_to_degree)
    )

conn.commit()
print("Inserted graduation rows")


AID_TYPES = ["Pell Grant", "Institutional Scholarship", "Federal Loan", "Work-Study"]

for sid, info in student_enrollment_status.items():
    pell_eligible = bool(np.random.choice([1, 0], p=[0.36, 0.64]))
    n_aid_types = random.randint(1, 2) if not pell_eligible else random.randint(2, 3)
    aid_types_for_student = random.sample(AID_TYPES, min(n_aid_types, len(AID_TYPES)))

    for aid_type in aid_types_for_student:
        amount = {
            "Pell Grant": random.randint(2000, 6500),
            "Institutional Scholarship": random.randint(1000, 15000),
            "Federal Loan": random.randint(3000, 12000),
            "Work-Study": random.randint(1500, 4000),
        }[aid_type]

        cursor.execute(
            """INSERT INTO financial_aid (student_id, term, aid_type, amount, pell_eligible)
               VALUES (?, ?, ?, ?, ?)""",
            (sid, info["cohort"], aid_type, amount, int(pell_eligible))
        )

conn.commit()
print("Inserted financial_aid rows")

SURVEY_TYPES = ["Orientation Survey", "Annual Satisfaction Survey"]

for sid, info in student_enrollment_status.items():
    for survey in SURVEY_TYPES:
        score = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.10, 0.20, 0.35, 0.30])
        would_recommend = bool(np.random.choice([1, 0], p=[0.7 if score >= 4 else 0.3, 0.3 if score >= 4 else 0.7]))

        cursor.execute(
            """INSERT INTO survey_responses (student_id, term, survey_type, satisfaction_score, would_recommend)
               VALUES (?, ?, ?, ?, ?)""",
            (sid, info["cohort"], survey, int(score), int(would_recommend))
        )

conn.commit()
print("Inserted survey_responses rows")

conn.close()
print("Done — database fully populated.")


