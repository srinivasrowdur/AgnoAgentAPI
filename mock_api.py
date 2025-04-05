from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Create the FastAPI app
app = FastAPI(
    title="Mock Standards Agents API",
    description="Mock API for testing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define request models
class QueryRequest(BaseModel):
    query: str
    model_id: Optional[str] = None

class TeamQueryRequest(BaseModel):
    query: str
    model_id: Optional[str] = None
    team_mode: Optional[str] = "collaborate"

# Endpoint to ask questions to the Safety Agent
@app.post("/safety/ask")
async def ask_safety_agent(request: QueryRequest):
    return {"response": f"Safety response to: {request.query}"}

# Endpoint to ask questions to the Quality Agent
@app.post("/quality/ask")
async def ask_quality_agent(request: QueryRequest):
    return {"response": f"Quality response to: {request.query}"}

# Endpoint to ask questions to the Team Agent
@app.post("/team/ask")
async def ask_team_agent(request: TeamQueryRequest):
    return {"response": f"Team response ({request.team_mode}) to: {request.query}"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "agents": ["safety", "quality", "team"]}

# Root endpoint with basic info
@app.get("/")
async def root():
    return {
        "app": "Mock Standards Agents API",
        "version": "1.0.0",
        "endpoints": {
            "POST /safety/ask": "Ask a question to the Safety Standards Agent",
            "POST /quality/ask": "Ask a question to the Quality Standards Agent",
            "POST /team/ask": "Ask a question to the Team Agent (combines both agents)",
            "GET /health": "Health check"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mock_api:app", host="0.0.0.0", port=8080, reload=True) 