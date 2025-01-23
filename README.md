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

## Contributing

We welcome contributions to the Prompt Research Lab! Here's how you can contribute:

1. **Fork the Repository**
   - Click the 'Fork' button at the top right of this repository
   - Clone your fork locally:
     ```bash
     git clone https://github.com/your-username/prompt-research-lab.git
     ```

2. **Set Up Development Environment**
   - Follow the setup instructions above to create your environment and install dependencies
   - Make sure to create your own `.env` file with your API keys

3. **Create a New Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-fix-name
   ```

4. **Make Your Changes**
   - Write clean, documented code
   - Follow the existing code style and structure
   - Add tests if applicable
   - Update documentation as needed

5. **Test Your Changes**
   - Ensure all existing tests pass
   - Test your new features thoroughly

6. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

7. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Submit a Pull Request**
   - Go to the original repository on GitHub
   - Click 'New Pull Request'
   - Select your fork and branch
   - Provide a clear description of your changes
   - Link any relevant issues

### Contribution Guidelines

- Keep pull requests focused on a single feature or fix
- Follow Python best practices and PEP 8 style guidelines
- Include docstrings and comments where appropriate
- Update the README if you're adding new features or changing functionality
- Be respectful and constructive in discussions

### Need Help?

If you have questions or need help with your contribution:
- Open an issue for discussion
- Comment on the relevant issue or pull request
- Reach out to the maintainers

Thank you for contributing to Prompt Research Lab!
