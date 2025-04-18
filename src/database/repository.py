"""Repositório para operações com instrumentos."""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import Instrumento

logger = logging.getLogger(__name__)

class InstrumentoRepository:
    """Repositório para operações com instrumentos."""

    def __init__(self, db: Session):
        """Inicializa o repositório com uma sessão do banco de dados."""
        self.db = db

    def criar(self, instrumento: Instrumento) -> Instrumento:
        """Cria um novo instrumento no banco de dados."""
        try:
            self.db.add(instrumento)
            self.db.commit()
            self.db.refresh(instrumento)
            logger.info(f"Instrumento criado com sucesso: {instrumento.id}")
            return instrumento
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar instrumento: {e}")
            raise

    def criar_em_massa(self, instrumentos: List[Instrumento]) -> List[Instrumento]:
        """Cria múltiplos instrumentos no banco de dados."""
        try:
            self.db.bulk_save_objects(instrumentos)
            self.db.commit()
            logger.info(f"{len(instrumentos)} instrumentos criados com sucesso")
            return instrumentos
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar instrumentos em massa: {e}")
            raise

    def obter_por_id(self, instrumento_id: int) -> Optional[Instrumento]:
        """Obtém um instrumento pelo ID."""
        return self.db.query(Instrumento).filter(Instrumento.id == instrumento_id).first()

    def listar_todos(self) -> List[Instrumento]:
        """Lista todos os instrumentos."""
        return self.db.query(Instrumento).all()

    def atualizar(self, instrumento_id: int, dados: Dict[str, Any]) -> Optional[Instrumento]:
        """Atualiza um instrumento existente."""
        try:
            instrumento = self.obter_por_id(instrumento_id)
            if instrumento:
                for chave, valor in dados.items():
                    setattr(instrumento, chave, valor)
                self.db.commit()
                self.db.refresh(instrumento)
                logger.info(f"Instrumento {instrumento_id} atualizado com sucesso")
            return instrumento
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar instrumento {instrumento_id}: {e}")
            raise

    def deletar(self, instrumento_id: int) -> bool:
        """Deleta um instrumento pelo ID."""
        try:
            instrumento = self.obter_por_id(instrumento_id)
            if instrumento:
                self.db.delete(instrumento)
                self.db.commit()
                logger.info(f"Instrumento {instrumento_id} deletado com sucesso")
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao deletar instrumento {instrumento_id}: {e}")
            raise

    def obter_por_spg(self, spg: str) -> List[Instrumento]:
        """Obtém instrumentos por SPG."""
        return self.db.query(Instrumento).filter(Instrumento.spg == spg).all()

    def obter_por_ensaio(self, ensaio: str) -> List[Instrumento]:
        """Obtém instrumentos por ensaio."""
        return self.db.query(Instrumento).filter(Instrumento.ensaio == ensaio).all()

    def obter_por_tipo(self, tipo: str) -> List[Instrumento]:
        """Obtém instrumentos por tipo."""
        return self.db.query(Instrumento).filter(Instrumento.tipo == tipo).all()

    def obter_por_status(self, status: str) -> List[Instrumento]:
        """Obtém instrumentos por status."""
        return self.db.query(Instrumento).filter(Instrumento.status == status).all()

    def obter_por_numero_serie(self, numero_serie: str) -> Optional[Instrumento]:
        """Obtém um instrumento pelo número de série."""
        return self.db.query(Instrumento).filter(Instrumento.numero_serie == numero_serie).first()

    def importar_dados_json(self, dados: List[Dict[str, Any]]) -> List[Instrumento]:
        """Importa dados de instrumentos a partir de uma lista de dicionários."""
        try:
            instrumentos = []
            for item in dados:
                instrumento = Instrumento(**item)
                instrumentos.append(instrumento)
            return self.criar_em_massa(instrumentos)
        except Exception as e:
            logger.error(f"Erro ao importar dados JSON: {e}")
            raise 