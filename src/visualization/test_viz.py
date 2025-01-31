import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
from datetime import datetime
import dash
from dash import html, dcc
from src.visualization.charts import (
    create_model_performance_chart, 
    create_char_change_impact_chart, 
    create_outcome_distribution_chart, 
    create_severity_impact_chart,
    create_performance_chart,
    create_robustness_chart
)
from src.visualization.summary import generate_executive_summary
from typing import List, Dict

def create_dashboard(data: List[Dict]) -> html.Div:
    """Create the complete dashboard"""
    
    return html.Div([
        html.H1('Model Comparison Analysis'),
        
        # Executive Summary
        html.Div([
            html.H2('Executive Summary'),
            dcc.Markdown(generate_executive_summary(data))
        ]),
        
        # Performance Chart
        html.Div([
            html.H2('Performance Comparison'),
            dcc.Graph(figure=create_performance_chart(data))
        ]),
        
        # Robustness Chart
        html.Div([
            html.H2('Robustness Analysis'),
            dcc.Graph(figure=create_robustness_chart(data))
        ])
    ])

if __name__ == "__main__":
    # Load data
    with open('model_comparison_results.json', 'r') as f:
        data = json.load(f)
    
    # Create Dash app
    app = dash.Dash(
        __name__,
        meta_tags=[
            {
                'name': 'viewport',
                'content': 'width=device-width, initial-scale=1.0'
            }
        ]
    )
    
    app.layout = create_dashboard(data)
    
    # Run server
    app.run_server(debug=True)