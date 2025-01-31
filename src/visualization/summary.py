import json
from collections import Counter
from src.config import settings  # Add this import
from typing import List, Dict

def generate_executive_summary(data: List[Dict]) -> str:
    """Generate executive summary of model comparison results"""
    
    # Initialize counters
    total_samples = len(data)
    stats = calculate_statistics(data)
    
    # Get model details from settings
    model_details = {
        'openai': settings.OPENAI_MODEL,
        'groq_llama': settings.GROQ_LLAMA_MODEL,
        'groq_mixtral': settings.GROQ_MIXTRAL_MODEL,
        'claude': settings.CLAUDE_MODEL
    }
    
    # Generate summary text
    summary = f"""Executive Summary: Model Comparison Analysis
==========================================
Models Compared: {model_details['openai']} vs {model_details['groq_llama']} vs {model_details['groq_mixtral']} vs {model_details['claude']}
Sample Size: {total_samples} questions

Original Text Performance
------------------------
- All models correct: {stats['original']['ALL_CORRECT']} ({stats['original']['ALL_CORRECT']/total_samples*100:.1f}%)
- Mixed results: {stats['original']['MIXED_RESULTS']} ({stats['original']['MIXED_RESULTS']/total_samples*100:.1f}%)
- All incorrect: {stats['original']['ALL_INCORRECT']} ({stats['original']['ALL_INCORRECT']/total_samples*100:.1f}%)
- Individual Performance:
  - OpenAI: {stats['original']['model_correct']['openai']/total_samples*100:.1f}%
  - Groq-Llama: {stats['original']['model_correct']['groq_llama']/total_samples*100:.1f}%
  - Groq-Mixtral: {stats['original']['model_correct']['groq_mixtral']/total_samples*100:.1f}%
  - Claude: {stats['original']['model_correct']['claude']/total_samples*100:.1f}%

Misspelled Text Performance
--------------------------
- All models correct: {stats['misspelled']['ALL_CORRECT']} ({stats['misspelled']['ALL_CORRECT']/total_samples*100:.1f}%)
- Mixed results: {stats['misspelled']['MIXED_RESULTS']} ({stats['misspelled']['MIXED_RESULTS']/total_samples*100:.1f}%)
- All incorrect: {stats['misspelled']['ALL_INCORRECT']} ({stats['misspelled']['ALL_INCORRECT']/total_samples*100:.1f}%)
- Individual Performance:
  - OpenAI: {stats['misspelled']['model_correct']['openai']/total_samples*100:.1f}%
  - Groq-Llama: {stats['misspelled']['model_correct']['groq_llama']/total_samples*100:.1f}%
  - Groq-Mixtral: {stats['misspelled']['model_correct']['groq_mixtral']/total_samples*100:.1f}%
  - Claude: {stats['misspelled']['model_correct']['claude']/total_samples*100:.1f}%

Key Findings
-----------
1. Original Text Performance:
   - OpenAI: {stats['original']['model_correct']['openai']/total_samples*100:.1f}%
   - Groq-Llama: {stats['original']['model_correct']['groq_llama']/total_samples*100:.1f}%
   - Groq-Mixtral: {stats['original']['model_correct']['groq_mixtral']/total_samples*100:.1f}%
   - Claude: {stats['original']['model_correct']['claude']/total_samples*100:.1f}%

2. Impact of Misspellings:
   OpenAI:  Original {stats['original']['model_correct']['openai']/total_samples*100:.1f}% → Misspelled {stats['misspelled']['model_correct']['openai']/total_samples*100:.1f}% ({stats['misspelled']['model_correct']['openai']/total_samples*100 - stats['original']['model_correct']['openai']/total_samples*100:.1f}%)
   Groq-Llama:    Original {stats['original']['model_correct']['groq_llama']/total_samples*100:.1f}% → Misspelled {stats['misspelled']['model_correct']['groq_llama']/total_samples*100:.1f}% ({stats['misspelled']['model_correct']['groq_llama']/total_samples*100 - stats['original']['model_correct']['groq_llama']/total_samples*100:.1f}%)
   Groq-Mixtral:  Original {stats['original']['model_correct']['groq_mixtral']/total_samples*100:.1f}% → Misspelled {stats['misspelled']['model_correct']['groq_mixtral']/total_samples*100:.1f}% ({stats['misspelled']['model_correct']['groq_mixtral']/total_samples*100 - stats['original']['model_correct']['groq_mixtral']/total_samples*100:.1f}%)
   Claude:  Original {stats['original']['model_correct']['claude']/total_samples*100:.1f}% → Misspelled {stats['misspelled']['model_correct']['claude']/total_samples*100:.1f}% ({stats['misspelled']['model_correct']['claude']/total_samples*100 - stats['original']['model_correct']['claude']/total_samples*100:.1f}%)

3. Overall Robustness:
   - All models correct on original: {stats['original']['ALL_CORRECT']/total_samples*100:.1f}%
   - All models correct on misspelled: {stats['misspelled']['ALL_CORRECT']/total_samples*100:.1f}%
   - Performance Retention:
     OpenAI: {abs(stats['original']['model_correct']['openai']/total_samples*100 - stats['misspelled']['model_correct']['openai']/total_samples*100):.1f}% drop
     Groq-Llama: {abs(stats['original']['model_correct']['groq_llama']/total_samples*100 - stats['misspelled']['model_correct']['groq_llama']/total_samples*100):.1f}% drop
     Groq-Mixtral: {abs(stats['original']['model_correct']['groq_mixtral']/total_samples*100 - stats['misspelled']['model_correct']['groq_mixtral']/total_samples*100):.1f}% drop
     Claude: {abs(stats['original']['model_correct']['claude']/total_samples*100 - stats['misspelled']['model_correct']['claude']/total_samples*100):.1f}% drop
   - Most robust model: {get_most_robust_model(stats, total_samples)[0]} (smallest performance drop)
"""
    return summary

