from dependency_injector.wiring import Provide, inject
from services.auth_service import AuthService
from config.container import Container

@inject
def get_auth_service(
    auth_service: AuthService = Provide[Container.auth_service]
) -> AuthService:
    """Dependency injection for AuthService."""
    return auth_service

