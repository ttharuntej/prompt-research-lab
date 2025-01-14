# src/test_setup.py
from crewai import Crew, Task
from dotenv import load_dotenv
import os
from agents.model_comparison_agent import comparison_agent

def main():
    # Load and verify environment variables
    load_dotenv()
    
    # Verify API keys
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    if not os.getenv('GROQ_API_KEY'):
        raise ValueError("GROQ_API_KEY not found in environment variables")
    
    # Create task with  input/output format
    task = Task(
        description="Compare how OpenAI and Groq handle this prompt",
        agent=comparison_agent,
        # Pass the prompt directly as a string
        input="Explain the concept of prompt engineering in three paragraphs.",
        expected_output="""A comparison analysis between OpenAI and Groq responses, 
        including response content and quality metrics."""  # Added this required field
    )
    
    # Create crew
    crew = Crew(
        agents=[comparison_agent],
        tasks=[task]
    )
    
    # Execute
    result = crew.kickoff()
    
    print("\nTest Results:")
    print("=============")
    print(result)

if __name__ == "__main__":
    main()