from crewai import Agent
from typing import Dict, Any
import os
import boto3
from dotenv import load_dotenv
from langchain.tools import Tool
from openai import OpenAI
import groq
from pydantic import BaseModel, Field
from src.config import settings  # Import settings

# Load environment variables
load_dotenv()

# Define the input schema for the tool using Pydantic

class PromptComparisonSchema(BaseModel):
    """Schema for model comparison input"""
    prompt: str = Field(
        description="The prompt to evaluate across different language models",
        example="Explain the concept of quantum computing in simple terms."
    )

def get_openai_response(prompt: str) -> str:
    """Get response from OpenAI's model"""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,  # Use from settings
        messages=[{"role": "user", "content": prompt}],
        max_tokens=settings.MAX_TOKENS  # Use from settings
    )
    return response.choices[0].message.content

def get_groq_response(prompt: str) -> str:
    """Get response from Groq"""
    client = groq.Groq(api_key=settings.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,  # Use from settings
        messages=[{"role": "user", "content": prompt}],
        max_tokens=settings.MAX_TOKENS  # Use from settings
    )
    return response.choices[0].message.content

def get_bedrock_response(prompt: str) -> str:
    """Get response from Claude LLM via AWS Bedrock"""
    bedrock = boto3.client('bedrock-runtime',
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                            region_name=settings.AWS_REGION_NAME)

    #input payload for the model
    request = {
        "anthropic_version":"bedrock-2023-05-31",
        "max_tokens": 1000 ,
        "messages":[
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }
    #convert the request to json
    request = json.dumps(request)

    #invoke the model with the request
    response = bedrock.invoke_model_with_response_stream(
        modelId=settings.CLAUDE_MODEL_ID,
        body=request
    )
    # Extract and print the response text in real-time
    response_text = ""
    for event in response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if chunk["type"] == "content_block_delta":
            response_text += chunk["delta"].get("text", "")
    return response_text

def compare_models(prompt: str) -> Dict[str, Any]:
    """
    Compare how different models handle the same prompt

    Args:
        prompt (str): The prompt to evaluate across models

    Returns:
        Dict[str, Any]: Comparison results including responses and analysis
    """
    if not prompt:
        return {
            "success": False,
            "error": "No prompt provided"
        }

    try:
        # Get responses from both models
        openai_resp = get_openai_response(prompt)
        groq_resp = get_groq_response(prompt)

        # Analyze responses
        analysis = {
            "length_comparison": {
                "openai": len(openai_resp),
                "groq": len(groq_resp)
            },
            "response_characteristics": {
                "openai": {
                    "word_count": len(openai_resp.split()),
                    "character_count": len(openai_resp)
                },
                "groq": {
                    "word_count": len(groq_resp.split()),
                    "character_count": len(groq_resp)
                },
                "bedrock": {
                    "word_count": len(bedrock_resp.split()),
                    "character_count": len(bedrock_resp)
                }
            }
        }

        return {
            "success": True,
            "responses": {
                "openai": openai_resp,
                "groq": groq_resp,
                "bedrock": bedrock_resp
            },
            "analysis": analysis
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Create the tool for model comparison
model_comparison_tool = Tool(
    name="compare_models",
    func=compare_models,
    description="""Compares responses from different LLM models (OpenAI and Groq)
    to analyze their interpretation and handling of the same prompt""",
    args_schema=PromptComparisonSchema
)

# Create the comparison agent
comparison_agent = Agent(
    role='Model Comparison Specialist',
    goal='Analyze and compare how different language models interpret and respond to prompts',
    backstory="""You are an expert in comparative analysis of language models.
    Your specialty is evaluating how different models interpret and respond to the same prompts,
    providing insights into their strengths, weaknesses, and unique characteristics.
    You help researchers and developers understand the nuances between different LLMs
    and their response patterns.""",
    tools=[model_comparison_tool],
    verbose=True
)