def get_most_robust_model(stats, total_samples):
    """Calculate which model is most robust based on performance retention"""
    model_metrics = {}
    for model in ['openai', 'groq_llama', 'groq_mixtral', 'claude']:
        original = stats['original']['model_correct'][model]/total_samples*100
        misspelled = stats['misspelled']['model_correct'][model]/total_samples*100
        
        # Consider original performance more heavily
        model_metrics[model] = {
            'original': original,
            'misspelled': misspelled,
            'weighted_score': (original * 0.6) + (misspelled * 0.4)
        }
    
    # Find model with highest weighted score
    best_model = max(model_metrics.items(), 
                    key=lambda x: x[1]['weighted_score'])
    
    return best_model[0].upper(), model_metrics

def calculate_statistics(data: List[Dict]) -> Dict:
    """Calculate statistics from comparison records"""
    stats = {
        'original': {
            'ALL_CORRECT': 0,
            'ALL_INCORRECT': 0,
            'MIXED_RESULTS': 0,
            'NONE_ANSWERED': 0,
            'model_correct': {'openai': 0, 'groq_llama': 0, 'groq_mixtral': 0, 'claude': 0}
        },
        'misspelled': {
            'ALL_CORRECT': 0,
            'ALL_INCORRECT': 0,
            'MIXED_RESULTS': 0,
            'NONE_ANSWERED': 0,
            'model_correct': {'openai': 0, 'groq_llama': 0, 'groq_mixtral': 0, 'claude': 0}
        }
    }
    
    for record in data:
        for variant in ['original', 'misspelled']:
            responses = record['results'][variant]['model_responses']
            outcome = record['results'][variant]['comparison_result']['outcome']
            stats[variant][outcome] += 1
            
            # Count correct answers for each model
            for model in ['openai', 'groq_llama', 'groq_mixtral', 'claude']:
                if responses[model]['is_correct']:
                    stats[variant]['model_correct'][model] += 1
    
    return stats

if __name__ == "__main__":
    with open('model_comparison_results.json', 'r') as f:
        data = json.load(f)
    print(generate_executive_summary(data)) 