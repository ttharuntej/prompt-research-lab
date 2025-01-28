import json
from collections import Counter
from src.config import settings  # Add this import

def generate_executive_summary(data: list) -> str:
    """Generate executive summary from comparison results"""
    
    # Get model names from config
    openai_model = settings.OPENAI_MODEL
    groq_model = settings.GROQ_MODEL
    
    # Initialize counters
    total_questions = len(data)
    original_stats = {
        'openai_correct': 0,
        'groq_correct': 0,
        'both_correct': 0
    }
    misspelled_stats = {
        'openai_correct': 0,
        'groq_correct': 0,
        'both_correct': 0
    }
    
    outcomes = {
        'original': Counter(),
        'misspelled': Counter()
    }
    
    # Analyze data
    for record in data:
        # Original text performance
        orig = record['results']['original']
        outcomes['original'][orig['comparison_result']['outcome']] += 1
        
        # Misspelled text performance
        misp = record['results']['misspelled']
        outcomes['misspelled'][misp['comparison_result']['outcome']] += 1
    
    # Updated summary with model names
    summary = f"""
Executive Summary: Model Comparison Analysis
==========================================
Models Compared: {openai_model} vs {groq_model}
Sample Size: {total_questions} questions

Original Text Performance
------------------------
- Both models correct: {outcomes['original']['BOTH_CORRECT']} ({outcomes['original']['BOTH_CORRECT']/total_questions*100:.1f}%)
- {openai_model} only correct: {outcomes['original']['OPENAI_ONLY_CORRECT']} ({outcomes['original']['OPENAI_ONLY_CORRECT']/total_questions*100:.1f}%)
- {groq_model} only correct: {outcomes['original']['GROQ_ONLY_CORRECT']} ({outcomes['original']['GROQ_ONLY_CORRECT']/total_questions*100:.1f}%)
- Both incorrect: {outcomes['original']['BOTH_INCORRECT']} ({outcomes['original']['BOTH_INCORRECT']/total_questions*100:.1f}%)

Misspelled Text Performance
--------------------------
- Both models correct: {outcomes['misspelled']['BOTH_CORRECT']} ({outcomes['misspelled']['BOTH_CORRECT']/total_questions*100:.1f}%)
- {openai_model} only correct: {outcomes['misspelled']['OPENAI_ONLY_CORRECT']} ({outcomes['misspelled']['OPENAI_ONLY_CORRECT']/total_questions*100:.1f}%)
- {groq_model} only correct: {outcomes['misspelled']['GROQ_ONLY_CORRECT']} ({outcomes['misspelled']['GROQ_ONLY_CORRECT']/total_questions*100:.1f}%)
- Both incorrect: {outcomes['misspelled']['BOTH_INCORRECT']} ({outcomes['misspelled']['BOTH_INCORRECT']/total_questions*100:.1f}%)

Key Findings
-----------
1. Model Performance: {get_performance_insight(outcomes, total_questions, openai_model, groq_model)}
2. Robustness: {get_robustness_insight(outcomes, total_questions, openai_model, groq_model)}
3. Reliability: {get_reliability_insight(outcomes, total_questions, openai_model, groq_model)}
"""
    return summary

def get_performance_insight(outcomes, total, openai_model, groq_model):
    orig_both_correct = outcomes['original']['BOTH_CORRECT']/total*100
    misp_both_correct = outcomes['misspelled']['BOTH_CORRECT']/total*100
    return f"On original text, both models ({openai_model} and {groq_model}) achieved {orig_both_correct:.1f}% accuracy together, while on misspelled text this dropped to {misp_both_correct:.1f}%"

def get_robustness_insight(outcomes, total, openai_model, groq_model):
    groq_misp_correct = (outcomes['misspelled']['GROQ_ONLY_CORRECT'] + outcomes['misspelled']['BOTH_CORRECT'])/total*100
    openai_misp_correct = (outcomes['misspelled']['OPENAI_ONLY_CORRECT'] + outcomes['misspelled']['BOTH_CORRECT'])/total*100
    return f"{groq_model} showed {groq_misp_correct:.1f}% accuracy on misspelled text vs {openai_model}'s {openai_misp_correct:.1f}%"

def get_reliability_insight(outcomes, total, openai_model, groq_model):
    groq_fails = outcomes['misspelled']['NEITHER_ANSWERED']
    openai_fails = outcomes['misspelled']['NEITHER_ANSWERED']
    if groq_fails > openai_fails:
        return f"{openai_model} showed higher reliability with fewer failed responses"
    elif openai_fails > groq_fails:
        return f"{groq_model} showed higher reliability with fewer failed responses"
    else:
        return f"Both models showed similar reliability in terms of response completion"

if __name__ == "__main__":
    with open('model_comparison_results.json', 'r') as f:
        data = json.load(f)
    print(generate_executive_summary(data)) 