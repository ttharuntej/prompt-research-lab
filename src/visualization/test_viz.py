import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
from src.visualization.charts import create_model_performance_chart, create_char_change_impact_chart, create_outcome_distribution_chart, create_severity_impact_chart
from datetime import datetime

def create_dashboard():
    """Create a dashboard HTML with all charts"""
    # Ensure reports directory exists
    os.makedirs('reports', exist_ok=True)
    
    try:
        with open('model_comparison_results.json', 'r') as f:
            data = json.load(f)
        
        # Create all charts
        performance_fig = create_model_performance_chart(data)
        impact_fig = create_char_change_impact_chart(data)
        outcome_fig = create_outcome_distribution_chart(data)
        severity_fig = create_severity_impact_chart(data)
        
        # Combine into HTML with refresh and better styling
        dashboard_html = f"""
        <html>
        <head>
            <title>Model Comparison Dashboard</title>
            <meta http-equiv="refresh" content="30">
            <style>
                .chart-container {{ margin: 20px; padding: 20px; }}
                body {{ font-family: Arial, sans-serif; }}
            </style>
        </head>
        <body>
            <h1 style="text-align: center;">Model Comparison Dashboard</h1>
            <p style="text-align: center;">Auto-refreshes every 30 seconds. Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <div class="chart-container">
                {performance_fig.to_html(full_html=False)}
            </div>
            <div class="chart-container">
                {impact_fig.to_html(full_html=False)}
            </div>
            <div class="chart-container">
                {outcome_fig.to_html(full_html=False)}
            </div>
            <div class="chart-container">
                {severity_fig.to_html(full_html=False)}
            </div>
        </body>
        </html>
        """
        
        with open("reports/dashboard.html", "w") as f:
            f.write(dashboard_html)
            
        print(f"\nDashboard created successfully!")
        print(f"Open reports/dashboard.html in your browser to view")
        
    except Exception as e:
        print(f"Error creating dashboard: {str(e)}")

if __name__ == "__main__":
    create_dashboard() 