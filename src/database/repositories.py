"""
Repositórios para acesso aos dados.
"""
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from .models import SPG, Ensaio, Instrumento, HistoricoInstrumento

logger = logging.getLogger(__name__)

class SPGRepository:
    """Repositório para operações com SPGs."""
    
    def __init__(self, session):
        self.session = session
        
    def criar(self, dados: Dict[str, Any]) -> Optional[SPG]:
        """
        Cria um novo SPG.
        
        Args:
            dados: Dicionário com os dados do SPG.
            
        Returns:
            SPG: Objeto SPG criado ou None em caso de erro.
        """
        try:
            spg = SPG(**dados)
            self.session.add(spg)
            self.session.commit()
            return spg
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Erro ao criar SPG: {str(e)}")
            return None
            
    def buscar_por_codigo(self, codigo: str) -> Optional[SPG]:
        """
        Busca um SPG pelo código.
        
        Args:
            codigo: Código do SPG.
            
        Returns:
            SPG: Objeto SPG encontrado ou None.
        """
        return self.session.query(SPG).filter(SPG.codigo == codigo).first()
        
    def listar_todos(self) -> List[SPG]:
        """
        Lista todos os SPGs.
        
        Returns:
            List[SPG]: Lista de SPGs.
        """
        return self.session.query(SPG).all()
        
    def atualizar(self, spg: SPG, dados: Dict[str, Any]) -> bool:
        """
        Atualiza um SPG.
        
        Args:
            spg: Objeto SPG a ser atualizado.
            dados: Dicionário com os novos dados.
            
        Returns:
            bool: True se a atualização foi bem sucedida.
        """
        try:
            for chave, valor in dados.items():
                setattr(spg, chave, valor)
            spg.data_atualizacao = datetime.now()
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Erro ao atualizar SPG: {str(e)}")
            return False
            
    def excluir(self, spg: SPG) -> bool:
        """
        Exclui um SPG.
        
        Args:
            spg: Objeto SPG a ser excluído.
            
        Returns:
            bool: True se a exclusão foi bem sucedida.
        """
        try:
            self.session.delete(spg)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Erro ao excluir SPG: {str(e)}")
            return False

class EnsaioRepository:
    """Repositório para operações com Ensaios."""
    
    def __init__(self, session):
        self.session = session
        
    def criar(self, dados: Dict[str, Any]) -> Optional[Ensaio]:
        """
        Cria um novo Ensaio.
        
        Args:
            dados: Dicionário com os dados do Ensaio.
            
        Returns:
            Ensaio: Objeto Ensaio criado ou None em caso de erro.
        """
        try:
            ensaio = Ensaio(**dados)
            self.session.add(ensaio)
            self.session.commit()
            return ensaio
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Erro ao criar Ensaio: {str(e)}")
            return None
            
    def buscar_por_codigo(self, codigo: str) -> Optional[Ensaio]:
        """
        Busca um Ensaio pelo código.
        
        Args:
            codigo: Código do Ensaio.
            
        Returns:
            Ensaio: Objeto Ensaio encontrado ou None.
        """
        return self.session.query(Ensaio).filter(Ensaio.codigo == codigo).first()
        
    def listar_por_spg(self, spg_id: int) -> List[Ensaio]:
        """
        Lista todos os Ensaios de um SPG.
        
        Args:
            spg_id: ID do SPG.
            
        Returns:
            List[Ensaio]: Lista de Ensaios.
        """
        return self.session.query(Ensaio).filter(Ensaio.spg_id == spg_id).all()
        
    def atualizar(self, ensaio: Ensaio, dados: Dict[str, Any]) -> bool:
        """
        Atualiza um Ensaio.
        
        Args:
            ensaio: Objeto Ensaio a ser atualizado.
            dados: Dicionário com os novos dados.
            
        Returns:
            bool: True se a atualização foi bem sucedida.
        """
        try:
            for chave, valor in dados.items():
                setattr(ensaio, chave, valor)
            ensaio.data_atualizacao = datetime.now()
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Erro ao atualizar Ensaio: {str(e)}")
            return False
            
    def excluir(self, ensaio: Ensaio) -> bool:
        """
        Exclui um Ensaio.
        
        Args:
            ensaio: Objeto Ensaio a ser excluído.
            
        Returns:
            bool: True se a exclusão foi bem sucedida.
        """
        try:
            self.session.delete(ensaio)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Erro ao excluir Ensaio: {str(e)}")
            return False

