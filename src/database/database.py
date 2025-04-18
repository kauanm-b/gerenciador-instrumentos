"""
Configuração do banco de dados usando SQLAlchemy.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

# URL do banco de dados (SQLite por padrão)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///instrumentos.db")

# Garantir que o diretório do banco de dados exista
if DATABASE_URL.startswith("sqlite:///"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:  # Se há um diretório especificado
        os.makedirs(db_dir, exist_ok=True)
        logger.info(f"Diretório do banco de dados criado/verificado: {db_dir}")

# Cria o engine do SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)

# Cria a sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria a base para os modelos
Base = declarative_base()

def init_db(force_recreate=False):
    """
    Inicializa o banco de dados criando todas as tabelas.
    
    Args:
        force_recreate (bool): Se True, remove o banco de dados existente antes de criar um novo.
                             Se False, apenas cria as tabelas se elas não existirem.
    """
    try:
        # Importar modelos para garantir que eles sejam registrados
        from .models import Instrumento
        
        if force_recreate and DATABASE_URL.startswith("sqlite:///"):
            db_path = DATABASE_URL.replace("sqlite:///", "")
            if os.path.exists(db_path):
                os.remove(db_path)
                logger.info("Banco de dados existente removido")
            
            # Garantir que o diretório exista após remoção
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Diretório do banco de dados recriado: {db_dir}")
        
        # Criar tabelas
        Base.metadata.create_all(bind=engine)
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
        raise

def get_db():
    """
    Função para obter uma sessão do banco de dados.
    
    Yields:
        Session: Sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def close_db():
    """Fecha a conexão com o banco de dados."""
    SessionLocal.remove()
    logger.info("Conexão com o banco de dados fechada") 