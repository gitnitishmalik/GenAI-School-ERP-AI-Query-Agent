# 🎓 GenAI School ERP — AI Query Agent

> Natural Language → MongoDB Query → Human-Friendly Response

A GenAI-powered School ERP query agent that converts natural language questions into MongoDB queries, executes them, and returns clean, friendly answers. Built with **Python**, **LLaMA 3 (via Ollama)**, **MongoDB**, **FastAPI**, and **Streamlit**.

---

## 📌 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [Setup & Installation](#setup--installation)
- [Running the Project](#running-the-project)
- [API Reference](#api-reference)
- [Supported Queries](#supported-queries)
- [Sample Output](#sample-output)
- [Optional Improvements](#optional-improvements)

---

## Overview

This project is a GenAI-powered backend agent for a School ERP system. Users ask questions in plain English — the agent dynamically generates and executes MongoDB queries, then returns clean, human-readable answers.

**Key capabilities:**
- Dynamic schema detection (no hardcoded field names)
- Query guardrails with operation validation
- Auto-displays the generated MongoDB query in debug/verbose mode
- Supports `find`, `aggregate`, and `count` operations
- REST API via FastAPI + interactive UI via Streamlit + CLI interface

---

## System Architecture

```
User Question
     ↓
Natural Language Understanding  (LLaMA 3 via Ollama)
     ↓
MongoDB Query Generation  (JSON plan: collection, operation, filter/pipeline)
     ↓
Query Validation  (operation whitelist + collection check)
     ↓
Query Execution  (PyMongo)
     ↓
Result Processing + Natural Language Formatting  (LLaMA 3)
     ↓
Chatbot Response
```

---

## Project Structure

```
GENAI/
├── agent.py            # Core agent: schema detection, query gen, execution, formatting
├── api.py              # FastAPI REST API (POST /ask, GET /health)
├── ui.py               # Streamlit frontend with chat history
├── seed.py             # Database seeder — run once to populate MongoDB
├── check_db.py         # Utility to inspect DB connection and document counts
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not committed)
└── .gitignore
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | LLaMA 3 via [Ollama](https://ollama.com) |
| Database | MongoDB (local or Atlas) |
| Backend API | FastAPI + Uvicorn |
| Frontend UI | Streamlit |
| Language | Python 3.10+ |
| DB Driver | PyMongo |

---

## Database Schema

The MongoDB database `erp_school` contains 7 collections:

### `students`
| Field | Type | Description |
|---|---|---|
| name | string | Student full name |
| email | string | Unique student email |
| class_name | string | e.g. `"Class 5"` |
| section | string | `"A"` or `"B"` |
| roll_no | int | Roll number |
| attendance_percentage | float | Computed from last 30 days |
| enrolled_date | datetime | Date of enrollment |

### `teachers`
| Field | Type | Description |
|---|---|---|
| name | string | Teacher full name |
| email | string | Unique teacher email |
| subject | string | Subject they teach |
| assigned_classes | array | List of class names |

### `classes`
| Field | Type | Description |
|---|---|---|
| class_name | string | e.g. `"Class 6"` |
| section | string | Section label |
| teacher_id | ObjectId | Reference to teachers collection |

### `courses`
| Field | Type | Description |
|---|---|---|
| course_name | string | e.g. `"Algebra"` |
| class_name | string | Associated class |
| teacher_id | ObjectId | Reference to teachers collection |

### `attendance`
| Field | Type | Description |
|---|---|---|
| student_id | string | Reference to student |
| student_name | string | Denormalized for query speed |
| class_name | string | Student's class |
| section | string | Student's section |
| date | datetime | Attendance date |
| status | string | `"present"` or `"absent"` |

### `assignments`
| Field | Type | Description |
|---|---|---|
| title | string | Assignment title |
| class_name | string | Target class |
| due_date | datetime | Submission deadline |
| created_at | datetime | Creation timestamp |
| submissions | array | List of `{student_id, student_name, submitted_at}` |

### `exams`
| Field | Type | Description |
|---|---|---|
| title | string | Exam title |
| class_name | string | Target class |
| subject | string | Subject name |
| exam_date | datetime | Scheduled exam date |

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- MongoDB running locally on port `27017` (or provide Atlas URI)
- [Ollama](https://ollama.com) installed with LLaMA 3 pulled

### 1. Clone & create virtual environment

```bash
git clone <your-repo-url>
cd GENAI
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

## Requirements

```
ollama
pymongo>=4.6.0
python-dotenv>=1.0.0
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
streamlit

```


```bash
pip install -r requirements.txt
```

### 3. Pull LLaMA 3 via Ollama

```bash
ollama pull llama3
```

### 4. Configure environment

Create a `.env` file in the project root:

```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=erp_school
OLLAMA_MODEL=llama3
```

### 5. Seed the database

```bash
python seed.py
```

This creates 60 students, 5 teachers, 5 classes, 9 courses, 1800 attendance records, 9 assignments, and 9 exams.

### 6. Verify the database (optional)

```bash
python check_db.py
```

Expected output:
```
MongoDB connection successful

Collections in database:
['students', 'teachers', 'classes', 'courses', 'attendance', 'assignments', 'exams']

Document counts:
Students: 60
Teachers: 5
Attendance: 1800
Assignments: 9
Exams: 9
```

---

## Running the Project

### Option 1 — CLI Agent (direct terminal)

```bash
python agent.py
```

### Option 2 — FastAPI REST Server

```bash
uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

Swagger docs available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Option 3 — Streamlit UI *(Optional)*

> 💡 This is optional. The project works fully via CLI or API without this.

Make sure the FastAPI server is running first, then:

```bash
streamlit run ui.py
```
---

## API Reference

### `GET /health`

Returns server and model status.

```json
{
  "status": "ok",
  "model": "llama3"
}
```

### `POST /ask`

Ask a natural language question.

**Request:**
```json
{
  "question": "Show students who were absent yesterday",
  "verbose": false
}
```

**Response:**
```json
{
  "question": "Show students who were absent yesterday",
  "answer": "The following 8 students were absent yesterday: Aarav Sharma (Class 5A), ...",
  "model": "llama3"
}
```

---

## Supported Queries

### Level 1 — Basic Queries
1. List all students in a particular class
2. Show the attendance of a student for a specific date
3. List all teachers in the system
4. Show all assignments created today

### Level 2 — Filtering Queries
5. Show students who were absent yesterday
6. List assignments due this week
7. Show students belonging to section A of class 6
8. Show all exams scheduled this month

### Level 3 — Aggregation Queries
9. Count how many students were absent today
10. Show the number of assignments submitted per class
11. Find the class with the highest number of absent students today

### Level 4 — Multi-Collection Queries
12. Show students who have not submitted an assignment
13. List teachers and the classes they teach
14. Show attendance percentage of each student

### Level 5 — Analytical Queries
15. Show the top 5 students with the highest attendance percentage

---

## Sample Output

Real CLI output for the query **"List all students in Class 5"**:

```
You: List all students in Class 5

Generated Mongo Query (hidden from user):
{
  "collection": "students",
  "operation": "find",
  "filter": {
    "class_name": "Class 5"
  },
  "projection": {},
  "pipeline": [],
  "description": "List all students in Class 5"
}

Agent: Here is the list of students in Class 5:

1.  Aryan Sharma    (Roll No. 1,  Section A, Attendance: 80.0%)
2.  Saanvi Patel    (Roll No. 2,  Section B, Attendance: 73.33%)
3.  Aarav Mehta     (Roll No. 6,  Section A, Attendance: 80.0%)
4.  Dhruv Kumar     (Roll No. 7,  Section B, Attendance: 80.0%)
5.  Rohan Sharma    (Roll No. 11, Section A, Attendance: 90.0%)
6.  Ishaan Mehta    (Roll No. 12, Section B, Attendance: 90.0%)
7.  Ishita Singh    (Roll No. 16, Section A, Attendance: 90.0%)
8.  Aditi Reddy     (Roll No. 17, Section B, Attendance: 90.0%)
9.  Vivaan Chopra   (Roll No. 21, Section A, Attendance: 93.33%)
10. Krishna Iyer    (Roll No. 22, Section B, Attendance: 86.67%)
...



The agent generates the MongoDB query, executes it, and formats a clean natural language response — all from a single English question.

---



