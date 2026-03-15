from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import json

try:
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)

    # Check connection
    client.admin.command("ping")
    print("MongoDB connection successful\n")

except ConnectionFailure:
    print("Could not connect to MongoDB")
    exit()

# Access the database
db = client["erp_school"]

# Show collections
collections = db.list_collection_names()
print("Collections in database:")
print(collections)

print("\nDocument counts:")
print("Students:", db.students.count_documents({}))
print("Teachers:", db.teachers.count_documents({}))
print("Attendance:", db.attendance.count_documents({}))
print("Assignments:", db.assignments.count_documents({}))
print("Exams:", db.exams.count_documents({}))

# Show sample student
print("\nSample student document:\n")
student = db.students.find_one()
print(json.dumps(student, indent=2, default=str))