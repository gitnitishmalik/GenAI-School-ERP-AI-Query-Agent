"""
Professional-Grade GenAI MongoDB Query Agent — LLaMA 3 Edition
Features:
- Dynamic schema detection
- Query guardrails
- Explainable responses
- Verbose/debug mode
- Automatically shows MongoDB query for every user query
"""

import os
import json
import re
from datetime import datetime, timedelta, UTC
import ollama
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

# ---------------- CONFIG ----------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "erp_school")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

mongo_client = None
db = None

# ---------------- DATABASE CONNECTION ----------------
def get_db():
    global mongo_client, db
    if db is None:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        mongo_client.admin.command("ping")
        db = mongo_client[DB_NAME]
    return db

# ---------------- DYNAMIC SCHEMA DETECTION ----------------
def get_schema_metadata(database):
    schema = {}
    for coll_name in database.list_collection_names():
        sample = database[coll_name].find_one()
        schema[coll_name] = list(sample.keys()) if sample else []
    return schema

# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """
You are a MongoDB query generator for a School ERP system.
Convert user questions into safe JSON queries.
Return ONLY JSON in this format:

{
 "collection":"collection_name",
 "operation":"find|aggregate|count",
 "filter":{},
 "projection":{},
 "pipeline":[],
 "description":"short explanation"
}

Rules:
- Only use collections in schema metadata
- Use find for basic lists
- Use aggregate for grouping, percentages, top results, joins
- Use count for totals
- ISO date format
- Do not output anything other than JSON
"""

# ---------------- PROMPT BUILDER WITH DATES ----------------
def build_system_prompt(schema_metadata):
    today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    month_start = today.replace(day=1)
    month_end = (today.replace(month=today.month+1, day=1) - timedelta(days=1)) if today.month != 12 else today.replace(day=31)

    schema_str = json.dumps(schema_metadata, indent=2)
    dates_str = f"Dates: today={today.isoformat()}, yesterday={yesterday.isoformat()}, week_start={week_start.isoformat()}, week_end={week_end.isoformat()}, month_start={month_start.isoformat()}, month_end={month_end.isoformat()}"
    return SYSTEM_PROMPT + "\n\nSchema Metadata:\n" + schema_str + "\n\n" + dates_str

# ---------------- CLEAN & EXTRACT JSON ----------------
def clean_llm_output(text: str):
    text = text.strip()
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()

def extract_json(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("LLM did not return JSON")
    return json.loads(match.group())

# ---------------- QUERY VALIDATION ----------------
def validate_query(plan, schema_metadata):
    if plan["operation"] not in ["find","aggregate","count"]:
        raise ValueError(f"Unsupported operation: {plan['operation']}")
    if plan["collection"] not in schema_metadata:
        raise ValueError(f"Invalid collection: {plan['collection']}")
    return True

# ---------------- GENERATE QUERY PLAN ----------------
def generate_query_plan(question, schema_metadata):
    response = ollama.chat(
        model=OLLAMA_MODEL,
        options={"temperature":0},
        messages=[
            {"role":"system","content": build_system_prompt(schema_metadata)},
            {"role":"user","content": question},
        ]
    )
    raw = response["message"]["content"]
    raw = clean_llm_output(raw)
    plan = extract_json(raw)
    validate_query(plan, schema_metadata)
    return plan

# ---------------- EXECUTE QUERY ----------------
def execute_query(plan, database):
    col = database[plan["collection"]]
    op = plan["operation"]

    if op == "find":
        cursor = col.find(plan.get("filter",{}), plan.get("projection", None)).limit(50)
        return list(cursor)
    if op == "aggregate":
        return list(col.aggregate(plan.get("pipeline", [])))
    if op == "count":
        return col.count_documents(plan.get("filter",{}))
    raise ValueError("Unsupported operation")

# ---------------- FORMAT RESPONSE ----------------
def format_response(question, plan, results):
    payload = {
        "question": question,
        "description": plan.get("description"),
        "results": results if isinstance(results,int) else results[:20],
        "count": results if isinstance(results,int) else len(results)
    }
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role":"system","content": "You are a helpful school assistant. Convert JSON results into human-friendly text. Do not mention MongoDB or queries."},
            {"role":"user","content": json.dumps(payload, default=str)}
        ]
    )
    return response["message"]["content"]

# ---------------- MAIN ASK FUNCTION ----------------
def ask(question, verbose=False):
    try:
        database = get_db()
    except ConnectionFailure:
        return "Could not connect to MongoDB."
    
    schema_metadata = get_schema_metadata(database)
    
    try:
        plan = generate_query_plan(question, schema_metadata)
    except Exception as e:
        return f"Query generation error: {e}"

    # 1️⃣ Automatically show MongoDB query for every question
    print("\nGenerated Mongo Query (hidden from user):")
    print(json.dumps(plan, indent=2))

    # 2️⃣ Execute the query
    try:
        results = execute_query(plan, database)
    except Exception as e:
        return f"Query execution error: {e}"

    # 3️⃣ Return the human-readable agent response
    return format_response(question, plan, results)

# ---------------- CLI INTERFACE ----------------
def main():
    print("="*60)
    print("Professional School ERP AI Agent (Llama3 + MongoDB)")
    print("Type 'quit' to exit")
    print("="*60)

    while True:
        question = input("\nYou: ")
        if question.lower() == "quit":
            break
        
        # Ask the question → automatically show query and response
        answer = ask(question)
        print("\nAgent:", answer)

if __name__ == "__main__":
    main()