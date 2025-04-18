#!/usr/bin/env python3
"""Script para inicializar o banco de dados."""

import os
import sys
import logging
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

# Configura o logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.database import Base, engine
from src.database.models import *  # This ensures all models are imported

def main():
    """Função principal para inicializar o banco de dados."""
    try:
        # Remove o arquivo do banco de dados se ele existir
        db_path = Path("instrumentos.db")
        if db_path.exists():
            os.remove(db_path)
            logger.info("Arquivo do banco de dados removido.")

        # Cria todas as tabelas
        Base.metadata.create_all(engine)
        logger.info("Tabelas criadas com sucesso!")

    except Exception as e:
        logger.error(f"Erro ao criar as tabelas: {e}")
        raise

if __name__ == "__main__":
    main() 