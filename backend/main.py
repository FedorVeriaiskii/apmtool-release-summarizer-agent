
# FastAPI backend for Dynatrace Release Notes Summarizer Agent
# Provides REST API endpoints for processing and summarizing Dynatrace release notes

# --------------------------------------------------------------
# Import dependencies and setup modules
# --------------------------------------------------------------

import sys
import os
# Add the current directory to Python path to find local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from io import BytesIO
import re
from datetime import datetime

from dotenv import load_dotenv

import openai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from services.data_models import ComponentLatestReleaseVersion, ComponentLatestReleaseSummary
from services.process_oneagent_release_notes import ProcessOneAgentReleaseNotes
from services.process_activegate_release_notes import ProcessActiveGateReleaseNotes
from services.process_dynatrace_api_release_notes import ProcessDynatraceApiReleaseNotes
from services.process_dynatrace_operator_release_notes import ProcessDynatraceOperatorReleaseNotes
from services.process_dynatrace_managed_release_notes import ProcessDynatraceManagedReleaseNotes

# --------------------------------------------------------------
# Initialize application configuration and logging
# --------------------------------------------------------------

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------
# Create FastAPI app instance and configure CORS
# --------------------------------------------------------------

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------
# Initialize OpenAI client and component processors
# --------------------------------------------------------------

# Initialize OpenAI client and processors
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None

# Initialize the release notes processors
oneagent_processor = ProcessOneAgentReleaseNotes(openai_client)
activegate_processor = ProcessActiveGateReleaseNotes(openai_client)
dynatrace_api_processor = ProcessDynatraceApiReleaseNotes(openai_client)
dynatrace_operator_processor = ProcessDynatraceOperatorReleaseNotes(openai_client)
dynatrace_managed_processor = ProcessDynatraceManagedReleaseNotes(openai_client)

# --------------------------------------------------------------
# Define helper functions for request processing
# --------------------------------------------------------------


def generate_pdf_content(release_summaries: dict) -> BytesIO:
    """Generate PDF content from release summaries"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        textColor='#1496FF'
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor='#1a3a6b'
    )
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=8,
        textColor='#1496FF'
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=6,
        spaceAfter=6,
        leftIndent=20
    )
    
    # Build story content
    story = []
    
    # Add title
    title = Paragraph("Dynatrace Release Notes Summary", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Add generation date
    date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}"
    story.append(Paragraph(date_text, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Process each component
    for component_key, component_data in release_summaries.items():
        if component_data.get('latestVersion'):
            # Component title with version
            component_name = component_key.replace('-', ' ').replace('_', ' ').title()
            if component_name == "Dynatrace Api":
                component_name = "Dynatrace API"
            
            component_title = f"{component_name} - Version {component_data['latestVersion']}"
            story.append(Paragraph(component_title, heading_style))
            story.append(Spacer(1, 15))
            
            # Add sections
            sections = [
                ('Breaking Changes', component_data.get('breaking_changes', '')),
                ('Announcements', component_data.get('announcements', '')),
                ('New Features', component_data.get('new_features', '')),
                ('Technology Support', component_data.get('technology_support', '')),
                ('Resolved Issues', component_data.get('resolved_issues', ''))
            ]
            
            for section_title, section_content in sections:
                if section_content and section_content.strip():
                    story.append(Paragraph(section_title, section_style))
                    
                    # Clean and format content
                    clean_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', section_content)
                    clean_content = clean_content.replace('\n\n', '<br/><br/>')
                    clean_content = clean_content.replace('\n', '<br/>')
                    
                    story.append(Paragraph(clean_content, normal_style))
                    story.append(Spacer(1, 10))
            
            story.append(Spacer(1, 30))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_pdf_from_release_news(release_news: list) -> BytesIO:
    """Generate PDF content from frontend releaseNews array format"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        textColor='#1496FF'
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor='#1a3a6b'
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=6,
        spaceAfter=6,
        leftIndent=20
    )
    
    # Build story content
    story = []
    
    # Add title
    title = Paragraph("Dynatrace Release Notes Summary", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Add generation date
    date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}"
    story.append(Paragraph(date_text, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Process each release news item
    for item in release_news:
        component = item.get('component', '')
        version = item.get('version', '')
        summary = item.get('summary', '')
        
        # Skip error components
        if component in ['Error', 'Info']:
            continue
        
        # Component title with version
        component_title = f"{component}"
        if version:
            component_title += f" - Version {version}"
            
        story.append(Paragraph(component_title, heading_style))
        story.append(Spacer(1, 15))
        
        # Clean and format summary content
        if summary:
            # Remove emoji and markdown formatting for PDF
            clean_content = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF🚨📢✨🔧🐛]', '', summary)
            clean_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_content)
            clean_content = clean_content.replace('\n\n', '<br/><br/>')
            clean_content = clean_content.replace('\n', '<br/>')
            
            story.append(Paragraph(clean_content, normal_style))
            story.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"message": "Hello from FastAPI!"}


