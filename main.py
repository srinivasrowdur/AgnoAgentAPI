from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import os
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Import the agents - wrapped in try/except to avoid startup failures
try:
    from agno.models.openai import OpenAIChat
    from agents import SafetyAgent, QualityAgent, TeamAgent, AGENTS, TEAM_INSTRUCTIONS, are_agents_available
    
    # Print status of agent initialization
    if are_agents_available():
        logger.info("Agents successfully loaded")
    else:
        logger.warning("Agents were not initialized properly")
        
except ImportError as e:
    logger.error(f"Error importing agent modules: {str(e)}")
    # Create empty objects for graceful failure
    AGENTS = {}
    TEAM_INSTRUCTIONS = {}
    SafetyAgent = None
    QualityAgent = None
    TeamAgent = None
    
    def are_agents_available():
        return False
        
except Exception as e:
    logger.error(f"Unexpected error loading agents: {str(e)}")
    # Create empty objects for graceful failure
    AGENTS = {}
    TEAM_INSTRUCTIONS = {}
    SafetyAgent = None
    QualityAgent = None 
    TeamAgent = None
    
    def are_agents_available():
        return False

# Diagnostic endpoint to check config without connecting to LanceDB
@app.get("/config")
async def get_config():
    return {
        "lance_url": os.environ.get("LanceURL", "Not set"),
        "lance_api_key_set": bool(os.environ.get("LANCE_API_KEY")),
        "openai_api_key_set": bool(os.environ.get("OPENAI_API_KEY")),
        "agents_available": are_agents_available() if 'are_agents_available' in globals() else False
    }

# Endpoint to ask questions to the Safety Agent
@app.post("/safety/ask")
async def ask_safety_agent(request: QueryRequest):
    if not SafetyAgent:
        raise HTTPException(status_code=503, detail="Safety Agent is not available due to LanceDB connection issues")
        
    try:
        # Use the model_id if provided
        if request.model_id:
            from agno.models.openai import OpenAIChat
            model = OpenAIChat(id=request.model_id)
            SafetyAgent.model = model
            
        response = SafetyAgent.run(request.query)
        return {"response": response.content}
    except Exception as e:
        logger.error(f"Error processing safety agent request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to ask questions to the Quality Agent
@app.post("/quality/ask")
async def ask_quality_agent(request: QueryRequest):
    if not QualityAgent:
        raise HTTPException(status_code=503, detail="Quality Agent is not available due to LanceDB connection issues")
        
    try:
        # Use the model_id if provided
        if request.model_id:
            from agno.models.openai import OpenAIChat
            model = OpenAIChat(id=request.model_id)
            QualityAgent.model = model
            
        response = QualityAgent.run(request.query)
        return {"response": response.content}
    except Exception as e:
        logger.error(f"Error processing quality agent request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to ask questions to the Team Agent
@app.post("/team/ask")
async def ask_team_agent(request: TeamQueryRequest):
    if not TeamAgent:
        raise HTTPException(status_code=503, detail="Team Agent is not available due to LanceDB connection issues")
        
    try:
        # Use the model_id if provided
        if request.model_id:
            from agno.models.openai import OpenAIChat
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
        logger.error(f"Error processing team agent request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    agents_status = "available" if (are_agents_available() if 'are_agents_available' in globals() else False) else "unavailable"
    available_agents = list(AGENTS.keys()) if AGENTS else []
    
    return {
        "status": "healthy",
        "agents_status": agents_status,
        "available_agents": available_agents
    }

# Root endpoint with basic info
@app.get("/")
async def root():
    agents_status = "available" if (are_agents_available() if 'are_agents_available' in globals() else False) else "unavailable"
    
    return {
        "app": "Standards Agents API",
        "version": "1.0.0",
        "agents_status": agents_status,
        "endpoints": {
            "POST /safety/ask": "Ask a question to the Safety Standards Agent",
            "POST /quality/ask": "Ask a question to the Quality Standards Agent",
            "POST /team/ask": "Ask a question to the Team Agent (combines both agents)",
            "GET /health": "Health check",
            "GET /config": "View configuration without requiring LanceDB connectivity"
        }
    }

if __name__ == "__main__":
    import asyncio
    import uvicorn
    # Get the port from the environment variable
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting server on port {port}")
    # Disable uvloop to avoid conflict with nest_asyncio
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False, loop="asyncio") 