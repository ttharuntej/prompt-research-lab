# Prompt Research Lab

A framework for comparing LLM responses across different models with misspelling stability testing.

## Features

- Compare responses from multiple LLMs:
  - OpenAI GPT-4
  - Groq Llama (llama-3.3-70b-versatile)
  - Groq Mixtral (mixtral-8x7b-32768)
  - Claude 3.5 Sonnet
- Test model robustness against misspellings
- Generate detailed comparison reports
- Visualize performance metrics

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your API keys:
   - OPENAI_API_KEY
   - GROQ_LLAMA_API_KEY
   - GROQ_MIXTRAL_API_KEY
   - ANTHROPIC_API_KEY

## Usage

1. Single Comparison Test (tests basic setup):
   ```bash
   python src/run_comparison.py
   ```
   This will:
   - Test all API connections
   - Run a single comparison across all models
   - Display raw results in the console

2. Batch Comparison (main testing):
   ```bash
   python src/run_batch_comparison.py
   ```
   This will:
   - Process multiple questions from eval_data.json
   - Test both original and misspelled variants
   - Generate model_comparison_results.json in project root

3. Visualize Results:
   ```bash
   python src/visualization/test_viz.py
   ```
   This will:
   - Load results from model_comparison_results.json
   - Start a local Dash server (usually at http://127.0.0.1:8050)
   - Open your browser to show interactive dashboard with:
     - Performance comparisons
     - Robustness analysis
     - Executive summary
     - Detailed metrics

Note: 
- Run the scripts in this order for a complete testing cycle
- Ensure eval_data.json exists before running batch comparison
- The visualization server can be stopped with Ctrl+C

## Configuration

Settings can be configured in `src/config.py`, including:
- Model selection
- Batch size
- Misspelling severity
- Output file locations

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
## Configuration

The application uses Pydantic Settings for configuration management. Configuration can be set through environment variables or a `.env` file.

### Required Settings
- `OPENAI_API_KEY`: Your OpenAI API key
- `GROQ_API_KEY`: Your Groq API key

### Optional Settings
- `DEFAULT_MODEL`: OpenAI model to use (default: "gpt-3.5-turbo")
- `GROQ_MODEL`: Groq model to use (default: "llama-3.3-70b-versatile")
- `MAX_TOKENS`: Maximum tokens for model responses (default: 1000)
- `BATCH_SIZE`: Number of questions to process in one batch (default: 10)
- `OUTPUT_FILE`: File to save failed comparisons (default: "failed_comparisons.json")

### Environment Variables
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your-openai-key-here
GROQ_LLAMA_API_KEY=your-groq-llama-key-here
GROQ_MIXTRAL_API_KEY=your-groq-mixtral-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here

# Optional settings
DEFAULT_MODEL=gpt-4o
MAX_TOKENS=1000
BATCH_SIZE=10
```

The application is flexible with additional environment variables and is case-insensitive.

