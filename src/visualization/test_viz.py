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
    create_severity_impact_chart
)
from src.visualization.summary import generate_executive_summary
from typing import List, Dict

def create_dashboard(data: List[Dict]) -> html.Div:
    """Create dashboard with all visualizations"""
    return html.Div([
        # Title and Print Button
        html.H1('Model Comparison Dashboard', 
                style={'textAlign': 'center', 'marginBottom': '10px'}),
        html.P(f'Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
               style={'textAlign': 'center', 'marginBottom': '30px'}),
        html.Button(
            'Print Dashboard',
            id='print-button',
            style={
                'position': 'fixed',
                'top': '20px',
                'right': '20px',
                'padding': '10px 20px',
                'backgroundColor': '#4CAF50',
                'color': 'white',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontSize': '16px'
            }
        ),
        
        # Print Script
        html.Script('''
            document.getElementById('print-button').onclick = function() {
                window.print();
            }
        '''),
        
        # Executive Summary
        html.Div([
            html.Pre(
                generate_executive_summary(data),
                style={
                    'whiteSpace': 'pre-wrap',
                    'fontFamily': 'monospace',
                    'padding': '20px',
                    'backgroundColor': '#f5f5f5',
                    'borderRadius': '5px',
                    'overflowX': 'auto',
                    'margin': '20px'
                }
            )
        ], className='summary-container'),
        
        # Charts in Vertical Layout
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=create_model_performance_chart(data),
                    config={'displayModeBar': False}
                )
            ], className='chart-container'),
            
            html.Div([
                dcc.Graph(
                    figure=create_outcome_distribution_chart(data),
                    config={'displayModeBar': False}
                )
            ], className='chart-container'),
            
            html.Div([
                dcc.Graph(
                    figure=create_char_change_impact_chart(data),
                    config={'displayModeBar': False}
                )
            ], className='chart-container'),
            
            html.Div([
                dcc.Graph(
                    figure=create_severity_impact_chart(data),
                    config={'displayModeBar': False}
                )
            ], className='chart-container')
        ], style={
            'display': 'flex',
            'flexDirection': 'column',
            'gap': '30px',
            'padding': '20px',
            'maxWidth': '1200px',
            'margin': '0 auto'
        })
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