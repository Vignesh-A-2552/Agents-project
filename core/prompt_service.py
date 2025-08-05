import yaml
from pathlib import Path
from langchain.prompts import PromptTemplate
from loguru import logger
from config.prompt_config import load_chat_config, load_code_review_config, ChatConfig, CodeReviewConfig


class PromptService:
    def __init__(self):
        self.prompts_dir = Path("prompts")
        self._setup_new_configs()
        self._setup_legacy_prompts()
    
    def _load_prompt_template(self, filename: str) -> PromptTemplate:
        """Load a prompt template from a YAML file."""
        try:
            prompt_file = self.prompts_dir / filename
            if not prompt_file.exists():
                logger.error(f"Prompt file not found: {prompt_file}")
                raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_data = yaml.safe_load(f)
            
            # Validate required fields
            if 'template' not in prompt_data:
                raise ValueError(f"Missing 'template' field in {filename}")
            
            # Log prompt metadata
            prompt_name = prompt_data.get('name', 'Unknown')
            prompt_version = prompt_data.get('version', '1.0')
            logger.debug(f"Loaded prompt '{prompt_name}' v{prompt_version} from {filename}")
            
            # Extract and return the template
            template_content = prompt_data['template'].strip()
            return PromptTemplate.from_template(template_content)
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {filename}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading prompt template from {filename}: {e}")
            raise
    
    def get_prompt_metadata(self, filename: str) -> dict:
        """Get metadata for a prompt file."""
        try:
            prompt_file = self.prompts_dir / filename
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_data = yaml.safe_load(f)
            
            return {
                'name': prompt_data.get('name', 'Unknown'),
                'description': prompt_data.get('description', ''),
                'version': prompt_data.get('version', '1.0'),
                'input_parameters': prompt_data.get('input_parameters', []),
                'output_format': prompt_data.get('output_format', {})
            }
        except Exception as e:
            logger.error(f"Error getting metadata from {filename}: {e}")
            return {}
    
    def _setup_new_configs(self):
        """Initialize all configurations using Pydantic models."""
        logger.info("Loading configurations using Pydantic models")
        
        try:
            # Load chat configuration
            self.chat_config = load_chat_config()
            logger.success("Chat configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load chat configuration: {e}")
            self.chat_config = None
        
        try:
            # Load code review configuration
            self.code_review_config = load_code_review_config()
            logger.success("Code review configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load code review configuration: {e}")
            self.code_review_config = None
    
    def _setup_legacy_prompts(self):
        """Fallback to legacy prompt loading if new configs fail."""
        if not self.chat_config:
            logger.info("Loading legacy chat prompt as fallback")
            try:
                self.chat_prompt = self._load_chat_prompt_template("chat.yml")
            except Exception as e:
                logger.warning(f"Failed to load legacy chat prompt: {e}")
        
        if not self.code_review_config:
            logger.info("Loading legacy code review prompts as fallback")
            try:
                self.syntax_prompt = self._load_prompt_template("syntax_analysis.yml")
                self.format_prompt = self._load_prompt_template("style_check.yml")
                self.comment_quality_prompt = self._load_prompt_template("comment_quality.yml")
                self.security_scan_prompt = self._load_prompt_template("security_scan.yml")
                self.performance_prompt = self._load_prompt_template("performance_analysis.yml")
                self.best_practices_prompt = self._load_prompt_template("best_practices.yml")
                self.explanation_prompt = self._load_prompt_template("explanations.yml")
                logger.success("Legacy code review prompts loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load legacy prompts: {e}")
    
    def _load_chat_prompt_template(self, filename: str) -> str:
        """Load chat prompt template with different structure."""
        try:
            prompt_file = self.prompts_dir / filename
            if not prompt_file.exists():
                logger.error(f"Chat prompt file not found: {prompt_file}")
                raise FileNotFoundError(f"Chat prompt file not found: {prompt_file}")
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_data = yaml.safe_load(f)
            
            # For chat prompts, we expect system_prompt and user_template
            system_prompt = prompt_data.get('system_prompt', '').strip()
            user_template = prompt_data.get('user_template', '').strip()
            
            return f"{system_prompt}\n\n{user_template}"
            
        except Exception as e:
            logger.error(f"Error loading chat prompt template from {filename}: {e}")
            raise
    
    def get_chat_prompt(self, question: str) -> str:
        """Get formatted chat prompt with user question."""
        try:
            # Use new Pydantic config if available
            if hasattr(self, 'chat_config') and self.chat_config:
                prompt_template = self.chat_config.CHAT_PROMPT_V1.prompt
                formatted_prompt = prompt_template.replace('{question}', question)
                return formatted_prompt
            # Fallback to legacy method
            elif hasattr(self, 'chat_prompt') and self.chat_prompt:
                formatted_prompt = self.chat_prompt.replace('{question}', question)
                return formatted_prompt
            else:
                raise AttributeError("No chat prompt configuration available")
        except Exception as e:
            logger.error(f"Error formatting chat prompt: {e}")
            # Ultimate fallback prompt
            return f"You are a helpful AI assistant. Please answer this question: {question}"
    
    def get_syntax_prompt(self, code: str, language: str) -> str:
        """Get formatted syntax analysis prompt."""
        if self.code_review_config:
            return self.code_review_config.SYNTAX_ANALYSIS.prompt.format(code=code, language=language)
        elif hasattr(self, 'syntax_prompt'):
            return self.syntax_prompt.format(code=code, language=language)
        else:
            return f"Analyze this {language} code for syntax issues:\n\n```{language}\n{code}\n```"
    
    def get_style_prompt(self, code: str, language: str) -> str:
        """Get formatted style check prompt."""
        if self.code_review_config:
            return self.code_review_config.STYLE_CHECK.prompt.format(code=code, language=language)
        elif hasattr(self, 'format_prompt'):
            return self.format_prompt.format(code=code, language=language)
        else:
            return f"Analyze this {language} code for style issues:\n\n```{language}\n{code}\n```"
    
    def get_comment_quality_prompt(self, code: str, language: str) -> str:
        """Get formatted comment quality prompt."""
        if self.code_review_config:
            return self.code_review_config.COMMENT_QUALITY.prompt.format(code=code, language=language)
        elif hasattr(self, 'comment_quality_prompt'):
            return self.comment_quality_prompt.format(code=code, language=language)
        else:
            return f"Analyze this {language} code for documentation quality:\n\n```{language}\n{code}\n```"
    
    def get_security_prompt(self, code: str, language: str) -> str:
        """Get formatted security scan prompt."""
        if self.code_review_config:
            return self.code_review_config.SECURITY_SCAN.prompt.format(code=code, language=language)
        elif hasattr(self, 'security_scan_prompt'):
            return self.security_scan_prompt.format(code=code, language=language)
        else:
            return f"Analyze this {language} code for security issues:\n\n```{language}\n{code}\n```"
    
    def get_performance_prompt(self, code: str, language: str) -> str:
        """Get formatted performance analysis prompt."""
        if self.code_review_config:
            return self.code_review_config.PERFORMANCE_ANALYSIS.prompt.format(code=code, language=language)
        elif hasattr(self, 'performance_prompt'):
            return self.performance_prompt.format(code=code, language=language)
        else:
            return f"Analyze this {language} code for performance issues:\n\n```{language}\n{code}\n```"
    
    def get_best_practices_prompt(self, code: str, language: str) -> str:
        """Get formatted best practices prompt."""
        if self.code_review_config:
            return self.code_review_config.BEST_PRACTICES.prompt.format(code=code, language=language)
        elif hasattr(self, 'best_practices_prompt'):
            return self.best_practices_prompt.format(code=code, language=language)
        else:
            return f"Analyze this {language} code for best practices:\n\n```{language}\n{code}\n```"
    
    def get_explanation_prompt(self, code: str, language: str) -> str:
        """Get formatted explanation prompt."""
        if self.code_review_config:
            return self.code_review_config.EXPLANATIONS.prompt.format(code=code, language=language)
        elif hasattr(self, 'explanation_prompt'):
            return self.explanation_prompt.format(code=code, language=language)
        else:
            return f"Explain this {language} code:\n\n```{language}\n{code}\n```"