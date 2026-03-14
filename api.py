import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import ask, OLLAMA_MODEL  # Make sure agent.py has OLLAMA_MODEL defined

app = FastAPI(
    title="School ERP AI Query Agent",
    description="Natural language → MongoDB → Friendly answer — powered by LLaMA 3 via Ollama",
    version="1.0.0",
)

# Request & Response models
class QuestionRequest(BaseModel):
    question: str
    verbose: bool = False

class QuestionResponse(BaseModel):
    question: str
    answer: str
    model: str

# Health check
@app.get("/health")
def health():
    return {"status": "ok", "model": OLLAMA_MODEL}

# Ask endpoint
@app.post("/ask", response_model=QuestionResponse)
def ask_endpoint(req: QuestionRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        answer = ask(req.question, req.verbose)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    return QuestionResponse(
        question=req.question,
        answer=answer,
        model=OLLAMA_MODEL
    )

# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)