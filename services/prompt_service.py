import yaml
from pathlib import Path
from langchain.prompts import PromptTemplate
from loguru import logger


class PromptService:
    def __init__(self):
        self.prompts_dir = Path("prompts")
        self._setup_prompts()
    
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
    
    def _setup_prompts(self):
        """Initialize all prompt templates from YAML files."""
        logger.info("Loading prompt templates from YAML files")
        
        try:
            self.syntax_prompt = self._load_prompt_template("syntax_analysis.yml")
            self.format_prompt = self._load_prompt_template("style_check.yml")
            self.comment_quality_prompt = self._load_prompt_template("comment_quality.yml")
            self.security_scan_prompt = self._load_prompt_template("security_scan.yml")
            self.performance_prompt = self._load_prompt_template("performance_analysis.yml")
            self.best_practices_prompt = self._load_prompt_template("best_practices.yml")
            self.explanation_prompt = self._load_prompt_template("explanations.yml")
            
            logger.success("All prompt templates loaded successfully from YAML files")
            
        except Exception as e:
            logger.critical(f"Failed to load prompt templates: {e}")
            raise