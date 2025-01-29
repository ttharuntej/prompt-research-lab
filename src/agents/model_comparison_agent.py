from crewai import Agent
from typing import Dict, Any
import os
from dotenv import load_dotenv
from langchain.tools import Tool
from openai import OpenAI
import groq
from pydantic import BaseModel, Field
from src.config import settings  # Import settings
from anthropic import Anthropic  # Add this import

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

def get_groq_llama_response(prompt: str) -> str:
    """Get response from Groq's Llama model"""
    client = groq.Groq(api_key=settings.GROQ_LLAMA_API_KEY)
    response = client.chat.completions.create(
        model=settings.GROQ_LLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=settings.MAX_TOKENS
    )
    return response.choices[0].message.content

def get_groq_mixtral_response(prompt: str) -> str:
    """Get response from Groq's Mixtral model"""
    client = groq.Groq(api_key=settings.GROQ_MIXTRAL_API_KEY)
    response = client.chat.completions.create(
        model=settings.GROQ_MIXTRAL_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=settings.MAX_TOKENS
    )
    return response.choices[0].message.content

def get_claude_response(prompt: str) -> str:
    """Get response from Anthropic's Claude"""
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=settings.CLAUDE_MODEL,  # We'll add this to settings
        messages=[{"role": "user", "content": prompt}],
        max_tokens=settings.MAX_TOKENS
    )
    return response.content[0].text

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
        # Get responses from all models
        openai_resp = get_openai_response(prompt)
        groq_llama_resp = get_groq_llama_response(prompt)
        groq_mixtral_resp = get_groq_mixtral_response(prompt)
        claude_resp = get_claude_response(prompt)
        
        # Analyze responses
        analysis = {
            "length_comparison": {
                "openai": len(openai_resp),
                "groq_llama": len(groq_llama_resp),
                "groq_mixtral": len(groq_mixtral_resp),
                "claude": len(claude_resp)
            },
            "response_characteristics": {
                "openai": {
                    "word_count": len(openai_resp.split()),
                    "character_count": len(openai_resp)
                },
                "groq_llama": {
                    "word_count": len(groq_llama_resp.split()),
                    "character_count": len(groq_llama_resp)
                },
                "groq_mixtral": {
                    "word_count": len(groq_mixtral_resp.split()),
                    "character_count": len(groq_mixtral_resp)
                },
                "claude": {
                    "word_count": len(claude_resp.split()),
                    "character_count": len(claude_resp)
                }
            }
        }
        
        return {
            "success": True,
            "responses": {
                "openai": openai_resp,
                "groq_llama": groq_llama_resp,
                "groq_mixtral": groq_mixtral_resp,
                "claude": claude_resp
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