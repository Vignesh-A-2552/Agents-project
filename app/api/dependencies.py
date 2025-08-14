from dependency_injector.wiring import Provide, inject

from app.config.container import Container

@inject
def get_auth_service(auth_service=Provide[Container.auth_service]
):
    """Dependency injection for AuthService."""
    return auth_service

@inject
def get_conversation_service(conversation_service=Provide[Container.conversation_service]
):
    """Dependency injection for ConversationService."""
    return conversation_service

@inject
def get_document_loader_service(document_loader_service=Provide[Container.document_loader_service]
):
    """Dependency injection for DocumentLoaderService."""
    return document_loader_service

@inject
def get_vectordb_service(vectordb_service=Provide[Container.vectordb_service]
):
    """Dependency injection for VectorDBService."""
    return vectordb_service

@inject
async def get_code_review_service(code_review_service=Provide[Container.code_review_service]
):
    """Dependency injection for CodeReviewService."""
    return code_review_service