class InstrumentoRepository:
    """Repositório para operações com Instrumentos."""
    
    def __init__(self, session):
        self.session = session
        
    def criar(self, dados: Dict[str, Any]) -> Optional[Instrumento]:
        """
        Cria um novo Instrumento.
        
        Args:
            dados: Dicionário com os dados do Instrumento.
            
        Returns:
            Instrumento: Objeto Instrumento criado ou None em caso de erro.
        """
        try:
            instrumento = Instrumento(**dados)
            self.session.add(instrumento)
            self.session.commit()
            return instrumento
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Erro ao criar Instrumento: {str(e)}")
            return None
            
    def buscar_por_identificacao(self, identificacao: str) -> Optional[Instrumento]:
        """
        Busca um Instrumento pela identificação.
        
        Args:
            identificacao: Identificação do Instrumento.
            
        Returns:
            Instrumento: Objeto Instrumento encontrado ou None.
        """
        return self.session.query(Instrumento).filter(
            Instrumento.identificacao == identificacao
        ).first()
        
    def listar_por_spg(self, spg_id: int) -> List[Instrumento]:
        """
        Lista todos os Instrumentos de um SPG.
        
        Args:
            spg_id: ID do SPG.
            
        Returns:
            List[Instrumento]: Lista de Instrumentos.
        """
        return self.session.query(Instrumento).filter(
            Instrumento.spg_id == spg_id
        ).all()
        
    def listar_por_ensaio(self, ensaio_id: int) -> List[Instrumento]:
        """
        Lista todos os Instrumentos de um Ensaio.
        
        Args:
            ensaio_id: ID do Ensaio.
            
        Returns:
            List[Instrumento]: Lista de Instrumentos.
        """
        return self.session.query(Instrumento).filter(
            Instrumento.ensaio_id == ensaio_id
        ).all()
        
    def atualizar(self, instrumento: Instrumento, dados: Dict[str, Any]) -> bool:
        """
        Atualiza um Instrumento.
        
        Args:
            instrumento: Objeto Instrumento a ser atualizado.
            dados: Dicionário com os novos dados.
            
        Returns:
            bool: True se a atualização foi bem sucedida.
        """
        try:
            for chave, valor in dados.items():
                if getattr(instrumento, chave) != valor:
                    # Registra o histórico da alteração
                    historico = HistoricoInstrumento(
                        instrumento_id=instrumento.id,
                        campo_alterado=chave,
                        valor_anterior=str(getattr(instrumento, chave)),
                        valor_novo=str(valor)
                    )
                    self.session.add(historico)
                    setattr(instrumento, chave, valor)
            
            instrumento.data_atualizacao = datetime.now()
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Erro ao atualizar Instrumento: {str(e)}")
            return False
            
    def excluir(self, instrumento: Instrumento) -> bool:
        """
        Exclui um Instrumento.
        
        Args:
            instrumento: Objeto Instrumento a ser excluído.
            
        Returns:
            bool: True se a exclusão foi bem sucedida.
        """
        try:
            self.session.delete(instrumento)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Erro ao excluir Instrumento: {str(e)}")
            return False
            
    def buscar_por_filtros(self, filtros: Dict[str, Any]) -> List[Instrumento]:
        """
        Busca instrumentos por filtros.
        
        Args:
            filtros: Dicionário com os filtros de busca.
            
        Returns:
            List[Instrumento]: Lista de instrumentos que atendem aos filtros.
        """
        query = self.session.query(Instrumento)
        
        for campo, valor in filtros.items():
            if valor:
                if isinstance(valor, str):
                    query = query.filter(
                        getattr(Instrumento, campo).ilike(f"%{valor}%")
                    )
                else:
                    query = query.filter(getattr(Instrumento, campo) == valor)
                    
        return query.all()
        
    def listar_historico(self, instrumento_id: int) -> List[HistoricoInstrumento]:
        """
        Lista o histórico de alterações de um instrumento.
        
        Args:
            instrumento_id: ID do instrumento.
            
        Returns:
            List[HistoricoInstrumento]: Lista de registros de histórico.
        """
        return self.session.query(HistoricoInstrumento).filter(
            HistoricoInstrumento.instrumento_id == instrumento_id
        ).order_by(HistoricoInstrumento.data_alteracao.desc()).all() 