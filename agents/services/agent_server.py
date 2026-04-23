"""
Generic FastAPI server that runs a single Aetherion agent.
Set environment variable AETHERION_AGENT to the agent class name.
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.colleges.all_colleges import AGENT_REGISTRY
from agents.colleges.base import CollegeAgent

app = FastAPI()

AGENT_NAME = os.getenv("AETHERION_AGENT", "PhysicistAgent")
if AGENT_NAME not in AGENT_REGISTRY:
    raise ValueError(f"Unknown agent: {AGENT_NAME}")

agent: CollegeAgent = AGENT_REGISTRY[AGENT_NAME](name=AGENT_NAME)


class AnalyzeRequest(BaseModel):
    goal: str
    context: dict = {}


class AnalyzeResponse(BaseModel):
    assessment: str
    confidence: float
    concerns: list = []
    recommendations: list = []


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    try:
        result = agent.analyze(request.goal, context=request.context)
        return AnalyzeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"agent": AGENT_NAME, "status": "ok"}
