from .llm_service import LLMService
from .prompt_service import PromptService
from loguru import logger
class ChatService:
    """Service class for handling chat-related operations."""

    def __init__(self, llm_service: LLMService = None, prompt_service: PromptService = None):
        # Initialize any required resources, e.g., chat model, database connections, etc.
        self.llm_service = llm_service
        self.prompt_service = prompt_service

    def ask_question(self, question: str) -> str:
        """Ask a question to the chat model and get a response."""
        try:
            # Get the chat prompt template
            chat_prompt = self.prompt_service.get_chat_prompt(question)
            logger.debug(f"Generated chat prompt: {chat_prompt}")
            
            # Generate response using LLM service
            response = self.llm_service.model.invoke(chat_prompt)
            logger.debug(f"Raw LLM response: {repr(response)}")
            
            # Handle different response types from langchain
            if hasattr(response, 'content'):
                response_text = response.content
            elif isinstance(response, str):
                response_text = response
            else:
                response_text = str(response)
            
            response_text = response_text.strip()
            
            # Ensure response is not empty
            if not response_text:
                return "I apologize, but I couldn't generate a proper response. Please try asking your question again."
            
            return response_text
        except Exception as e:
            # Fallback response if AI service fails
            return f"I'm sorry, I'm having trouble processing your question right now. Please try again later. Error: {str(e)}"
