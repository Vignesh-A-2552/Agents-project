"""
Prompt configuration models using Pydantic for type safety and validation.
"""
import yaml
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field
from loguru import logger


class PromptConfig(BaseModel):
    """Configuration for a specific prompt version."""
    
    model: str = Field(..., description="The model to use for this prompt")
    temperature: float = Field(default=0.0, description="Temperature setting for the model")
    prompt: str = Field(..., description="The actual prompt template")


class ConversationConfig(BaseModel):
    """Configuration for conversation prompts."""

    CONVERSATION_PROMPT_V1: PromptConfig


class CodeReviewConfig(BaseModel):
    """Configuration for code review prompts."""
    
    SYNTAX_ANALYSIS: PromptConfig
    STYLE_CHECK: PromptConfig
    COMMENT_QUALITY: PromptConfig
    SECURITY_SCAN: PromptConfig
    PERFORMANCE_ANALYSIS: PromptConfig
    BEST_PRACTICES: PromptConfig
    EXPLANATIONS: PromptConfig


class AllPromptsConfig(BaseModel):
    """Configuration for all prompt categories."""
    
    conversation: ConversationConfig
    code_review: CodeReviewConfig


def load_prompt_config(config_path: str) -> Dict[str, Any]:
    """
    Load a prompt configuration from a YAML file in the prompts directory.

    Args:
        config_path: Name of the YAML configuration file.

    Returns:
        Dictionary containing the parsed YAML configuration.

    Raises:
        FileNotFoundError: If the configuration file cannot be found.
        yaml.YAMLError: If the YAML file is malformed or cannot be parsed.
    """
    import os
    config_path = os.path.join("prompts", config_path)
    return load_config(config_path)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load the configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Dictionary containing the parsed YAML configuration.

    Raises:
        FileNotFoundError: If the configuration file cannot be found.
        yaml.YAMLError: If the YAML file is malformed or cannot be parsed.
    """
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        logger.debug(f"Loaded configuration from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found at: {config_path}")
        raise FileNotFoundError(
            f"Configuration file not found at: {config_path}"
        )
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {str(e)}")
        raise yaml.YAMLError(f"Error parsing YAML configuration: {str(e)}")


def load_conversation_config(config_path: str = "conversation_config.yml") -> ConversationConfig:
    """
    Load the conversation configuration from a YAML file and convert it to a ConversationConfig object.

    Args:
        config_path: Name of the YAML configuration file in the prompts directory.
        
    Returns:
        ConversationConfig object containing the parsed configuration.
        
    Raises:
        FileNotFoundError: If the configuration file cannot be found.
        yaml.YAMLError: If the YAML file is malformed or cannot be parsed.
    """
    config_dict = load_prompt_config(config_path)
    return ConversationConfig(**config_dict)


def load_code_review_config(config_path: str = "code_review_config.yml") -> CodeReviewConfig:
    """
    Load the code review configuration from a YAML file and convert it to a CodeReviewConfig object.
    
    Args:
        config_path: Name of the YAML configuration file in the prompts directory.
        
    Returns:
        CodeReviewConfig object containing the parsed configuration.
        
    Raises:
        FileNotFoundError: If the configuration file cannot be found.
        yaml.YAMLError: If the YAML file is malformed or cannot be parsed.
    """
    config_dict = load_prompt_config(config_path)
    return CodeReviewConfig(**config_dict)