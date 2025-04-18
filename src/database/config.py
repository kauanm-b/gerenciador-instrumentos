"""
Configuração do banco de dados.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Configuração do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///instrumentos.db')

# Criar engine do SQLAlchemy
engine = create_engine(DATABASE_URL)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar base para os modelos
Base = declarative_base()

def get_db():
    """Retorna uma sessão do banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializa o banco de dados criando todas as tabelas."""
    Base.metadata.create_all(bind=engine) 