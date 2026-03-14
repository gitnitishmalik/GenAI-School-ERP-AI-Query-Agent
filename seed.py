"""
seed.py — Populates the erp_school MongoDB database with realistic sample data.
Run once before starting the agent: python seed.py
"""

import os
import random
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from calendar import monthrange

# ───────────────── CONFIG ─────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "erp_school")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ───────────────── HELPERS ─────────────────
def rand_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

TODAY = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
YESTERDAY = TODAY - timedelta(days=1)

# ───────────────── RESET DATABASE ─────────────────
for col in ["students", "teachers", "classes", "courses", "attendance", "assignments", "exams"]:
    db[col].drop()

print("Dropped existing collections.")

# ───────────────── TEACHERS ─────────────────
teachers_data = [
    {"name": "Rohit Sharma", "email": "rohit@school.edu", "subject": "Math", "assigned_classes": ["Class 5", "Class 6"]},
    {"name": "Anjali Verma", "email": "anjali@school.edu", "subject": "Science", "assigned_classes": ["Class 6", "Class 7"]},
    {"name": "Vivek Gupta", "email": "vivek@school.edu", "subject": "English", "assigned_classes": ["Class 5", "Class 7"]},
    {"name": "Neha Iyer", "email": "neha@school.edu", "subject": "History", "assigned_classes": ["Class 5"]},
    {"name": "Amit Patel", "email": "amit@school.edu", "subject": "CS", "assigned_classes": ["Class 6", "Class 7"]},
]

teacher_ids = db.teachers.insert_many(teachers_data).inserted_ids
print("Inserted teachers:", len(teacher_ids))

# ───────────────── CLASSES ─────────────────
classes_data = [
    {"class_name": "Class 5", "section": "A", "teacher_id": teacher_ids[0]},
    {"class_name": "Class 5", "section": "B", "teacher_id": teacher_ids[3]},
    {"class_name": "Class 6", "section": "A", "teacher_id": teacher_ids[1]},
    {"class_name": "Class 6", "section": "B", "teacher_id": teacher_ids[4]},
    {"class_name": "Class 7", "section": "A", "teacher_id": teacher_ids[2]},
]

db.classes.insert_many(classes_data)
print("Inserted classes:", len(classes_data))

# ───────────────── STUDENTS ─────────────────
first_names = [
    "Aarav","Vivaan","Aditya","Sai","Krishna","Aryan","Rohan",
    "Ananya","Ishaan","Aditi","Kavya","Saanvi","Anika",
    "Dhruv","Ishita","Ved","Meera","Lakshya","Tanvi","Riya"
]

last_names = [
    "Sharma","Verma","Gupta","Reddy","Iyer",
    "Chopra","Patel","Mehta","Singh","Kumar"
]

class_sections = [
    ("Class 5","A"),
    ("Class 5","B"),
    ("Class 6","A"),
    ("Class 6","B"),
    ("Class 7","A")
]

students_data = []

for i in range(60):

    cn, sec = class_sections[i % len(class_sections)]
    name = f"{random.choice(first_names)} {random.choice(last_names)}"

    students_data.append({
        "name": name,
        "email": f"student{i+1}@school.edu",
        "class_name": cn,
        "section": sec,
        "roll_no": i + 1,
        "attendance_percentage": 0,
        "enrolled_date": rand_date(
            datetime(2023,1,1,tzinfo=timezone.utc),
            datetime(2023,8,31,tzinfo=timezone.utc)
        ),
    })

student_ids = db.students.insert_many(students_data).inserted_ids
print("Inserted students:", len(student_ids))

# ───────────────── COURSES ─────────────────
courses_data = [
    {"course_name": "Algebra", "class_name": "Class 5", "teacher_id": teacher_ids[0]},
    {"course_name": "Basic Science", "class_name": "Class 5", "teacher_id": teacher_ids[1]},
    {"course_name": "English Lit", "class_name": "Class 5", "teacher_id": teacher_ids[2]},
    {"course_name": "Geometry", "class_name": "Class 6", "teacher_id": teacher_ids[0]},
    {"course_name": "Chemistry", "class_name": "Class 6", "teacher_id": teacher_ids[1]},
    {"course_name": "Intro to CS", "class_name": "Class 6", "teacher_id": teacher_ids[4]},
    {"course_name": "Advanced Math", "class_name": "Class 7", "teacher_id": teacher_ids[0]},
    {"course_name": "Physics", "class_name": "Class 7", "teacher_id": teacher_ids[1]},
    {"course_name": "Creative Writing", "class_name": "Class 7", "teacher_id": teacher_ids[2]},
]

db.courses.insert_many(courses_data)

# ───────────────── ATTENDANCE ─────────────────
attendance_docs = []

for i, student in enumerate(students_data):

    present_days = 0

    for d in range(30):

        date = TODAY - timedelta(days=d)

        status = "absent" if random.random() < 0.15 else "present"

        if status == "present":
            present_days += 1

        attendance_docs.append({
            "student_id": str(student_ids[i]),
            "student_name": student["name"],
            "class_name": student["class_name"],
            "section": student["section"],
            "date": date,
            "status": status
        })

    percentage = round((present_days / 30) * 100, 2)

    db.students.update_one(
        {"email": student["email"]},
        {"$set": {"attendance_percentage": percentage}}
    )

db.attendance.insert_many(attendance_docs)

print("Inserted attendance records:", len(attendance_docs))

# ───────────────── ASSIGNMENTS ─────────────────
assignments_data = []

week_start = TODAY - timedelta(days=TODAY.weekday())
week_end = week_start + timedelta(days=6)

for cls in ["Class 5", "Class 6", "Class 7"]:

    class_students = [
        {"id": str(student_ids[idx]), "name": students_data[idx]["name"]}
        for idx in range(len(students_data))
        if students_data[idx]["class_name"] == cls
    ]

    submitted = random.sample(class_students, random.randint(5, len(class_students)//2))

    assignments_data.append({
        "title": f"Assignment – {cls}",
        "class_name": cls,
        "due_date": TODAY - timedelta(days=random.randint(1,5)),
        "created_at": TODAY - timedelta(days=random.randint(2,7)),
        "submissions": [
            {
                "student_id": s["id"],
                "student_name": s["name"],
                "submitted_at": TODAY - timedelta(days=1)
            }
            for s in submitted
        ]
    })

    assignments_data.append({
        "title": f"Weekly Quiz – {cls}",
        "class_name": cls,
        "due_date": week_end,
        "created_at": TODAY,
        "submissions": []
    })

    assignments_data.append({
        "title": f"Today's Homework – {cls}",
        "class_name": cls,
        "due_date": TODAY + timedelta(days=1),
        "created_at": TODAY,
        "submissions": []
    })

db.assignments.insert_many(assignments_data)

print("Inserted assignments:", len(assignments_data))

# ───────────────── EXAMS (FIXED) ─────────────────
exams_data = []

month_start = TODAY.replace(day=1)
last_day = monthrange(TODAY.year, TODAY.month)[1]
month_end = TODAY.replace(day=last_day)

for cls in ["Class 5","Class 6","Class 7"]:
    for subj in ["Math","Science","English"]:

        exam_date = rand_date(month_start, month_end)

        exams_data.append({
            "title": f"{subj} Exam – {cls}",
            "class_name": cls,
            "subject": subj,
            "exam_date": exam_date
        })

db.exams.insert_many(exams_data)

print("Inserted exams:", len(exams_data))

print("\n✅ Seed complete! Database:", DB_NAME)

client.close()