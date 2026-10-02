from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from agent_x import AgentX
from agent_y import AgentY
from negotiation import negotiate
from web_research import research_supporting, research_challenging

app = FastAPI(title="OmegaTruth API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str = Field(min_length=5, max_length=500)

@app.get("/")
def root():
    return {
        "message": "OmegaTruth API is running",
        "version": "1.1.0",
        "features": [
            "generic claim investigation",
            "independent supporting and counter research",
            "evidence exchange",
            "reassessment",
        ],
    }

@app.post("/analyze")
def analyze(request: QuestionRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please provide a claim to investigate.",
        )

    # The two research agents work independently and in parallel.
    with ThreadPoolExecutor(max_workers=2) as pool:
        future_a = pool.submit(research_supporting, question, 6)
        future_b = pool.submit(research_challenging, question, 6)
        supporting = future_a.result()
        challenging = future_b.result()

    agent_a = AgentX().analyze_question(question, supporting)
    agent_b = AgentY().analyze_question(question, challenging)
    negotiation = negotiate(agent_a, agent_b, question)

    return {
        "question": question,
        "agent_x": agent_a,
        "agent_y": agent_b,
        "negotiation": negotiation,
        "external_verification": {
            "mode": "live public web/news retrieval",
            "agent_x_sources": len(supporting),
            "agent_y_sources": len(challenging),
        },
    }
