import json
import os
from datetime import datetime
from crewai import Crew, Task
from dotenv import load_dotenv
from agents.model_comparison_agent import comparison_agent

# Configuration
BATCH_SIZE = 10  # Number of questions to process in one run
OUTPUT_FILE = "failed_comparisons.json"

def load_eval_data(limit=BATCH_SIZE):
    """Load evaluation data from JSON file"""
    with open('eval_data.json', 'r') as f:
        data = json.load(f)
        # Get questions up to limit
        return data['rows'][:limit]

def extract_answer(response):
    """Extract just the letter answer from model response
    Args:
        response: CrewOutput object containing the model's response
    Returns:
        str: Single letter (A, B, C, or D) or None if no valid answer found
    """
    if not hasattr(response, 'raw'):
        return None
        
    # Get the raw string response
    answer_text = response.raw
    
    # Validate and extract the answer
    if not answer_text:
        return None
        
    lines = answer_text.split('\n')
    for line in reversed(lines):
        if line.startswith('Answer:'):
            answer = line.strip()[-1].upper()  # Get last character and uppercase it
            # Validate it's one of the allowed options
            if answer in ['A', 'B', 'C', 'D']:
                return answer
    return None

def run_comparison():
    # Load environment variables
    load_dotenv()
    
    # Verify API keys
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    if not os.getenv('GROQ_API_KEY'):
        raise ValueError("GROQ_API_KEY not found in environment variables")

    # Load evaluation data
    eval_data = load_eval_data()
    failed_comparisons = []
    total = len(eval_data)
    passed = 0
    
    print(f"\nProcessing {total} questions...")
    
    for idx, row in enumerate(eval_data, 1):
        print(f"\nQuestion {idx}/{total}")
        question = row['row']['input_query']
        expected_answer = row['row']['expected_answer']
        
        # Create task for this question
        task = Task(
            description=question,
            agent=comparison_agent,
            expected_output="Answer in format: 'Answer: X' where X is A, B, C, or D"
        )

        # Create crew
        crew = Crew(
            agents=[comparison_agent],
            tasks=[task]
        )

        # Get model responses (remove debug prints)
        result = crew.kickoff()
        model_answer = extract_answer(result)
        
        # Compare answers
        if model_answer != expected_answer:
            print(f"❌ Question {idx}: Expected {expected_answer}, got {model_answer}")
            failed_comparisons.append({
                'timestamp': datetime.now().isoformat(),
                'question': question,
                'expected_answer': expected_answer,
                'model_response': result.raw,
                'model_answer': model_answer,
                'model_full_response': {
                    'openai': result.tasks_output[0].raw if result.tasks_output else None,
                    'groq': result.tasks_output[0].raw if result.tasks_output else None
                }
            })
        else:
            passed += 1
            print(f"✅ Question {idx}: Correct answer {expected_answer}")

    # Print summary
    print("\n=== Summary ===")
    print(f"Total questions: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")

    # Save failed comparisons
    if failed_comparisons:
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(failed_comparisons, f, indent=2)
        print(f"\nFailed comparisons saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_comparison() 