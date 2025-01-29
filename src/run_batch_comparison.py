import json
from datetime import datetime
from dotenv import load_dotenv
from crewai import Crew, Task
from agents.model_comparison_agent import comparison_agent
from agents.model_misspelling_stability import MisspellingGenerator
from config import settings
from schemas.comparison_schema import (
    ComparisonRecord, ComparisonOutcome, QuestionPair,
    MisspellingInfo, TestResults, ModelResponse, ModelDetail,
    ComparisonResult
)
import ijson  # Add to requirements.txt

def load_eval_data(batch_size=settings.BATCH_SIZE, total_limit=None):
    """Stream evaluation data from JSON file in batches
    
    Args:
        batch_size: Number of items to process in each batch
        total_limit: Maximum total items to process (None for all)
    """
    current_batch = []
    total_processed = 0
    
    with open('eval_data.json', 'rb') as f:
        parser = ijson.items(f, 'rows.item')
        
        for row in parser:
            if total_limit and total_processed >= total_limit:
                # Yield remaining items in batch before stopping
                if current_batch:
                    yield current_batch
                break
                
            current_batch.append(row)
            total_processed += 1
            
            if len(current_batch) == batch_size:
                yield current_batch
                current_batch = []
    
    # Yield any remaining items
    if current_batch:
        yield current_batch

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
    claude = find_last_answer('claude')
    
    return openai, groq, claude

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
    Compare how OpenAI, Groq, and Claude respond to this multiple choice question.
    
    IMPORTANT INSTRUCTIONS:
    1. Use the compare_models tool to get responses from all three models
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

def create_failure_record(question: str, expected_answer: str, 
                         openai_answer=None, groq_answer=None, claude_answer=None,  # Add Claude
                         error=None, is_misspelled=False):
    """Create a standardized failure record"""
    record = {
        'timestamp': datetime.now().isoformat(),
        'question': question,
        'expected_answer': expected_answer,
        'is_misspelled': is_misspelled,
    }
    
    if error:
        record['error'] = str(error)
    else:
        models_failed = []
        if openai_answer is None: models_failed.append('openai')
        if groq_answer is None: models_failed.append('groq')
        if claude_answer is None: models_failed.append('claude')  
            
        record['model_responses'] = {
            'openai': {'answer': openai_answer, 'failed': 'openai' in models_failed},
            'groq': {'answer': groq_answer, 'failed': 'groq' in models_failed},
            'claude': {'answer': claude_answer, 'failed': 'claude' in models_failed}  
        }
        record['models_failed'] = models_failed
    
    return record

def check_model_answers(openai_answer: str, groq_answer: str, claude_answer: str, 
                       expected_answer: str) -> tuple[bool, str]:
    """Check if model answers match expected answer"""
    if None in (openai_answer, groq_answer, claude_answer):
        return False, "❌ One or more models failed to provide an answer"
        
    answers = {
        'OpenAI': openai_answer,
        'Groq': groq_answer,
        'Claude': claude_answer
    }
    incorrect = [name for name, ans in answers.items() if ans != expected_answer]
    
    if incorrect:
        msg = f"\n❌ Incorrect answers from: {', '.join(incorrect)}\n"
        msg += f"Expected: {expected_answer}\n"
        msg += "\n".join(f"{name}: {ans}" for name, ans in answers.items())
        return False, msg
        
    return True, f"✅ All models correct with answer {expected_answer}"

def determine_outcome(model_responses: dict, expected_answer: str) -> ComparisonOutcome:
    """Determine the comparison outcome based on model performances"""
    # Count correct and answered
    total_models = len(model_responses)
    correct_count = sum(1 for resp in model_responses.values() 
                       if resp.answer == expected_answer)
    answered_count = sum(1 for resp in model_responses.values() 
                        if resp.answer is not None)
    
    if answered_count == 0:
        return ComparisonOutcome.NONE_ANSWERED
    elif correct_count == total_models:
        return ComparisonOutcome.ALL_CORRECT
    elif correct_count == 0:
        return ComparisonOutcome.ALL_INCORRECT
    else:
        return ComparisonOutcome.MIXED_RESULTS

