# Dynatrace Operator release notes processing service for Dynatrace documentation

import logging
import openai
from fastapi.responses import JSONResponse
from .data_models import ComponentLatestReleaseVersion
from .prompts.dynatrace_operator_prompts import get_dynatrace_operator_summary_prompt, get_dynatrace_operator_version_prompt


logger = logging.getLogger(__name__)


class ProcessDynatraceOperatorReleaseNotes:
    """Service class for processing Dynatrace Operator release notes and version information"""
    
    def __init__(self, openai_client: openai.OpenAI):
        """Initialize with OpenAI client"""
        self.openai_client = openai_client

    async def process_dynatrace_release_news(self):
        """Main method to process Dynatrace Operator release news"""
        logger.info("Received request for Dynatrace Operator release news")
        
        dynatrace_operator_latest_version = await self._get_dynatrace_operator_latest_version()
        if "error" in dynatrace_operator_latest_version:
            return JSONResponse(status_code=500, content=dynatrace_operator_latest_version)

        summary_result = await self._get_dynatrace_operator_release_summary(dynatrace_operator_latest_version)
        if "error" in summary_result:
            return JSONResponse(status_code=500, content=summary_result)
        
        return {"summary": summary_result["summary"], "dynatraceOperatorLatestVersion": dynatrace_operator_latest_version}

    async def _get_dynatrace_operator_latest_version(self):
        """Get the latest Dynatrace Operator version"""
        return await self._dynatrace_operator_latest_version()

    async def _dynatrace_operator_latest_version(self) -> ComponentLatestReleaseVersion:
        """Fetch the latest Dynatrace Operator version from OpenAI"""
        if not self.openai_client:
            return {"error": "OpenAI API key not configured."}
        
        try:
            dynatrace_operator_version_prompt = get_dynatrace_operator_version_prompt()
            print(f"Sending prompt to OpenAI: {dynatrace_operator_version_prompt}")

            dynatrace_operator_version_response = self.openai_client.responses.parse(
                model="gpt-4o",  # Use gpt-4o instead of gpt-4.1
                input=dynatrace_operator_version_prompt,
                tools=[{"type": "web_search_preview"}],
                text_format=ComponentLatestReleaseVersion
            )
            result = dynatrace_operator_version_response.output_parsed
            if result is None:
                return {"error": "Failed to extract the latest Dynatrace Operator version."}
            
            print(f"Received response from OpenAI: {result}")
            return result.version
            
        except Exception as e:
            return {"error": str(e)}

    async def _get_dynatrace_operator_release_summary(self, version: str):
        """Get the summary for a given Dynatrace Operator version"""
        try:
            summary_prompt = get_dynatrace_operator_summary_prompt(version)
            print(f"Sending summary prompt to OpenAI: {summary_prompt}")
            
            summary_response = self.openai_client.responses.create(
                model="gpt-4o",  # Use gpt-4o instead of gpt-4.1 for better web access
                input=summary_prompt,
                tools=[{"type": "web_search_preview"}]
            )
            summary = summary_response.output_text
            print(f"Received summary from OpenAI: {summary}")
            
            if summary is None:
                return {"error": "Failed to get summary from OpenAI."}
                    
            return {"summary": summary}
        except Exception as e:
            return {"error": str(e)}
