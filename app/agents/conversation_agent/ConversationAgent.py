from datetime import datetime
from loguru import logger
from core.llm_service import LLMService
from core.prompt_service import PromptService
from services.vectordb_service import VectorDBService
from models.types import ConversationState
from langgraph.graph import StateGraph, END


class ConversationAgent:
    """Agent class for managing conversations with RAG support using agent architecture."""

    def __init__(self, llm_service: LLMService = None, prompt_service: PromptService = None, vectordb_service: VectorDBService = None):
        logger.info("Initializing Conversation Service")
        self.llm_service = llm_service or LLMService()
        self.prompt_service = prompt_service or PromptService()
        self.vectordb_service = vectordb_service
        logger.success("Conversation Service initialized successfully")

    async def parse_question_input(self, state: ConversationState) -> ConversationState:
        """Parse and validate the input question."""
        logger.info(f"Parsing question input - Use RAG: {state.get('use_rag', True)}")
        start_time = datetime.now()
        
        question = state["question"]
        logger.debug(f"Question length: {len(question)} characters")

        if not question or len(question.strip()) == 0:
            logger.error("Invalid question: empty or whitespace only")
            state["error"] = "Invalid question: empty or whitespace only"
            return state
        
        if len(question) > 10000:
            logger.error(f"Question too long: {len(question)} characters")
            state["error"] = "Question too long (max 10,000 characters)"
            return state

        processing_time = (datetime.now() - start_time).total_seconds()
        state["processing_time"] = processing_time
        logger.success(f"Question input parsed successfully in {processing_time:.3f}s")
        return state

    async def retrieve_context(self, state: ConversationState) -> ConversationState:
        """Retrieve relevant documents using RAG if enabled."""
        if state.get("error"):
            return state
            
        logger.info("Starting context retrieval")
        try:
            if state.get("use_rag", True) and self.vectordb_service:
                question = state["question"]
                logger.debug(f"DEBUG - Searching for query: '{question}'")
                
                # Use search with scores for better debugging
                results_with_scores = self.vectordb_service.search_with_scores(question, k=6)
                logger.debug(f"DEBUG - Found {len(results_with_scores)} documents with scores")
                
                # Log all results with scores
                for i, (doc, score) in enumerate(results_with_scores):
                    logger.debug(f"DEBUG - Document {i+1}: Score={score:.4f}, Source={doc.metadata.get('source_file', 'Unknown')}")
                    logger.debug(f"DEBUG - Content preview: {doc.page_content[:200]}...")
                
                # Filter by similarity threshold (lower scores are more similar in FAISS)
                similarity_threshold = 2.0  # Adjusted threshold to include more results
                relevant_docs = [doc for doc, score in results_with_scores if score < similarity_threshold]
                
                logger.debug(f"DEBUG - After filtering (threshold={similarity_threshold}): {len(relevant_docs)} documents")
                logger.info(f"IMPORTANT DEBUG - Threshold: {similarity_threshold}, Results after filtering: {len(relevant_docs)}")
                
                if relevant_docs:
                    state["relevant_documents"] = relevant_docs
                    context = self._create_context_from_documents(relevant_docs)
                    state["context"] = context
                    logger.info(f"Enhanced prompt with {len(relevant_docs)} relevant documents")
                    logger.debug(f"DEBUG - Final context length: {len(context)} characters")
                    logger.debug(f"DEBUG - Context preview: {context[:300]}...")
                else:
                    logger.warning("No relevant documents found after filtering, using original question")
                    state["context"] = ""
            else:
                logger.info("RAG disabled or vectordb_service not available")
                state["context"] = ""
                
        except Exception as e:
            logger.error(f"Error in context retrieval: {e}")
            state["context"] = ""
        
        return state

    async def enhance_prompt(self, state: ConversationState) -> ConversationState:
        """Enhance the prompt with context and generate the final prompt."""
        if state.get("error"):
            return state
            
        logger.info("Enhancing prompt with context")
        try:
            question = state["question"]
            context = state.get("context", "")
            
            enhanced_prompt = self.prompt_service.get_conversation_prompt(question, context)
            state["enhanced_prompt"] = enhanced_prompt
            logger.debug(f"Generated enhanced prompt: {enhanced_prompt}")
            
        except Exception as e:
            logger.error(f"Error enhancing prompt: {e}")
            state["error"] = f"Error enhancing prompt: {str(e)}"
        
        return state

    async def generate_response(self, state: ConversationState) -> ConversationState:
        """Generate response using LLM service."""
        if state.get("error"):
            return state
            
        logger.info("Generating LLM response")
        try:
            enhanced_prompt = state["enhanced_prompt"]
            
            response = await self.llm_service.model.ainvoke(enhanced_prompt)
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
                state["response"] = "I apologize, but I couldn't generate a proper response. Please try asking your question again."
            else:
                state["response"] = response_text
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            state["error"] = f"Error generating response: {str(e)}"
        
        return state

    async def finalize_output(self, state: ConversationState) -> ConversationState:
        """Finalize the response and handle any errors."""
        if state.get("error"):
            state["response"] = f"I'm sorry, I'm having trouble processing your question right now. Please try again later. Error: {state['error']}"
        
        logger.success("Response generation completed")
        return state

    
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
    
    
    def get_vector_store_status(self) -> dict:
        """Get information about the vector store status."""
        try:
            return self.vectordb_service.get_vector_store_info()
        except Exception as e:
            logger.error(f"Error getting vector store status: {e}")
            return {"status": "error", "error": str(e)}

    async def build_agent(self):
        """Build the conversation workflow graph."""
        logger.info("Building conversation workflow graph")
        workflow = StateGraph(ConversationState)
        
        # Add nodes
        workflow.add_node("parse_input", self.parse_question_input)
        workflow.add_node("retrieve_context", self.retrieve_context)
        workflow.add_node("enhance_prompt", self.enhance_prompt)
        workflow.add_node("generate_response", self.generate_response)
        workflow.add_node("finalize_output", self.finalize_output)

        # Add edges for sequential flow
        workflow.add_edge("parse_input", "retrieve_context")
        workflow.add_edge("retrieve_context", "enhance_prompt")
        workflow.add_edge("enhance_prompt", "generate_response")
        workflow.add_edge("generate_response", "finalize_output")
        workflow.add_edge("finalize_output", END)

        # Set entry point
        workflow.set_entry_point("parse_input")
        
        compiled_workflow = workflow.compile()
        logger.success("Conversation workflow compiled successfully")
        return compiled_workflow

    async def invoke(self, question: str, use_rag: bool = True) -> dict:
        """Process a question using the agent workflow and return structured response."""
        logger.info(f"Processing question - Use RAG: {use_rag}")
        start_time = datetime.now()
        
        try:
            # Create initial state
            initial_state: ConversationState = {
                "question": question,
                "use_rag": use_rag
            }
            
            # Build and execute the workflow
            agent = await self.build_agent()
            result = await agent.ainvoke(initial_state)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Return structured response
            response = {
                "success": True,
                "message": result.get("response", "I apologize, but I couldn't generate a response."),
                "processing_time": processing_time,
                "use_rag": use_rag,
                "context_used": bool(result.get("context", "")),
                "documents_found": len(result.get("relevant_documents", [])),
                "error": None
            }
            
            logger.success(f"Question processed successfully in {processing_time:.3f}s")
            return response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error processing question: {e}", exc_info=True)
            
            return {
                "success": False,
                "message": f"I'm sorry, I'm having trouble processing your question right now. Please try again later.",
                "processing_time": processing_time,
                "use_rag": use_rag,
                "context_used": False,
                "documents_found": 0,
                "error": str(e)
            }
