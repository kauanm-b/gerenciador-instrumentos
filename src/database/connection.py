"""
Conexão com o banco de dados.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Classe para gerenciar a conexão com o banco de dados."""
    
    def __init__(self, db_url=None):
        """
        Inicializa a conexão com o banco de dados.
        
        Args:
            db_url (str, optional): URL de conexão com o banco de dados.
                Se não fornecida, usa a variável de ambiente DATABASE_URL.
        """
        self.db_url = db_url or os.getenv('DATABASE_URL', 'sqlite:///instrumentos.db')
        self.engine = None
        self.Session = None
        
    def connect(self):
        """Estabelece a conexão com o banco de dados."""
        try:
            self.engine = create_engine(self.db_url)
            self.Session = sessionmaker(bind=self.engine)
            logger.info(f"Conexão estabelecida com o banco de dados: {self.db_url}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
            return False
            
    def get_session(self):
        """
        Retorna uma sessão do banco de dados.
        
        Returns:
            Session: Sessão do SQLAlchemy.
        """
        if not self.Session:
            if not self.connect():
                raise Exception("Não foi possível estabelecer conexão com o banco de dados")
        return self.Session()
        
    def create_tables(self, Base):
        """
        Cria as tabelas no banco de dados.
        
        Args:
            Base: Classe base dos modelos SQLAlchemy.
        """
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Tabelas criadas com sucesso")
        except SQLAlchemyError as e:
            logger.error(f"Erro ao criar tabelas: {str(e)}")
            raise
            
    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.engine:
            self.engine.dispose()
            logger.info("Conexão com o banco de dados fechada") 