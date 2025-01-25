from typing import List, Dict
import plotly.graph_objects as go
import plotly.express as px
from ..schemas.comparison_schema import ComparisonOutcome
from plotly.subplots import make_subplots

def create_model_performance_chart(data: List[Dict]) -> go.Figure:
    """Create bar chart comparing model performance
    
    Shows:
    - Original vs Misspelled accuracy
    - OpenAI vs Groq comparison
    """
    # Process data
    stats = {
        'original': {'openai': 0, 'groq': 0, 'total': 0},
        'misspelled': {'openai': 0, 'groq': 0, 'total': 0}
    }
    
    for record in data:
        # Original results
        orig = record['results']['original']
        stats['original']['total'] += 1
        if orig['model_responses']['openai']['answer'] == record['question_pair']['expected_answer']:
            stats['original']['openai'] += 1
        if orig['model_responses']['groq']['answer'] == record['question_pair']['expected_answer']:
            stats['original']['groq'] += 1
            
        # Misspelled results
        misp = record['results']['misspelled']
        stats['misspelled']['total'] += 1
        if misp['model_responses']['openai']['answer'] == record['question_pair']['expected_answer']:
            stats['misspelled']['openai'] += 1
        if misp['model_responses']['groq']['answer'] == record['question_pair']['expected_answer']:
            stats['misspelled']['groq'] += 1
    
    # Create figure
    fig = go.Figure(data=[
        go.Bar(name='OpenAI Original', 
               x=['Accuracy'], 
               y=[stats['original']['openai']/stats['original']['total'] * 100]),
        go.Bar(name='Groq Original',
               x=['Accuracy'],
               y=[stats['original']['groq']/stats['original']['total'] * 100]),
        go.Bar(name='OpenAI Misspelled',
               x=['Accuracy'],
               y=[stats['misspelled']['openai']/stats['misspelled']['total'] * 100]),
        go.Bar(name='Groq Misspelled',
               x=['Accuracy'],
               y=[stats['misspelled']['groq']/stats['misspelled']['total'] * 100])
    ])
    
    fig.update_layout(
        title=f'Model Performance Comparison (n={stats["original"]["total"]} samples)',
        yaxis_title='Accuracy (%)',
        barmode='group',
        height=600,
        margin=dict(t=100, b=100),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.9)'
        )
    )
    
    return fig 

def create_char_change_impact_chart(data: List[Dict]) -> go.Figure:
    """Create scatter plot showing impact of character changes on accuracy
    
    Shows relationship between:
    - Number of character changes
    - Model accuracy
    """
    # Collect data points
    points = []
    for record in data:
        char_changes = record['misspelling_info']['char_change_count']
        expected = record['question_pair']['expected_answer']
        
        # OpenAI accuracy
        openai_correct = record['results']['misspelled']['model_responses']['openai']['answer'] == expected
        points.append({
            'char_changes': char_changes,
            'correct': int(openai_correct),
            'model': 'OpenAI'
        })
        
        # Groq accuracy
        groq_correct = record['results']['misspelled']['model_responses']['groq']['answer'] == expected
        points.append({
            'char_changes': char_changes,
            'correct': int(groq_correct),
            'model': 'Groq'
        })
    
    # Create figure using plotly express
    total_samples = len(data)
    fig = px.scatter(points, 
                    x='char_changes',
                    y='correct',
                    color='model',
                    title=f'Impact of Character Changes on Model Accuracy (n={total_samples} samples)',
                    labels={
                        'char_changes': 'Number of Character Changes',
                        'correct': 'Correct (1) / Incorrect (0)',
                        'model': 'Model'
                    })
    
    fig.update_layout(
        title=f'Impact of Character Changes on Model Accuracy (n={total_samples} samples)',
        height=600,
        margin=dict(t=100, b=100),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.9)'
        )
    )
    
    return fig 

def create_outcome_distribution_chart(data: List[Dict]) -> go.Figure:
    """Create pie charts showing distribution of outcomes
    
    Shows:
    - Distribution of BOTH_CORRECT, BOTH_INCORRECT, etc.
    - Separate for original vs misspelled
    """
    outcomes = {
        'original': {'BOTH_CORRECT': 0, 'BOTH_INCORRECT': 0, 
                    'OPENAI_ONLY_CORRECT': 0, 'GROQ_ONLY_CORRECT': 0, 
                    'NEITHER_ANSWERED': 0},
        'misspelled': {'BOTH_CORRECT': 0, 'BOTH_INCORRECT': 0, 
                      'OPENAI_ONLY_CORRECT': 0, 'GROQ_ONLY_CORRECT': 0, 
                      'NEITHER_ANSWERED': 0}
    }
    
    for record in data:
        # Count original outcomes
        orig_outcome = record['results']['original']['comparison_result']['outcome']
        outcomes['original'][orig_outcome] += 1
        
        # Count misspelled outcomes
        misp_outcome = record['results']['misspelled']['comparison_result']['outcome']
        outcomes['misspelled'][misp_outcome] += 1
    
    # Create subplots
    fig = make_subplots(rows=1, cols=2, 
                       specs=[[{'type':'domain'}, {'type':'domain'}]],
                       subplot_titles=('Original Text', 'Misspelled Text'))
    
    fig.add_trace(go.Pie(labels=list(outcomes['original'].keys()),
                        values=list(outcomes['original'].values()),
                        name="Original"), 1, 1)
    
    fig.add_trace(go.Pie(labels=list(outcomes['misspelled'].keys()),
                        values=list(outcomes['misspelled'].values()),
                        name="Misspelled"), 1, 2)
    
    total_samples = len(data)
    fig.update_layout(
        title=f'Distribution of Outcomes (n={total_samples} samples)',
        height=600,
        margin=dict(t=100, b=100),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.9)'
        )
    )
    return fig

def create_severity_impact_chart(data: List[Dict]) -> go.Figure:
    """Create line chart showing accuracy by severity level
    
    Shows:
    - Model accuracy at different severity levels
    - Trend lines
    """
    # Group by severity
    severity_stats = {}
    
    for record in data:
        severity = record['misspelling_info']['severity']
        if severity not in severity_stats:
            severity_stats[severity] = {
                'openai_correct': 0, 'groq_correct': 0, 'total': 0
            }
        
        expected = record['question_pair']['expected_answer']
        stats = severity_stats[severity]
        stats['total'] += 1
        
        # Check correctness
        if record['results']['misspelled']['model_responses']['openai']['answer'] == expected:
            stats['openai_correct'] += 1
        if record['results']['misspelled']['model_responses']['groq']['answer'] == expected:
            stats['groq_correct'] += 1
    
    # Create figure
    fig = go.Figure()
    
    severities = list(severity_stats.keys())
    openai_acc = [stats['openai_correct']/stats['total']*100 
                  for stats in severity_stats.values()]
    groq_acc = [stats['groq_correct']/stats['total']*100 
                for stats in severity_stats.values()]
    
    fig.add_trace(go.Scatter(x=severities, y=openai_acc, 
                            mode='lines+markers', name='OpenAI'))
    fig.add_trace(go.Scatter(x=severities, y=groq_acc, 
                            mode='lines+markers', name='Groq'))
    
    total_samples = sum(stats['total'] for stats in severity_stats.values())
    fig.update_layout(
        title=f'Model Accuracy by Severity Level (n={total_samples} samples)',
        xaxis_title='Severity Level',
        yaxis_title='Accuracy (%)',
        height=600,
        margin=dict(t=100, b=100),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.9)'
        )
    )
    
    return fig