# Prompt Templates

This directory contains all the prompt templates used by the Code Review API in structured YAML format.

## Files

- `syntax_analysis.yml` - Prompt for syntax error detection
- `style_check.yml` - Prompt for code style violations  
- `comment_quality.yml` - Prompt for documentation quality assessment
- `security_scan.yml` - Prompt for security vulnerability detection
- `performance_analysis.yml` - Prompt for performance issue analysis
- `best_practices.yml` - Prompt for best practices violations
- `explanations.yml` - Prompt for educational explanations and suggestions

## YAML Structure

Each YAML file contains:

```yaml
name: "Prompt Name"
description: "Description of what this prompt does"
version: "1.0"
input_parameters:
  - name: "language"
    description: "Programming language of the code"
    required: true
  - name: "code"
    description: "Source code to analyze"
    required: true
output_format:
  type: "json"
  schema:
    # Expected JSON response structure
template: |
  # The actual prompt template with placeholders
```

## Placeholders

Prompt templates use Python string formatting with placeholders:
- `{language}` - Programming language (e.g., "python", "javascript")
- `{code}` - Code to analyze
- `{aspect}` - Performance aspect (only for performance_analysis.yml)
- `{issues}` - Issues found (only for explanations.yml)

## Editing

You can edit these YAML files directly to modify:
- Prompt templates (`template` field)
- Metadata (name, description, version)
- Input/output documentation
- Response schemas

Changes will be automatically loaded when the service restarts.

## Features

- **Structured metadata** - Name, description, version tracking
- **Parameter documentation** - Input requirements and examples
- **Schema validation** - Expected output format documentation
- **Version control friendly** - Clear diff tracking for changes
- **Enhanced logging** - Metadata is logged during prompt loading