def create_comparison_record(row_idx: int, original_q: str, misspelled_q: str, 
                           expected_answer: str, 
                           original_results: dict, misspelled_results: dict,
                           misspelling_info: dict) -> ComparisonRecord:
    """Create a structured comparison record"""
    
    def create_test_results(results: dict) -> TestResults:
        model_responses = {
            "openai": ModelResponse(
                answer=results.get('openai_answer'),
                failed=results.get('openai_answer') is None,
                model_name=settings.OPENAI_MODEL,
                is_correct=results.get('openai_answer') == expected_answer
            ),
            "groq": ModelResponse(
                answer=results.get('groq_answer'),
                failed=results.get('groq_answer') is None,
                model_name=settings.GROQ_MODEL,
                is_correct=results.get('groq_answer') == expected_answer
            ),
            "claude": ModelResponse(  # Add Claude
                answer=results.get('claude_answer'),
                failed=results.get('claude_answer') is None,
                model_name=settings.CLAUDE_MODEL,
                is_correct=results.get('claude_answer') == expected_answer
            )
        }
        
        # Create comparison result
        comparison_result = ComparisonResult(
            models_agree=len(set(r.answer for r in model_responses.values() if r.answer is not None)) == 1,
            outcome=determine_outcome(model_responses, expected_answer),
            details={
                "openai": ModelDetail(
                    is_correct=model_responses["openai"].is_correct,
                    provided_answer=model_responses["openai"].answer is not None
                ),
                "groq": ModelDetail(
                    is_correct=model_responses["groq"].is_correct,
                    provided_answer=model_responses["groq"].answer is not None
                ),
                "claude": ModelDetail(
                    is_correct=model_responses["claude"].is_correct,
                    provided_answer=model_responses["claude"].answer is not None
                )
            }
        )
        
        return TestResults(
            model_responses=model_responses,
            comparison_result=comparison_result
        )
    
    return ComparisonRecord(
        timestamp=datetime.now().isoformat(),
        row_idx=row_idx,
        question_pair=QuestionPair(
            text={
                "original": original_q,
                "misspelled": misspelled_q
            },
            expected_answer=expected_answer
        ),
        misspelling_info=MisspellingInfo(
            char_change_count=misspelling_info["char_change_count"],
            severity=misspelling_info["severity"]
        ),
        results={
            "original": create_test_results(original_results),
            "misspelled": create_test_results(misspelled_results)
        }
    )

def run_model_comparison(question: str) -> dict:
    """Run comparison between models and return their answers"""
    try:
        task = create_comparison_task(question)
        crew = Crew(agents=[comparison_agent], tasks=[task])
        result = crew.kickoff()
        raw_output = result.tasks_output[0].raw
        
        openai_answer, groq_answer, claude_answer = extract_answer(raw_output)
        return {
            'openai_answer': openai_answer,
            'groq_answer': groq_answer,
            'claude_answer': claude_answer
        }
    except Exception as e:
        print(f"❌ Error in comparison: {str(e)}")
        return {
            'openai_answer': None,
            'groq_answer': None,
            'claude_answer': None
        }

def run_comparison():
    # Load environment variables and verify API keys
    load_dotenv()
    if not settings.OPENAI_API_KEY or not settings.GROQ_API_KEY:
        raise ValueError("Missing API keys in environment variables")

    # Initialize misspelling generator
    misspelling_gen = MisspellingGenerator()
    
    # Load evaluation data
    eval_data = load_eval_data(
        batch_size=settings.BATCH_SIZE,
        total_limit=settings.TOTAL_ITEMS
    )
    comparison_records = []
    
    print("\nProcessing questions...")
    processed_count = 0
    
    for batch in eval_data:
        for row in batch:
            processed_count += 1
            print(f"Processing question {processed_count}...", end='\r')
            
            row_idx = row['row_idx']
            question = row['row']['input_query']
            expected_answer = row['row']['expected_answer']
            
            # Generate misspelled variant
            misspelled_question, char_changes = misspelling_gen.generate_variant(
                question,
                severity=settings.MISSPELLING_SEVERITY,
                return_changes=True
            )
            
            # Test both variants
            original_results = run_model_comparison(question)
            misspelled_results = run_model_comparison(misspelled_question)
            
            # Create record
            record = create_comparison_record(
                row_idx=row_idx,
                original_q=question,
                misspelled_q=misspelled_question,
                expected_answer=expected_answer,
                original_results=original_results,
                misspelled_results=misspelled_results,
                misspelling_info={
                    "char_change_count": char_changes,
                    "severity": settings.MISSPELLING_SEVERITY
                }
            )
            
            comparison_records.append(record.model_dump(mode='json'))
            
        # Save after each batch
        save_results(comparison_records)
    
    print(f"\nCompleted processing {processed_count} questions")
    print(f"Results saved to {settings.OUTPUT_FILE}")

def save_results(records: list):
    """Save comparison records to output file"""
    with open(settings.OUTPUT_FILE, 'w') as f:
        json.dump(records, f, indent=2)

if __name__ == "__main__":
    run_comparison() 