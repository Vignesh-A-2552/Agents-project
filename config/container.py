from dependency_injector import containers, providers
from services.auth_service import AuthService
from core.llm_service import LLMService
from core.prompt_service import PromptService
from services.code_review_service import CodeReviewService
from services.chat_service import ChatService
from Infrastructure.client.auth_repository import AuthRepository
from config.settings import settings
from services.document_loader_service import DocumentLoaderService
from services.vectordb_service import VectorDBService


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
    
    # Composite Services - Factory provides callable to create instances
    code_review_service = providers.Factory(
        CodeReviewService,
        llm_service=llm_service,
        prompt_service=prompt_service
    )
    
    # Authentication Service
    auth_service = providers.Singleton(
        AuthService,
        repo=auth_repository
    )
    
    # Chat Service
    chat_service = providers.Factory(
        ChatService,
        llm_service=llm_service,
        prompt_service=prompt_service,
        vectordb_service=vectordb_service
    )

    # Document Loader Service
    document_loader_service = providers.Factory(
        DocumentLoaderService,
        vectordb_service=vectordb_service
    )
    