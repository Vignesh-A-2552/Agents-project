from dependency_injector import containers, providers
from services.auth_service import AuthService
from Infrastructure.client.AuthRepository import AuthRepository


class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()
    
    # Repository
    auth_repository = providers.Singleton(
        AuthRepository,
        connection_string=""  # Will be handled by BasePostgresRepository
    )
    
    # Services
    auth_service = providers.Singleton(
        AuthService,
        repo=auth_repository
    )
    