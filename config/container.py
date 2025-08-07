from dependency_injector import containers, providers
from services.auth_service import AuthService
from core.llm_service import LLMService
from core.prompt_service import PromptService
from services.code_review_service import CodeReviewService
from services.conversation_service import ConversationService
from Infrastructure.client.auth_repository import AuthRepository
from config.settings import settings
from services.document_loader_service import DocumentLoaderService
from services.vectordb_service import VectorDBService
from agents.code_review_agent.CodeReviewAgent import CodeReviewAgent
from agents.conversation_agent.ConversationAgent import ConversationAgent


class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()
    
    # Repository
    auth_repository = providers.Singleton(
        AuthRepository,
        connection_string=settings.DATABASE_URL
    )
    
    # Core Services
    llm_service = providers.Singleton(LLMService)
    
    prompt_service = providers.Singleton(PromptService)
    
    vectordb_service = providers.Singleton(VectorDBService)
    

    # Agents
    code_review_agent = providers.Factory(
        CodeReviewAgent,
        llm_service=llm_service,
        prompt_service=prompt_service
    )

    conversation_agent = providers.Factory(
        ConversationAgent,
        llm_service=llm_service,
        prompt_service=prompt_service,
        vectordb_service=vectordb_service
    )
    
    # Composite Services - Factory provides callable to create instances
   
    # Authentication Service
    auth_service = providers.Singleton(
        AuthService,
        repo=auth_repository
    )

    # Document Loader Service
    document_loader_service = providers.Factory(
        DocumentLoaderService,
        vectordb_service=vectordb_service
    )

    # Code Review Service
    code_review_service = providers.Factory(
        CodeReviewService,
        code_review_agent=code_review_agent
    )

    # Conversation Service
    conversation_service = providers.Factory(
        ConversationService,
        conversation_agent=conversation_agent
    )