async def process_selected_components(selected_items: list) -> dict:
    """Process selected Dynatrace components and return structured response"""
    
    # --------------------------------------------------------------
    # Step 1: Parse selected components from request
    # --------------------------------------------------------------
    
    # Check which components are selected
    oneagent_selected = False
    activegate_selected = False
    dynatrace_api_selected = False
    dynatrace_operator_selected = False
    dynatrace_managed_selected = False
    
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
            elif "dynatrace_managed" in item:
                dynatrace_managed_selected = True
    
    # --------------------------------------------------------------
    # Step 2: Initialize structured response template
    # --------------------------------------------------------------
    
    # Initialize response object
    response = {
        "oneagent": {
            "latestVersion": "",
            "breaking_changes": "",
            "announcements": "",
            "technology_support": "",
            "new_features": "",
            "resolved_issues": ""
        },
        "active-gate": {
            "latestVersion": "",
            "breaking_changes": "",
            "announcements": "",
            "technology_support": "",
            "new_features": "",
            "resolved_issues": ""
        },
        "dynatrace-api": {
            "latestVersion": "",
            "breaking_changes": "",
            "announcements": "",
            "technology_support": "",
            "new_features": "",
            "resolved_issues": ""
        },
        "dynatrace-operator": {
            "latestVersion": "",
            "breaking_changes": "",
            "announcements": "",
            "technology_support": "",
            "new_features": "",
            "resolved_issues": ""
        },
        "dynatrace-managed": {
            "latestVersion": "",
            "breaking_changes": "",
            "announcements": "",
            "technology_support": "",
            "new_features": "",
            "resolved_issues": ""
        }
    }

    # --------------------------------------------------------------
    # Step 3: Prepare tasks for parallel execution
    # --------------------------------------------------------------

    # Prepare tasks for parallel execution
    tasks = []
    task_mapping = []
    
    if oneagent_selected:
        tasks.append(oneagent_processor.process_dynatrace_release_news())
        task_mapping.append(("oneagent", "oneAgentLatestVersion"))
    
    if activegate_selected:
        tasks.append(activegate_processor.process_dynatrace_release_news())
        task_mapping.append(("active-gate", "activeGateLatestVersion"))
    
    if dynatrace_api_selected:
        tasks.append(dynatrace_api_processor.process_dynatrace_release_news())
        task_mapping.append(("dynatrace-api", "dynatraceApiLatestVersion"))
    
    if dynatrace_operator_selected:
        tasks.append(dynatrace_operator_processor.process_dynatrace_release_news())
        task_mapping.append(("dynatrace-operator", "dynatraceOperatorLatestVersion"))
    
    if dynatrace_managed_selected:
        tasks.append(dynatrace_managed_processor.process_dynatrace_release_news())
        task_mapping.append(("dynatrace-managed", "dynatraceManagedLatestVersion"))
    
    # --------------------------------------------------------------
    # Step 4: Execute processors in parallel and handle results
    # --------------------------------------------------------------
    
    # Execute all selected processors in parallel
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            component_key, version_key = task_mapping[i]
            
            # Check if result is an exception
            if isinstance(result, Exception):
                return {"error": f"Error processing {component_key}: {str(result)}", "status_code": 500}
            
            # Check if result is a JSONResponse (error case)
            if isinstance(result, JSONResponse):
                return {"error": "Processing error occurred", "status_code": 500}
            
            # Update response with successful result from ComponentLatestReleaseSummary
            if isinstance(result, ComponentLatestReleaseSummary):
                response[component_key]["latestVersion"] = result.latestVersion
                response[component_key]["breaking_changes"] = result.breaking_changes
                response[component_key]["announcements"] = result.announcements
                response[component_key]["technology_support"] = result.technology_support
                response[component_key]["new_features"] = result.new_features
                response[component_key]["resolved_issues"] = result.resolved_issues
    
    # --------------------------------------------------------------
    # Step 5: Validate selection and return response
    # --------------------------------------------------------------
    
    # Check if at least one component was selected
    if not oneagent_selected and not activegate_selected and not dynatrace_api_selected and not dynatrace_operator_selected and not dynatrace_managed_selected:
        return {"error": "No supported release notes selected. Please select OneAgent, ActiveGate, Dynatrace API, Dynatrace Operator, or Dynatrace Managed to proceed.", "status_code": 400}
    
    return response

# --------------------------------------------------------------
# Define API endpoints
# --------------------------------------------------------------


@app.post("/api/dynatrace-release-news-summary")
async def build_dynatrace_release_news_summary(request: Request):
    """Main endpoint to generate Dynatrace release news summary"""
    
    # --------------------------------------------------------------
    # Parse and validate request body
    # --------------------------------------------------------------
    
    # Parse request body to check for selectedItems
    try:
        request_body = await request.json()
        selected_items = request_body.get("selectedItems", [])
        
        # --------------------------------------------------------------
        # Process selected components and handle response
        # --------------------------------------------------------------
        
        # Process selected components
        result = await process_selected_components(selected_items)
        
        # Check if there was an error in processing
        if "error" in result:
            return JSONResponse(
                status_code=result.get("status_code", 500),
                content={"error": result["error"]}
            )
        
        return result
            
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Invalid request format: {str(e)}"})


@app.post("/api/download-release-news-pdf")
async def download_release_news_pdf(request: Request):
    """Endpoint to download release news as PDF from frontend releaseNews data"""
    
    # --------------------------------------------------------------
    # Parse request and generate PDF from releaseNews data
    # --------------------------------------------------------------
    
    try:
        request_body = await request.json()
        release_news = request_body.get("releaseNews", [])
        
        # Validate that we have release news data
        if not release_news or len(release_news) == 0:
            return JSONResponse(
                status_code=400,
                content={"error": "No release news data provided"}
            )
        
        # Filter out error/info components
        valid_release_news = [
            item for item in release_news 
            if item.get('component') not in ['Error', 'Info'] and item.get('summary', '').strip()
        ]
        
        if not valid_release_news:
            return JSONResponse(
                status_code=400,
                content={"error": "No valid release data available to generate PDF"}
            )
        
        # Generate PDF from release news data
        pdf_buffer = generate_pdf_from_release_news(valid_release_news)
        
        # Generate filename with current date
        filename = f"Dynatrace_Release_Notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Return PDF as streaming response
        return StreamingResponse(
            BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"PDF generation failed: {str(e)}"})
