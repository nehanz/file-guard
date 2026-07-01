from dependency_injector import containers, providers
from app.database.connection import DatabaseConnection
from app.repositories.user import UserRepository
from app.repositories.token import RefreshTokenRepository
from app.services.auth import AuthService


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container.
    """
    wiring_config = containers.WiringConfiguration(packages=["app.api", "app.services", "app.repositories", "app.dependencies"])

    # Core Providers
    db_client = providers.Singleton(DatabaseConnection.get_db)
    
    # Repositories
    user_repo = providers.Factory(UserRepository, db=db_client)
    token_repo = providers.Factory(RefreshTokenRepository, db=db_client)
    
    # Services
    auth_service = providers.Factory(AuthService, user_repo=user_repo, token_repo=token_repo)
    
    # Blockchain
