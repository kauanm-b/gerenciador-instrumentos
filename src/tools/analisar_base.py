#!/usr/bin/env python
"""
Script para analisar a base de dados de instrumentos.
"""
import logging
import json
from datetime import datetime
from typing import List, Dict, Any
from src.database.repository import InstrumentoRepository
from src.database.models import Instrumento
from src.database.database import SessionLocal

# Configuração de logging
logger = logging.getLogger(__name__)

def main():
    """Função principal."""
    try:
        logger.info("Iniciando análise da base de dados...")
        
        # Criar sessão do banco de dados
        db = SessionLocal()
        try:
            # Criar repositório com a sessão
            repo = InstrumentoRepository(db)
            
            # Carregar dados do JSON mais recente
            with open("data/json/instrumentos.json", "r", encoding="utf-8") as f:
                instrumentos = json.load(f)
            
            logger.info(f"Carregados {len(instrumentos)} instrumentos do JSON")
            
            # Converte os dados para objetos do modelo
            instrumentos_db = []
            for inst in instrumentos:
                # Converte a data de validade se existir
                validade = None
                if inst.get('ValidadeCertificado') and inst.get('ValidadeCertificado') != '-':
                    try:
                        # Tenta converter a data ISO 8601 para objeto date
                        validade = datetime.strptime(inst['ValidadeCertificado'], '%Y-%m-%d').date()
                    except ValueError as e:
                        logger.warning(f"Data de validade inválida para o instrumento {inst.get('Instrumento')}: {inst.get('ValidadeCertificado')}")
                
                # Cria instância do modelo Instrumento
                instrumento = Instrumento(
                    spg=inst.get('SPG'),
                    ensaio=inst.get('Ensaio'),
                    nome=inst.get('Instrumento'),
                    tipo=inst.get('Tipo'),
                    marca=inst.get('Marca'),
                    modelo=inst.get('Modelo'),
                    numero_serie=inst.get('Número de Série'),
                    localizacao=inst.get('Localização'),
                    faixa=inst.get('Faixa'),
                    unidade=inst.get('Unidade'),
                    status=inst.get('Status'),
                    classe=inst.get('Classe'),
                    certificado=inst.get('Certificado'),
                    descricao=inst.get('Descrição'),
                    validade_certificado=validade,
                    criterio_aceitacao=inst.get('CriterioAceitacao'),
                    intervalo_operacao=inst.get('IntervaloOperacao')
                )
                instrumentos_db.append(instrumento)
            
            # Salva os instrumentos no banco de dados
            logger.info("Iniciando salvamento em massa...")
            repo.criar_em_massa(instrumentos_db)
            
            logger.info("Dados salvos com sucesso!")
            
        finally:
            # Sempre fecha a sessão
            db.close()
            
    except Exception as e:
        logger.error(f"Erro ao analisar base: {str(e)}")
        raise

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Executar função principal
    main() 