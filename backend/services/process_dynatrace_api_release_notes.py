# Dynatrace API changelog processing service for Dynatrace documentation

import logging
import openai
from fastapi.responses import JSONResponse
from .data_models import ComponentLatestReleaseVersion, ComponentLatestReleaseSummary
from .prompts.dynatrace_api_prompts import get_dynatrace_api_summary_prompt, get_dynatrace_api_version_prompt


logger = logging.getLogger(__name__)


class ProcessDynatraceApiReleaseNotes:
    """Service class for processing Dynatrace API release notes and version information"""
    
    def __init__(self, openai_client: openai.OpenAI):
        """Initialize with OpenAI client"""
        self.openai_client = openai_client

    async def process_dynatrace_release_news(self):
        """Main method to process Dynatrace API release news"""
        logger.info("Received request for Dynatrace API release news")
        
        dynatrace_api_latest_version = await self._get_dynatrace_api_latest_version()
        if "error" in dynatrace_api_latest_version:
            return JSONResponse(status_code=500, content=dynatrace_api_latest_version)

        summary_result = await self._get_dynatrace_api_release_summary(dynatrace_api_latest_version)
        if "error" in summary_result:
            return JSONResponse(status_code=500, content=summary_result)
        
        return summary_result

    async def _get_dynatrace_api_latest_version(self):
        """Get the latest Dynatrace API version"""
        return await self._dynatrace_api_latest_version()

    async def _dynatrace_api_latest_version(self) -> ComponentLatestReleaseVersion:
        """Fetch the latest Dynatrace API version from OpenAI"""
        if not self.openai_client:
            return {"error": "OpenAI API key not configured."}
        
        try:
            dynatrace_api_version_prompt = get_dynatrace_api_version_prompt()
            print(f"Sending prompt to OpenAI: {dynatrace_api_version_prompt}")

            dynatrace_api_version_response = self.openai_client.responses.parse(
                model="gpt-4o",  # Use gpt-4o instead of gpt-4.1
                input=dynatrace_api_version_prompt,
                tools=[{"type": "web_search_preview"}],
                text_format=ComponentLatestReleaseVersion
            )
            result = dynatrace_api_version_response.output_parsed
            if result is None:
                return {"error": "Failed to extract the latest Dynatrace API version."}
            
            print(f"Received response from OpenAI: {result}")
            return result.version
            
        except Exception as e:
            return {"error": str(e)}

    async def _get_dynatrace_api_release_summary(self, version: str):
        """Get the summary for a given Dynatrace API version"""
        try:
            summary_prompt = get_dynatrace_api_summary_prompt(version)
            print(f"Sending summary prompt to OpenAI: {summary_prompt}")
            
            summary_response = self.openai_client.responses.parse(
                model="gpt-4o",  # Use gpt-4o instead of gpt-4.1 for better web access
                input=summary_prompt,
                tools=[{"type": "web_search_preview"}],
                text_format=ComponentLatestReleaseSummary
            )
            result = summary_response.output_parsed
            print(f"Received summary from OpenAI: {result}")
            
            if result is None:
                return {"error": "Failed to get summary from OpenAI."}
            
            # Ensure latestVersion is set
            result.latestVersion = version
            return result
                    
        except Exception as e:
            return {"error": str(e)}
