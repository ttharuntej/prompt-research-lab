import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
from src.visualization.charts import create_model_performance_chart, create_char_change_impact_chart, create_outcome_distribution_chart, create_severity_impact_chart
from datetime import datetime
from src.config import settings
from src.visualization.summary import generate_executive_summary

def create_dashboard():
    """Create a dashboard HTML with all charts"""
    # Ensure reports directory exists
    os.makedirs('reports', exist_ok=True)
    
    try:
        with open('model_comparison_results.json', 'r') as f:
            data = json.load(f)
        
        # Get executive summary
        exec_summary = generate_executive_summary(data)
        
        # Create all charts
        performance_fig = create_model_performance_chart(data)
        impact_fig = create_char_change_impact_chart(data)
        outcome_fig = create_outcome_distribution_chart(data)
        severity_fig = create_severity_impact_chart(data)
        
        # Updated dashboard HTML with PDF export button
        dashboard_html = f"""
        <html>
        <head>
            <title>Model Comparison Dashboard</title>
            <meta http-equiv="refresh" content="30">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                /* Vertical layout for charts */
                .dashboard-grid {{
                    display: flex;
                    flex-direction: column;
                    gap: 30px;
                    padding: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                
                .chart-container {{ 
                    margin: 0;
                    padding: 10px;
                    height: 500px;  /* Taller for vertical layout */
                    width: 100%;
                }}
                
                .summary-container {{ 
                    margin: 20px; 
                    padding: 20px; 
                    background-color: #f5f5f5;
                    border-radius: 5px;
                    white-space: pre-wrap;
                    font-family: monospace;
                    overflow-x: auto;  /* For mobile */
                }}
                
                /* Print specific styles */
                @media print {{
                    .export-button {{ display: none; }}
                    
                    @page {{
                        size: portrait;
                        margin: 1cm;
                    }}
                    
                    .chart-container {{
                        page-break-inside: avoid;
                        break-inside: avoid;
                        height: 80vh;
                    }}
                    
                    .summary-container {{
                        page-break-before: avoid;
                        page-break-after: always;
                    }}
                }}
                
                /* Mobile responsive */
                @media screen and (max-width: 768px) {{
                    .chart-container {{
                        height: 400px;
                    }}
                    
                    .summary-container {{
                        margin: 10px;
                        padding: 10px;
                        font-size: 14px;
                    }}
                    
                    .export-button {{
                        position: static;
                        margin: 20px auto;
                        display: block;
                    }}
                }}
                
                body {{ font-family: Arial, sans-serif; }}
                .export-button {{
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                }}
                .export-button:hover {{
                    background-color: #45a049;
                }}
            </style>
            <script>
                function exportToPDF() {{
                    window.print();
                }}
            </script>
        </head>
        <body>
            <button class="export-button" onclick="exportToPDF()">Export to PDF</button>
            <h1 style="text-align: center;">Model Comparison Dashboard</h1>
            <p style="text-align: center;">Auto-refreshes every 30 seconds. Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="summary-container">
                {exec_summary}
            </div>
            
            <div class="dashboard-grid">
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