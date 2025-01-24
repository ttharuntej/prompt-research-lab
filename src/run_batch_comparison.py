import json
from datetime import datetime
from dotenv import load_dotenv
from crewai import Crew, Task
from agents.model_comparison_agent import comparison_agent
from config import settings

def load_eval_data(limit=settings.BATCH_SIZE):
    """Load evaluation data from JSON file"""
    with open('eval_data.json', 'r') as f:
        data = json.load(f)
        return data['rows'][:limit]

def extract_answer(text):
    import re
    
    # Clean the text
    text = text.lower()
    text = re.sub(r'\*|\-|•|\n+', ' ', text)
    
    # Find the last answer for each model
    def find_last_answer(model):
        pattern = f"{model}.*?answer:\\s*([a-d])"
        matches = re.findall(pattern, text)
        return matches[-1].upper() if matches else None
    
    openai = find_last_answer('openai')
    groq = find_last_answer('groq')
    
    return openai, groq

# def extract_answer(text):
    """Extract OpenAI and Groq answers from the response text.
    Returns a tuple of (openai_answer, groq_answer)"""
    # Split into OpenAI and Groq parts
    parts = text.split('Groq')
    if len(parts) != 2:
        parts = text.split('groq')  # Try lowercase if first split fails
        if len(parts) != 2:
            raise ValueError("Could not separate OpenAI and Groq responses")
    
    def get_letter(text):
        if 'Answer:' not in text:
            return None
        after_answer = text.split('Answer:')[1].strip()
        return after_answer[0].upper()
    
    openai_answer = get_letter(parts[0])
    groq_answer = get_letter(parts[1])
    
    if not openai_answer or not groq_answer:
        raise ValueError("Could not extract answers in expected format")
    
    return openai_answer, groq_answer

def create_comparison_task(question: str) -> Task:
    """Create a task with proper prompt engineering"""
    enhanced_prompt = f"""
    Compare how OpenAI and Groq respond to this multiple choice question.
    
    IMPORTANT INSTRUCTIONS:
    1. Use the compare_models tool to get responses from both models
    2. Each model must analyze the question and provide their answer
    3. Each model's response MUST include 'Answer: X' where X is A, B, C, or D
    4. Models can provide explanations, but 'Answer: X' must be present 
    5. The answer should be a single letter (A, B, C, or D)
    
    Here is the question to analyze:
    {question}
    """
    
    return Task(
        description=enhanced_prompt,
        agent=comparison_agent,
        expected_output="Comparison of model responses, each including 'Answer: X' format"
    )

def create_failure_record(question: str, expected_answer: str, openai_answer=None, groq_answer=None, error=None):
    """Create a standardized failure record for both error cases and answer mismatches"""
    record = {
        'timestamp': datetime.now().isoformat(),
        'question': question,
        'expected_answer': expected_answer,
    }
    
    if error:
        record['error'] = str(error)
    else:
        models_failed = []
        if openai_answer is None:
            models_failed.append('openai')
        if groq_answer is None:
            models_failed.append('groq')
            
        record['model_responses'] = {
            'openai': {
                'answer': openai_answer,
                'failed': 'openai' in models_failed
            },
            'groq': {
                'answer': groq_answer,
                'failed': 'groq' in models_failed
            }
        }
        record['models_failed'] = models_failed
        
    return record

def check_model_answers(openai_answer: str, groq_answer: str, expected_answer: str) -> tuple[bool, str]:
    """Check if model answers match expected answer and generate appropriate message.
    Returns (is_correct, message)"""
    if None in (openai_answer, groq_answer):
        return False, "❌ One or more models failed to provide an answer"
        
    if openai_answer != expected_answer or groq_answer != expected_answer:
        return False, f"\n❌ Answers differ from expected:\nExpected: {expected_answer}\nOpenAI: {openai_answer}\nGroq: {groq_answer}"
        
    return True, f"✅ Both models correct with answer {expected_answer}"

def run_comparison():
    # Load environment variables and verify API keys
    load_dotenv()
    if not settings.OPENAI_API_KEY or not settings.GROQ_API_KEY:
        raise ValueError("Missing API keys in environment variables")

    # 1. Load evaluation data
    eval_data = load_eval_data()
    failed_comparisons = []
    total = len(eval_data)
    passed = 0
    
    print(f"\nProcessing {total} questions...")
    
    for idx, row in enumerate(eval_data, 1):
        question = row['row']['input_query']
        expected_answer = row['row']['expected_answer']
        
        print(f"\n{'='*50}")
        print(f"Question {idx}/{total}")
        print(f"Question text: {question}")
        print(f"Expected answer: {expected_answer}")
        print(f"{'='*50}")
        
        try:
            task = create_comparison_task(question)
            crew = Crew(agents=[comparison_agent], tasks=[task])
            result = crew.kickoff() 
            raw_output = result.tasks_output[0].raw
            print("\n📝 Model Responses:")
            print(raw_output)
            
            # Write raw model responses to file
            with open('model_responses.txt', 'a') as f:
                f.write(raw_output)
                f.write("\n")
            
            openai_answer, groq_answer = extract_answer(raw_output)
            print("OpenAI Answer:", openai_answer)
            print("Groq Answer:", groq_answer)
            
            is_correct, message = check_model_answers(openai_answer, groq_answer, expected_answer)
            print(message)
            
            if not is_correct:
                failed_comparisons.append(
                    create_failure_record(question, expected_answer, openai_answer, groq_answer)
                )
            else:
                passed += 1
                
        except Exception as e:
            print(f"❌ Error processing question: {str(e)}")
            failed_comparisons.append(
                create_failure_record(question, expected_answer, error=e)
            )

    # Print summary and save results
    print("\n=== Summary ===")
    print(f"Total questions: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")

    if failed_comparisons:
        with open(settings.OUTPUT_FILE, 'w') as f:
            json.dump(failed_comparisons, f, indent=2)
        print(f"\nFailed comparisons saved to {settings.OUTPUT_FILE}")

if __name__ == "__main__":
    run_comparison() 