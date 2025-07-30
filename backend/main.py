
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
from services.process_oneagent_release_notes import ProcessOneAgentReleaseNotes
from services.process_activegate_release_notes import ProcessActiveGateReleaseNotes
from services.process_dynatrace_api_release_notes import ProcessDynatraceApiReleaseNotes
from services.process_dynatrace_operator_release_notes import ProcessDynatraceOperatorReleaseNotes


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

# Initialize OpenAI client and processors
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None

# Initialize the release notes processors
oneagent_processor = ProcessOneAgentReleaseNotes(openai_client)
activegate_processor = ProcessActiveGateReleaseNotes(openai_client)
dynatrace_api_processor = ProcessDynatraceApiReleaseNotes(openai_client)
dynatrace_operator_processor = ProcessDynatraceOperatorReleaseNotes(openai_client)


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
        
        # Check which components are selected
        oneagent_selected = False
        activegate_selected = False
        dynatrace_api_selected = False
        dynatrace_operator_selected = False
        
        for item in selected_items:
            if isinstance(item, dict):
                if "oneagent" in item:
                    oneagent_selected = True
                elif "active_gate" in item:
                    activegate_selected = True
                elif "dynatrace_api" in item:
                    dynatrace_api_selected = True
                elif "dynatrace_operator" in item:
                    dynatrace_operator_selected = True
        
        # Initialize response object
        response = {
            "oneagent": {
                "latestVersion": "",
                "summary": ""
            },
            "active-gate": {
                "latestVersion": "",
                "summary": ""
            },
            "dynatrace-api": {
                "latestVersion": "",
                "summary": ""
            },
            "dynatrace-operator": {
                "latestVersion": "",
                "summary": ""
            }
        }
        
        # Process OneAgent if selected
        if oneagent_selected:
            oneagent_result = await oneagent_processor.process_dynatrace_release_news()
            if isinstance(oneagent_result, JSONResponse):
                # Handle error case
                return oneagent_result
            response["oneagent"]["latestVersion"] = oneagent_result.get("oneAgentLatestVersion", "")
            response["oneagent"]["summary"] = oneagent_result.get("summary", "")
        
        # Process ActiveGate if selected
        if activegate_selected:
            activegate_result = await activegate_processor.process_dynatrace_release_news()
            if isinstance(activegate_result, JSONResponse):
                # Handle error case
                return activegate_result
            response["active-gate"]["latestVersion"] = activegate_result.get("activeGateLatestVersion", "")
            response["active-gate"]["summary"] = activegate_result.get("summary", "")
        
        # Process Dynatrace API if selected
        if dynatrace_api_selected:
            dynatrace_api_result = await dynatrace_api_processor.process_dynatrace_release_news()
            if isinstance(dynatrace_api_result, JSONResponse):
                # Handle error case
                return dynatrace_api_result
            response["dynatrace-api"]["latestVersion"] = dynatrace_api_result.get("dynatraceApiLatestVersion", "")
            response["dynatrace-api"]["summary"] = dynatrace_api_result.get("summary", "")
        
        # Process Dynatrace Operator if selected
        if dynatrace_operator_selected:
            dynatrace_operator_result = await dynatrace_operator_processor.process_dynatrace_release_news()
            if isinstance(dynatrace_operator_result, JSONResponse):
                # Handle error case
                return dynatrace_operator_result
            response["dynatrace-operator"]["latestVersion"] = dynatrace_operator_result.get("dynatraceOperatorLatestVersion", "")
            response["dynatrace-operator"]["summary"] = dynatrace_operator_result.get("summary", "")
        
        # Check if at least one component was selected
        if not oneagent_selected and not activegate_selected and not dynatrace_api_selected and not dynatrace_operator_selected:
            return JSONResponse(
                status_code=400, 
                content={"error": "No supported release notes selected. Please select OneAgent, ActiveGate, Dynatrace API, or Dynatrace Operator to proceed."}
            )
        
        return response
            
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Invalid request format: {str(e)}"})
