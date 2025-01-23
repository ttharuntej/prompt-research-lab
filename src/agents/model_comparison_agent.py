from crewai import Agent
from typing import Dict, Any
import os
from dotenv import load_dotenv
from langchain.tools import Tool
from openai import OpenAI
import groq
from pydantic import BaseModel, Field

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
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content

def get_groq_response(prompt: str) -> str:
    """Get response from Groq"""
    client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content

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
                }
            }
        }
        
        return {
            "success": True,
            "responses": {
                "openai": openai_resp,
                "groq": groq_resp
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
    # verbose=True
)