"""
Script para inicializar o banco de dados e criar as tabelas.
"""
import logging
from .database import init_db as init_database

logger = logging.getLogger(__name__)

def init_db():
    """Inicializa o banco de dados criando todas as tabelas."""
    try:
        logger.info("Inicializando banco de dados...")
        init_database()
        logger.info("Banco de dados inicializado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
        raise

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Inicializar banco de dados
    init_db() 