# Code Review API

AI-powered code review service that analyzes syntax, security, performance, and best practices using LangGraph agents and OpenAI models.

## Features

- **Multi-dimensional Analysis**: Comprehensive code review covering syntax, security, performance, and best practices
- **Language Support**: Python and JavaScript code analysis
- **AI-Powered**: Uses OpenAI models with structured prompts for consistent analysis
- **Agent-Based Architecture**: Built with LangGraph for modular and extensible analysis workflows
- **RESTful API**: FastAPI-based service with comprehensive logging and monitoring
- **Configurable**: Environment-based configuration with validation

## Architecture

```
agent/
├── app/                    # FastAPI application
│   ├── api.py             # API routes and endpoints
│   └── __init__.py
├── config/                 # Configuration management
│   ├── logging.py         # Logging setup with loguru
│   ├── settings.py        # Environment and app settings
│   └── __init__.py
├── models/                 # Data models and schemas
│   ├── schemas.py         # Pydantic models for API
│   ├── types.py           # Type definitions
│   └── __init__.py
├── services/               # Core business logic
│   ├── code_review_service.py  # Main review orchestration
│   ├── llm_service.py     # OpenAI integration
│   ├── prompt_service.py  # Prompt management
│   └── __init__.py
├── prompts/                # Analysis prompts and configurations
│   ├── best_practices.yml # Best practices analysis
│   ├── comment_quality.yml# Code comments evaluation
│   ├── explanations.yml   # Issue explanations
│   ├── performance_analysis.yml # Performance optimization
│   ├── security_scan.yml  # Security vulnerability detection
│   ├── style_check.yml    # Code style validation
│   ├── syntax_analysis.yml# Syntax error detection
│   └── README.md          # Prompts documentation
├── logs/                   # Application logs
│   ├── app.log           # General application logs
│   ├── error.log         # Error logs
│   └── requests.log      # API request logs
├── main.py                # Application entry point
└── requirements.txt       # Python dependencies
```

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd agent
```

2. Create virtual environment:
```bash
python -m venv agents-venv
source agents-venv/bin/activate  # On Windows: agents-venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file
OPENAI_API_KEY=your_openai_api_key_here
MODEL=gpt-4-turbo-preview
```

5. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Core Endpoints

- `POST /review` - Analyze code for issues and improvements
- `GET /health` - Health check endpoint
- `GET /supported-languages` - List supported programming languages

### Debug Endpoints

- `GET /debug/status` - System status and configuration
- `GET /debug/logs` - Recent log entries

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Example

### Code Review Request

```bash
curl -X POST "http://localhost:8000/review" \
     -H "Content-Type: application/json" \
     -d '{
       "code": "def hello_world():\n    print(\"Hello, World!\")",
       "language": "python",
       "file_type": "py",
       "context": "Simple greeting function"
     }'
```

### Response Format

```json
{
  "severity_level": "low",
  "requires_human_review": false,
  "analysis_complete": true,
  "processing_time_seconds": 2.1,
  "syntax_issues": [],
  "security_vulnerabilities": [],
  "performance_issues": [],
  "style_violations": [],
  "best_practice_violations": [],
  "explanations": [],
  "improvement_suggestions": [],
  "learning_resources": [],
  "summary": {
    "total_issues": 0,
    "syntax_issues": 0,
    "security_vulnerabilities": 0,
    "performance_issues": 0,
    "style_violations": 0,
    "best_practice_violations": 0,
    "code_length": 45,
    "language": "python"
  }
}
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `MODEL` | OpenAI model to use | Yes | - |

### Application Settings

Configure in `config/settings.py`:

- **Server**: Host, port, reload settings
- **Analysis**: Max code length, supported languages
- **CORS**: Cross-origin request settings
- **Performance**: Analysis aspects and thresholds

## Analysis Types

1. **Syntax Analysis**: Detects syntax errors and malformed code
2. **Security Scan**: Identifies potential security vulnerabilities
3. **Performance Analysis**: Evaluates efficiency and optimization opportunities
4. **Style Check**: Validates code style and formatting
5. **Best Practices**: Reviews adherence to language-specific best practices
6. **Comment Quality**: Assesses code documentation and comments

## Logging

The application uses structured logging with loguru:

- **app.log**: General application events
- **error.log**: Error conditions and exceptions
- **requests.log**: API request/response logging

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Development

### Adding New Languages

1. Update `SUPPORTED_LANGUAGES` and `SUPPORTED_FILE_TYPES` in `settings.py`
2. Add language-specific prompts in `prompts/` directory
3. Update prompt loading in `PromptService`
4. Test with sample code

### Extending Analysis

1. Create new prompt templates in `prompts/`
2. Add analysis methods in `CodeReviewService`
3. Update the LangGraph workflow
4. Add corresponding response fields in schemas

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with appropriate tests
4. Ensure code follows style guidelines
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the logs at `/debug/logs` endpoint
2. Verify configuration at `/debug/status` endpoint
3. Review the API documentation at `/docs`
4. Check environment variables and OpenAI API key