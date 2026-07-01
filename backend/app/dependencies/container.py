from dependency_injector import containers, providers
from app.database.connection import DatabaseConnection


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container.
    """
    wiring_config = containers.WiringConfiguration(packages=["app.api", "app.services", "app.repositories"])

    # Core Providers
    db_client = providers.Singleton(DatabaseConnection.get_db)
    
    # Repositories
    
    # Services
    
    # Blockchain
