
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import os
from dotenv import load_dotenv

import openai
from pydantic import BaseModel
from .prompts import get_oneagent_summary_prompt, get_oneagent_version_prompt


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

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None



class ComponentLatestReleaseVersion(BaseModel):
    version: str



@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}


@app.post("/api/oneagent-release-news")
async def oneagent_release_news(request: Request):
    logger.info("Received request for OneAgent release news")
    one_agent_latest_version = await get_oneagent_latest_version()
    if "error" in one_agent_latest_version:
        return JSONResponse(status_code=500, content=one_agent_latest_version)

    summary_result = await get_oneagent_release_summary(one_agent_latest_version)
    if "error" in summary_result:
        return JSONResponse(status_code=500, content=summary_result)
    return {"summary": summary_result["summary"], "oneAgentLatestVersion": one_agent_latest_version}



# @app.post("/api/download-full-release-news")
# async def download_full_release_news(request: Request):
#     if not openai_client:
#         return JSONResponse(status_code=500, content={"error": "OpenAI API key not configured."})
#     try:
#         open_api_prompt = (
#             "open https://docs.dynatrace.com/managed/whats-new/oneagent;\n"
#             "search for the latest version in the 'version' table column; output that number only"
#         )
#         open_api_response = openai_client.responses.create(
#             model="gpt-4.1",
#             input=open_api_prompt,
#             tools=[{"type": "web_search_preview"}]
#         )
#         one_agent_latest_version = open_api_response.output_text.strip()

#         summary_prompt = (
#             f"Get the contents of the Dynatrace OneAgent release notes for version {one_agent_latest_version}"
#         )
#         summary_response = openai_client.chat.completions.create(
#             model="gpt-4.1",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": summary_prompt}
#             ]
#         )
#         summary = summary_response.choices[0].message.content
#         return {"summary": summary, "oneAgentLatestVersion": one_agent_latest_version}
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": str(e)})


# Helper function for internal use
async def get_oneagent_latest_version():
    return await oneagent_latest_version()


async def oneagent_latest_version() -> ComponentLatestReleaseVersion:
    if not openai_client:
        return {"error": "OpenAI API key not configured."}
    try:
        oneagent_version_prompt = get_oneagent_version_prompt()
        print(f"Sending prompt to OpenAI: {oneagent_version_prompt}")
        # open_api_completion = openai_client.beta.chat.completions.parse(
        #     model="gpt-4.1",
        #     messages=[
        #         {
        #             "role": "system",
        #             "content": "You are a helpful assistant that can access web pages and extract information.",
        #         },
        #         {"role": "user", "content": open_api_prompt},
        #     ],
        #     # tools=[{"type": "web_search_preview"}],


        oneagent_version_response= openai_client.responses.parse(
            model="gpt-4o",  # Use gpt-4o instead of gpt-4.1
            input=oneagent_version_prompt,
            tools=[{"type": "web_search_preview"}],
            text_format=ComponentLatestReleaseVersion
        )
        result = oneagent_version_response.output_parsed
        if result is None:
            return {"error": "Failed to extract the latest OneAgent version."}
        
        print(f"Received response from OpenAI: {result}")

        return result.version
        
        # one_agent_latest_version = result.version.strip()

        # return {"oneAgentLatestVersion": one_agent_latest_version}
    except Exception as e:
        return {"error": str(e)}



# Helper function for getting the summary for a given version
async def get_oneagent_release_summary(version: str):
    try:
        # Option 1: Use improved prompt with web_search_preview
        summary_prompt = get_oneagent_summary_prompt(version)
        print(f"Sending summary prompt to OpenAI: {summary_prompt}")
        
        summary_response = openai_client.responses.create(
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

