from pathlib import Path
from loguru import logger
from config.prompt_config import load_conversation_config, load_code_review_config


class PromptService:
    def __init__(self):
        self.prompts_dir = Path("prompts")
        self._setup_configs()
    
    def _setup_configs(self):
        """Initialize all configurations using Pydantic models."""
        logger.info("Loading configurations using Pydantic models")
        
        try:
            # Load conversation configuration
            self.conversation_config = load_conversation_config()
            logger.success("Conversation configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load conversation configuration: {e}")
            self.conversation_config = None

        try:
            # Load code review configuration
            self.code_review_config = load_code_review_config()
            logger.success("Code review configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load code review configuration: {e}")
            self.code_review_config = None
    
    def get_conversation_prompt(self, question: str, context: str = "") -> str:
        """Get formatted conversation prompt with user question and optional context."""
        if self.conversation_config:
            prompt_template = self.conversation_config.CONVERSATION_PROMPT_V1.prompt
            formatted_prompt = prompt_template.replace('{question}', question).replace('{context}', context)
            return formatted_prompt
        else:
            raise AttributeError("No conversation prompt configuration available")

    
    def get_syntax_prompt(self, code: str, language: str) -> str:
        """Get formatted syntax analysis prompt."""
        if self.code_review_config:
            return self.code_review_config.SYNTAX_ANALYSIS.prompt.format(code=code, language=language)
        else:
            return f"Analyze this {language} code for syntax issues:\n\n```{language}\n{code}\n```"
    
    def get_style_prompt(self, code: str, language: str) -> str:
        """Get formatted style check prompt."""
        if self.code_review_config:
            return self.code_review_config.STYLE_CHECK.prompt.format(code=code, language=language)
        else:
            return f"Analyze this {language} code for style issues:\n\n```{language}\n{code}\n```"
    
    def get_comment_quality_prompt(self, code: str, language: str) -> str:
        """Get formatted comment quality prompt."""
        if self.code_review_config:
            return self.code_review_config.COMMENT_QUALITY.prompt.format(code=code, language=language)
        else:
            return f"Analyze this {language} code for documentation quality:\n\n```{language}\n{code}\n```"
    
    def get_security_prompt(self, code: str, language: str) -> str:
        """Get formatted security scan prompt."""
        if self.code_review_config:
            return self.code_review_config.SECURITY_SCAN.prompt.format(code=code, language=language)
        else:
            return f"Analyze this {language} code for security issues:\n\n```{language}\n{code}\n```"
    
    def get_performance_prompt(self, code: str, language: str) -> str:
        """Get formatted performance analysis prompt."""
        if self.code_review_config:
            return self.code_review_config.PERFORMANCE_ANALYSIS.prompt.format(code=code, language=language)
        else:
            return f"Analyze this {language} code for performance issues:\n\n```{language}\n{code}\n```"
    
    def get_best_practices_prompt(self, code: str, language: str) -> str:
        """Get formatted best practices prompt."""
        if self.code_review_config:
            return self.code_review_config.BEST_PRACTICES.prompt.format(code=code, language=language)
        else:
            return f"Analyze this {language} code for best practices:\n\n```{language}\n{code}\n```"
    
    def get_explanation_prompt(self, code: str, language: str) -> str:
        """Get formatted explanation prompt."""
        if self.code_review_config:
            return self.code_review_config.EXPLANATIONS.prompt.format(code=code, language=language)
        else:
            return f"Explain this {language} code:\n\n```{language}\n{code}\n```"