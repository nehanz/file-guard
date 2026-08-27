from dependency_injector import containers, providers
from app.database.connection import DatabaseConnection
from app.repositories.user import UserRepository
from app.repositories.token import RefreshTokenRepository
from app.repositories.log import ActivityLogRepository
from app.repositories.file import FileRepository
from app.services.auth import AuthService
from app.services.user import UserService
from app.services.file import FileService
from app.blockchain.client import BlockchainClient
from app.core.config import settings


def get_blockchain_client_or_none():
    """Factory function that returns BlockchainClient if configured, else None."""
    if settings.CONTRACT_ADDRESS and settings.ETH_PRIVATE_KEY and settings.WEB3_PROVIDER_URI:
        try:
            return BlockchainClient()
        except Exception as e:
            print(f"Warning: Blockchain client initialization failed: {e}")
            return None
    return None


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
    activity_log_repo = providers.Factory(ActivityLogRepository, db=db_client)
    file_repo = providers.Factory(FileRepository, db=db_client)

    # Blockchain
    blockchain_client = providers.Singleton(get_blockchain_client_or_none)

    # Services
    auth_service = providers.Factory(AuthService, user_repo=user_repo, token_repo=token_repo)
    user_service = providers.Factory(UserService, user_repo=user_repo, activity_log_repo=activity_log_repo)
    file_service = providers.Factory(FileService, file_repo=file_repo, activity_log_repo=activity_log_repo, blockchain_client=blockchain_client)
