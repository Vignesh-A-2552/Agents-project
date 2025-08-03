from dependency_injector import containers, providers
from services.auth_service import AuthService
from services.llm_service import LLMService
from services.prompt_service import PromptService
from services.code_review_service import CodeReviewService
from Infrastructure.client.AuthRepository import AuthRepository
from config.settings import settings


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
    