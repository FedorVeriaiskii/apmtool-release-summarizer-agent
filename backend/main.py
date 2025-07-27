
# FastAPI backend for Dynatrace Release Notes Summarizer Agent
# Provides REST API endpoints for processing and summarizing Dynatrace release notes

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import os
from dotenv import load_dotenv

import openai
from pydantic import BaseModel
from .services.process_oneagent_release_notes import ProcessOneAgentReleaseNotes


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client and OneAgent processor
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None

# Initialize the OneAgent release notes processor
oneagent_processor = ProcessOneAgentReleaseNotes(openai_client)


class ComponentLatestReleaseVersion(BaseModel):
    """Pydantic model for version responses"""
    version: str



@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"message": "Hello from FastAPI!"}


@app.post("/api/dynatrace-release-news-summary")
async def build_dynatrace_release_news_summary(request: Request):
    """Main endpoint to generate Dynatrace release news summary"""
    
    # Parse request body to check for selectedItems
    try:
        request_body = await request.json()
        selected_items = request_body.get("selectedItems", [])
        
        # Check if any selected item contains "oneagent" key
        oneagent_selected = False
        for item in selected_items:
            if isinstance(item, dict) and "oneagent" in item:
                oneagent_selected = True
                break
        
        if oneagent_selected:
            return await oneagent_processor.process_dynatrace_release_news()
        else:
            return JSONResponse(
                status_code=400, 
                content={"error": "No OneAgent release notes selected. Please select OneAgent to proceed."}
            )
            
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Invalid request format: {str(e)}"})
