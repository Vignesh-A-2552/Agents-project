from core.llm_service import LLMService
from core.prompt_service import PromptService
from services.vectordb_service import VectorDBService
from loguru import logger


class ChatService:
    """Service class for handling chat-related operations with RAG support."""

    def __init__(self, llm_service: LLMService = None, prompt_service: PromptService = None, vectordb_service: VectorDBService = None):
        # Initialize any required resources, e.g., chat model, database connections, etc.
        self.llm_service = llm_service
        self.prompt_service = prompt_service
        self.vectordb_service = vectordb_service or VectorDBService()

    def ask_question(self, question: str, use_rag: bool = True) -> str:
        """Ask a question to the chat model with optional RAG support."""
        try:
            enhanced_prompt = question
            
            if use_rag:
                # Retrieve relevant documents
                relevant_docs = self.vectordb_service.search_similar_documents(question, k=4)
                
                if relevant_docs:
                    # Create context from retrieved documents
                    context = self._create_context_from_documents(relevant_docs)
                    enhanced_prompt = self._create_rag_prompt(question, context)
                    logger.info(f"Enhanced prompt with {len(relevant_docs)} relevant documents")
                else:
                    logger.info("No relevant documents found, using original question")
            
            # Get the chat prompt template
            chat_prompt = self.prompt_service.get_chat_prompt(enhanced_prompt)
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
            logger.error(f"Error in ask_question: {e}")
            return f"I'm sorry, I'm having trouble processing your question right now. Please try again later. Error: {str(e)}"
    
    def _create_context_from_documents(self, documents) -> str:
        """Create a context string from retrieved documents."""
        try:
            context_parts = []
            for i, doc in enumerate(documents, 1):
                source_file = doc.metadata.get('source_file', 'Unknown')
                chunk_content = doc.page_content.strip()
                
                context_parts.append(f"[Document {i} - {source_file}]\n{chunk_content}")
            
            context = "\n\n".join(context_parts)
            logger.debug(f"Created context with {len(context)} characters from {len(documents)} documents")
            return context
            
        except Exception as e:
            logger.error(f"Error creating context from documents: {e}")
            return ""
    
    def _create_rag_prompt(self, question: str, context: str) -> str:
        """Create an enhanced prompt combining the question with retrieved context."""
        if not context:
            return question
        
        rag_prompt = f"""Based on the following context from uploaded documents, please answer the question.

Context:
{context}

Question: {question}

Please provide a comprehensive answer based on the context provided. If the context doesn't contain enough information to fully answer the question, please indicate what information is missing and provide the best answer possible with the available context."""
        
        return rag_prompt
    
    def get_vector_store_status(self) -> dict:
        """Get information about the vector store status."""
        try:
            return self.vectordb_service.get_vector_store_info()
        except Exception as e:
            logger.error(f"Error getting vector store status: {e}")
            return {"status": "error", "error": str(e)}
