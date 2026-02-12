"""
Cliente de base de datos para Supabase (PostgreSQL + pgvector)
"""
from typing import Optional
import logging
from supabase import create_client, Client
from config.settings import settings

logger = logging.getLogger(__name__)


class Database:
    """Singleton para conexión a Supabase"""

    _instance: Optional['Database'] = None
    _client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._initialize_client()

    def _initialize_client(self):
        """Inicializa cliente de Supabase"""
        try:
            self._client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_key
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    @property
    def client(self) -> Client:
        """Retorna el cliente de Supabase"""
        if self._client is None:
            self._initialize_client()
        return self._client

    async def health_check(self) -> bool:
        """Verifica conexión a la base de datos"""
        try:
            # Simple query para verificar conectividad
            result = self.client.table('articles').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Singleton instance
db = Database()


def get_db() -> Database:
    """Dependency injection para FastAPI"""
    return db
