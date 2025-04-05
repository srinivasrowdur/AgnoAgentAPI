from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from agno.models.openai import OpenAIChat

# Import the agents from our agents.py file
from agents import SafetyAgent, QualityAgent, TeamAgent, AGENTS, TEAM_INSTRUCTIONS

# Create the FastAPI app
app = FastAPI(
    title="Standards Agents API",
    description="API for Safety and Quality Standards Agents",
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
    team_mode: Optional[str] = "collaborate"  # Default to collaborate, can be "route" or "coordinate"

# Endpoint to ask questions to the Safety Agent
@app.post("/safety/ask")
async def ask_safety_agent(request: QueryRequest):
    try:
        # Use the model_id if provided
        if request.model_id:
            model = OpenAIChat(id=request.model_id)
            SafetyAgent.model = model
            
        response = SafetyAgent.run(request.query)
        return {"response": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to ask questions to the Quality Agent
@app.post("/quality/ask")
async def ask_quality_agent(request: QueryRequest):
    try:
        # Use the model_id if provided
        if request.model_id:
            model = OpenAIChat(id=request.model_id)
            QualityAgent.model = model
            
        response = QualityAgent.run(request.query)
        return {"response": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to ask questions to the Team Agent
@app.post("/team/ask")
async def ask_team_agent(request: TeamQueryRequest):
    try:
        # Use the model_id if provided
        if request.model_id:
            model = OpenAIChat(id=request.model_id)
            TeamAgent.model = model
        
        # Set the team mode and instructions
        if request.team_mode in TEAM_INSTRUCTIONS:
            TeamAgent.mode = request.team_mode
            TeamAgent.instructions = TEAM_INSTRUCTIONS[request.team_mode]["instructions"]
            TeamAgent.description = TEAM_INSTRUCTIONS[request.team_mode]["description"]
        else:
            raise HTTPException(status_code=400, detail=f"Invalid team mode: {request.team_mode}. Must be one of: {', '.join(TEAM_INSTRUCTIONS.keys())}")
            
        response = TeamAgent.run(request.query)
        return {"response": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "agents": list(AGENTS.keys())}

# Root endpoint with basic info
@app.get("/")
async def root():
    return {
        "app": "Standards Agents API",
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
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 