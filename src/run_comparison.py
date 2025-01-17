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
    
  # Create task with input/output format
    task = Task(
        description=(
            "Compare how OpenAI and Groq handle this prompt: {prompt}."
            " Provide a comparison analysis including response content and quality metrics."
        ),
        agent=comparison_agent,
        expected_output=(
            "A comparison analysis between OpenAI and Groq responses, "
            "including response content and quality metrics."
        )
    )

    # Create crew
    crew = Crew(
        agents=[comparison_agent],
        tasks=[task]
    )

    # Execute with dynamic input
    result = crew.kickoff(inputs={'prompt': 'Explain the concept of prompt engineering in three paragraphs.'})
 
    print("\nTest Results:")
    print("=============")
    print(result)

if __name__ == "__main__":
    main()