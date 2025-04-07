#!/usr/bin/env python3
import os
from dotenv import load_dotenv

from agno.agent import Agent
from agno.document.chunking.agentic import AgenticChunking
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.vectordb.lancedb import LanceDb
from agno.vectordb.search import SearchType
from agno.embedder.openai import OpenAIEmbedder
from agno.models.openai import OpenAIChat
from agno.team.team import Team

# Load environment variables from .env file
load_dotenv()

# Get LanceDB cloud credentials
lance_url = os.environ.get("LanceURL")
lance_api_key = os.environ.get("LANCE_API_KEY")

if not lance_url or not lance_api_key:
    raise ValueError("LanceDB cloud configuration is incomplete. Please check your .env file for LanceURL and LANCE_API_KEY.")

# Default model
default_model_id = "o3-mini"

# Initialize vector databases with cloud storage
try:
    safety_vector_db = LanceDb(
        table_name="safety_standards",
        uri=lance_url,
        api_key=lance_api_key,
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small")
    )

    quality_vector_db = LanceDb(
        table_name="quality_standards",
        uri=lance_url,
        api_key=lance_api_key,
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small")
    )

    # Initialize knowledge bases
    safety_knowledge_base = PDFKnowledgeBase(
        path="data/pdfs",
        vector_db=safety_vector_db,
        chunking_strategy=AgenticChunking(),
    )

    quality_knowledge_base = PDFKnowledgeBase(
        path="data/Quality PDF",
        vector_db=quality_vector_db,
        chunking_strategy=AgenticChunking(),
    )

    # Create individual agents
    SafetyAgent = Agent(
        name="Safety Standards Agent",
        role="You are an expert on safety standards and protocols. Always provide your response in a concise manner based on the information provided in the documents.",
        model=OpenAIChat(id=default_model_id),
        knowledge=safety_knowledge_base,
        search_knowledge=True,
        show_tool_calls=False,
        markdown=True,
    )

    QualityAgent = Agent(
        name="Quality Standards Agent",
        role="You are an expert on quality standards and quality assurance processes. Always provide your response in a concise manner based on the information provided in the documents.",
        model=OpenAIChat(id=default_model_id),
        knowledge=quality_knowledge_base,
        search_knowledge=True,
        show_tool_calls=False,
        markdown=True,
    )

    # Define instructions for team modes
    collaborate_instructions = [
        "First determine whether the question is primarily about safety standards or quality standards.",
        "For safety questions (workplace safety, hazard prevention, fire safety, electrical safety, etc.), primarily rely on the Safety Standards Agent.",
        "For quality questions (quality assurance, cross-contamination prevention, personnel hygiene, etc.), primarily rely on the Quality Standards Agent.",
        "Synthesize a comprehensive response based on contributions from all experts.",
        "Always identify which expert provided which information in your response.",
        "If the question is completely unrelated to either safety or quality standards, respond that you can only answer questions related to safety and quality standards."
    ]

    route_instructions = [
        "Analyze the user's question to determine if it's about safety standards or quality standards.",
        "If the question is about safety protocols, workplace safety, hazard prevention, fire safety, electrical safety, noise standards, fall prevention, etc., route to the Safety Standards Agent.",
        "If the question is about quality assurance, quality control, cross-contamination prevention, personnel hygiene, utilities quality, etc., route to the Quality Standards Agent.",
        "If the question could apply to both domains, prioritize routing based on the most relevant expertise needed.",
        "Always provide a brief explanation of why you're routing to a particular agent before routing.",
        "If the question is completely unrelated to either safety or quality standards, respond that you can only answer questions related to safety and quality standards."
    ]

    coordinate_instructions = [
        "Break down the user's question into specific sub-tasks for each relevant team member.",
        "Delegate safety-related aspects (workplace safety, hazard prevention, fire safety, etc.) to the Safety Standards Agent.",
        "Delegate quality-related aspects (quality assurance, hygiene, contamination prevention, etc.) to the Quality Standards Agent.",
        "Synthesize the responses from each team member into a cohesive answer.",
        "Ensure the final response is comprehensive and addresses all aspects of the question.",
        "If the question is completely unrelated to either safety or quality standards, respond that you can only answer questions related to safety and quality standards."
    ]

    # Store team mode instructions in a dictionary for easy access
    TEAM_INSTRUCTIONS = {
        "collaborate": {
            "instructions": collaborate_instructions,
            "description": "You are a collaborative team where all members work on the same task to create comprehensive responses."
        },
        "route": {
            "instructions": route_instructions,
            "description": "You are a router that directs questions to the appropriate standards agent."
        },
        "coordinate": {
            "instructions": coordinate_instructions,
            "description": "You are a coordinator that delegates tasks to team members and synthesizes their outputs."
        }
    }

    # Create team agent (using collaborate mode by default)
    TeamAgent = Team(
        name="Standards Team",
        mode="collaborate",
        model=OpenAIChat(id=default_model_id),
        members=[SafetyAgent, QualityAgent],
        share_member_interactions=True,
        show_tool_calls=False,
        markdown=True,
        description="You are a collaborative team where all members work on the same task to create comprehensive responses.",
        instructions=collaborate_instructions,
        show_members_responses=True,
        debug_mode=False,
    )

    # For convenience, create a dictionary of available agents
    AGENTS = {
        "safety": SafetyAgent,
        "quality": QualityAgent,
        "team": TeamAgent
    }
    
    # Function to check if agents are available
    def are_agents_available():
        return True

except Exception as e:
    import traceback
    print(f"Error initializing agents: {str(e)}")
    traceback.print_exc()
    
    # Create empty objects for graceful failure
    AGENTS = {}
    TEAM_INSTRUCTIONS = {}
    SafetyAgent = None
    QualityAgent = None
    TeamAgent = None
    
    # Function to check if agents are available
    def are_agents_available():
        return False

# Helper function to load data into knowledge bases if needed
def load_knowledge_bases(reload_safety=False, reload_quality=False):
    """Load data into knowledge bases."""
    if reload_safety:
        print("Loading safety documents into knowledge base...")
        safety_knowledge_base.load(recreate=False)  # False for cloud storage
        print("Safety documents loaded successfully!")
    
    if reload_quality:
        print("Loading quality documents into knowledge base...")
        quality_knowledge_base.load(recreate=False)  # False for cloud storage
        print("Quality documents loaded successfully!")

if __name__ == "__main__":
    print("Agent definitions loaded. Import these agents in your FastAPI application.")
    # Example import in FastAPI:
    # from agents import SafetyAgent, QualityAgent, TeamAgent 