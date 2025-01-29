import json
from collections import Counter
from src.config import settings  # Add this import
from typing import List, Dict

def generate_executive_summary(data: List[Dict]) -> str:
    """Generate executive summary of model comparison results"""
    
    # Initialize counters
    total_samples = len(data)
    stats = {
        'original': {
            'ALL_CORRECT': 0,
            'ALL_INCORRECT': 0,
            'MIXED_RESULTS': 0,
            'NONE_ANSWERED': 0,
            'model_correct': {'openai': 0, 'groq': 0, 'claude': 0}
        },
        'misspelled': {
            'ALL_CORRECT': 0,
            'ALL_INCORRECT': 0,
            'MIXED_RESULTS': 0,
            'NONE_ANSWERED': 0,
            'model_correct': {'openai': 0, 'groq': 0, 'claude': 0}
        }
    }
    
    # Process data
    for record in data:
        # Get model details for display
        model_details = record['model_details']
        
        # Process original text results
        orig = record['results']['original']
        orig_outcome = orig['comparison_result']['outcome']
        stats['original'][orig_outcome] += 1
        
        # Count individual model performance
        for model in ['openai', 'groq', 'claude']:
            if orig['model_responses'][model]['is_correct']:
                stats['original']['model_correct'][model] += 1
        
        # Process misspelled text results
        misp = record['results']['misspelled']
        misp_outcome = misp['comparison_result']['outcome']
        stats['misspelled'][misp_outcome] += 1
        
        # Count individual model performance
        for model in ['openai', 'groq', 'claude']:
            if misp['model_responses'][model]['is_correct']:
                stats['misspelled']['model_correct'][model] += 1
    
    # Generate summary text
    summary = f"""Executive Summary: Model Comparison Analysis
==========================================
Models Compared: {model_details['openai']} vs {model_details['groq']} vs {model_details['claude']}
Sample Size: {total_samples} questions

Original Text Performance
------------------------
- All models correct: {stats['original']['ALL_CORRECT']} ({stats['original']['ALL_CORRECT']/total_samples*100:.1f}%)
- Mixed results: {stats['original']['MIXED_RESULTS']} ({stats['original']['MIXED_RESULTS']/total_samples*100:.1f}%)
- All incorrect: {stats['original']['ALL_INCORRECT']} ({stats['original']['ALL_INCORRECT']/total_samples*100:.1f}%)
- Individual Performance:
  - OpenAI: {stats['original']['model_correct']['openai']/total_samples*100:.1f}%
  - Groq: {stats['original']['model_correct']['groq']/total_samples*100:.1f}%
  - Claude: {stats['original']['model_correct']['claude']/total_samples*100:.1f}%

Misspelled Text Performance
--------------------------
- All models correct: {stats['misspelled']['ALL_CORRECT']} ({stats['misspelled']['ALL_CORRECT']/total_samples*100:.1f}%)
- Mixed results: {stats['misspelled']['MIXED_RESULTS']} ({stats['misspelled']['MIXED_RESULTS']/total_samples*100:.1f}%)
- All incorrect: {stats['misspelled']['ALL_INCORRECT']} ({stats['misspelled']['ALL_INCORRECT']/total_samples*100:.1f}%)
- Individual Performance:
  - OpenAI: {stats['misspelled']['model_correct']['openai']/total_samples*100:.1f}%
  - Groq: {stats['misspelled']['model_correct']['groq']/total_samples*100:.1f}%
  - Claude: {stats['misspelled']['model_correct']['claude']/total_samples*100:.1f}%

Key Findings
-----------
1. Original Text Performance:
   - OpenAI: {stats['original']['model_correct']['openai']/total_samples*100:.1f}%
   - Groq: {stats['original']['model_correct']['groq']/total_samples*100:.1f}%
   - Claude: {stats['original']['model_correct']['claude']/total_samples*100:.1f}%

2. Impact of Misspellings:
   OpenAI:  Original {stats['original']['model_correct']['openai']/total_samples*100:.1f}% → Misspelled {stats['misspelled']['model_correct']['openai']/total_samples*100:.1f}% ({stats['misspelled']['model_correct']['openai']/total_samples*100 - stats['original']['model_correct']['openai']/total_samples*100:.1f}%)
   Groq:    Original {stats['original']['model_correct']['groq']/total_samples*100:.1f}% → Misspelled {stats['misspelled']['model_correct']['groq']/total_samples*100:.1f}% ({stats['misspelled']['model_correct']['groq']/total_samples*100 - stats['original']['model_correct']['groq']/total_samples*100:.1f}%)
   Claude:  Original {stats['original']['model_correct']['claude']/total_samples*100:.1f}% → Misspelled {stats['misspelled']['model_correct']['claude']/total_samples*100:.1f}% ({stats['misspelled']['model_correct']['claude']/total_samples*100 - stats['original']['model_correct']['claude']/total_samples*100:.1f}%)

3. Overall Robustness:
   - All models correct on original: {stats['original']['ALL_CORRECT']/total_samples*100:.1f}%
   - All models correct on misspelled: {stats['misspelled']['ALL_CORRECT']/total_samples*100:.1f}%
   - Performance Retention:
     OpenAI: {abs(stats['original']['model_correct']['openai']/total_samples*100 - stats['misspelled']['model_correct']['openai']/total_samples*100):.1f}% drop
     Groq:   {abs(stats['original']['model_correct']['groq']/total_samples*100 - stats['misspelled']['model_correct']['groq']/total_samples*100):.1f}% drop
     Claude: {abs(stats['original']['model_correct']['claude']/total_samples*100 - stats['misspelled']['model_correct']['claude']/total_samples*100):.1f}% drop
   - Most robust model: {get_most_robust_model(stats, total_samples)[0]} (smallest performance drop)
"""
    return summary

def get_most_robust_model(stats, total_samples):
    """Calculate which model is most robust based on performance retention and absolute performance"""
    model_metrics = {}
    for model in ['openai', 'groq', 'claude']:
        original = stats['original']['model_correct'][model]/total_samples*100
        misspelled = stats['misspelled']['model_correct'][model]/total_samples*100
        
        # Consider original performance more heavily
        model_metrics[model] = {
            'original': original,
            'misspelled': misspelled,
            'weighted_score': (original * 0.6) + (misspelled * 0.4)  # Weight original performance more
        }
    
    # Find model with highest weighted score
    best_model = max(model_metrics.items(), 
                    key=lambda x: x[1]['weighted_score'])
    
    return best_model[0].upper(), model_metrics

if __name__ == "__main__":
    with open('model_comparison_results.json', 'r') as f:
        data = json.load(f)
    print(generate_executive_summary(data)) 