# Prompt Research Lab

## Overview

Prompt Research Lab is a project designed to evaluate and compare the performance of different language models (LLMs) in handling various prompts. The project leverages models from OpenAI and Llama  Via Groq to provide insights into how different models respond to the same input, helping researchers and developers optimize prompt engineering strategies.

## Features

- **Model Comparison**: Compare responses from different LLMs to analyze their interpretation and handling of prompts.
- **Response Analysis**: Analyze response characteristics including length, word count, and content quality.
- **Automated Evaluation**: Utilize CrewAI for structured and automated model comparison workflows.
- **Multi-Model Support**: Currently supports OpenAI (GPT-3.5-turbo) and Groq (llama-3.3-70b-versatile) models.

## Project Structure

```
prompt-research-lab/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── model_comparison_agent.py
│   │   ├── optimization_agent.py    # To be implemented
│   │   └── research_agent.py        # To be implemented
│   └── run_comparison.py
├── .env
├── requirements.txt
└── README.md
```

## Components

### Agents

- **Model Comparison Agent**: Evaluates and compares responses from different LLM models, providing detailed analysis of their performance characteristics and response patterns.
- **Optimization Agent**: (Planned) Will focus on optimizing prompts based on comparison results.
- **Research Agent**: (Planned) Will conduct research on prompt engineering techniques and model capabilities.

### Tools

- **Model Comparison Tool**: Compares responses from different LLMs using standardized metrics.
- **Response Analysis**: Provides detailed analysis of response characteristics and quality metrics.

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/prompt-research-lab.git
   cd prompt-research-lab
   ```

2. **Create a Virtual Environment**:
   ```bash
    # Create new environment with Python 3.10
   conda create -n prompt-lab python=3.10
   
   # Activate the environment
   conda activate prompt-lab
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the project root with your API keys:
   ```plaintext
   OPENAI_API_KEY=your-openai-api-key
   GROQ_API_KEY=your-groq-api-key
   ```

## Usage

Run the model comparison:
```bash
python src/run_comparison.py
```

This will:
1. Load your environment variables
2. Initialize the model comparison agent
3. Execute the comparison task
4. Display detailed results comparing responses from both models

## Example Output

The comparison results include:
- Full responses from both models
- Length comparison metrics
- Word and character count analysis
- Quality assessment of responses


## Dependencies

- crewai
- openai
- groq
- python-dotenv
- langchain
- pydantic
