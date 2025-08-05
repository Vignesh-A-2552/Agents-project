from dependency_injector.wiring import Provide, inject
from services.auth_service import AuthService
from services.chat_service import ChatService
from config.container import Container

@inject
def get_auth_service(
    auth_service = Provide[Container.auth_service]
):
    """Dependency injection for AuthService."""
    return auth_service

@inject
def get_chat_service(
    chat_service = Provide[Container.chat_service]
):
    """Dependency injection for ChatService."""
    return chat_service

@inject
def get_document_loader_service(
    document_loader_service = Provide[Container.document_loader_service]
):
    """Dependency injection for DocumentLoaderService."""
    return document_loader_service

@inject
def get_vectordb_service(
    vectordb_service = Provide[Container.vectordb_service]
):
    """Dependency injection for VectorDBService."""
    return vectordb_service
