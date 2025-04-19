#!/usr/bin/env python
"""
Script para gerenciar a base de dados de instrumentos.
"""
import logging
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any
from src.database.repository import InstrumentoRepository
from src.database.models import Instrumento
from src.database.database import SessionLocal
from src.database.init_db import init_db

# Configuração de logging
logger = logging.getLogger(__name__)

def limpar_arquivo_log(caminho_arquivo):
    """Limpa o conteúdo do arquivo de log."""
    try:
        # Verifica se o arquivo existe
        if os.path.exists(caminho_arquivo):
            # Abre o arquivo em modo de escrita, o que apaga seu conteúdo
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write("")
            print(f"🧹 Arquivo de log limpo: {caminho_arquivo}")
        else:
            print(f"📝 Arquivo de log não encontrado: {caminho_arquivo}")
    except Exception as e:
        print(f"❌ Erro ao limpar arquivo de log: {e}")

def configurar_logging():
    """Configura o sistema de logging para salvar em arquivo e console."""
    # Caminho do arquivo de log
    caminho_log = "logs/instrumentos.log"
    
    # Criar diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    # Limpar o arquivo de log antes de começar
    limpar_arquivo_log(caminho_log)
    
    # Configurar o logger
    logger = logging.getLogger("instrumentos")
    logger.setLevel(logging.INFO)
    
    # Limpar handlers existentes para evitar duplicação
    if logger.handlers:
        logger.handlers.clear()
    
    # Formato do log
    formato = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Handler para arquivo
    arquivo_handler = logging.FileHandler(caminho_log, encoding="utf-8")
    arquivo_handler.setFormatter(formato)
    logger.addHandler(arquivo_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formato)
    logger.addHandler(console_handler)
    
    return logger

def main():
    """Função principal."""
    # Registrar início da execução
    tempo_inicio = time.time()
    
    try:
        # Configurar logging
        logger = configurar_logging()
        
        logger.info("=" * 50)
        logger.info("INICIANDO PROCESSO DE GERENCIAMENTO DE INSTRUMENTOS")
        logger.info("=" * 50)
        
        # Inicializa o banco de dados se necessário
        logger.info("🔍 Verificando banco de dados...")
        init_db()
        logger.info("✅ Banco de dados verificado com sucesso!")
        
        # Criar sessão do banco de dados
        db = SessionLocal()
        try:
            # Criar repositório com a sessão
            repo = InstrumentoRepository(db)
            
            # Carregar dados do JSON mais recente
            logger.info("📂 Carregando dados do arquivo JSON...")
            with open("data/json/instrumentos.json", "r", encoding="utf-8") as f:
                instrumentos = json.load(f)
            
            logger.info(f"📊 Carregados {len(instrumentos)} instrumentos do JSON")
            
            # Sincronizar os dados do JSON com o banco de dados
            logger.info("🔄 Iniciando sincronização de dados...")
            estatisticas = repo.sincronizar_dados(instrumentos)
            
            # Calcular tempo de execução
            tempo_execucao = time.time() - tempo_inicio
            
            # Resumo da operação
            logger.info("=" * 50)
            logger.info("RESUMO DA OPERAÇÃO")
            logger.info("=" * 50)
            logger.info(f"📝 Instrumentos processados: {len(instrumentos)}")
            logger.info(f"➕ Novos instrumentos adicionados: {estatisticas['adicionados']}")
            logger.info(f"🔄 Instrumentos atualizados: {estatisticas['atualizados']}")
            logger.info(f"➖ Instrumentos removidos: {estatisticas['removidos']}")
            logger.info(f"⚠️ Avisos gerados: {estatisticas['avisos']}")
            logger.info(f"⏱️ Tempo de execução: {tempo_execucao:.2f} segundos")
            logger.info("=" * 50)
            logger.info("✅ Sincronização concluída com sucesso!")
            logger.info("=" * 50)
            
        finally:
            # Sempre fecha a sessão
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao gerenciar base: {str(e)}")
        raise

if __name__ == "__main__":
    # Executar função principal
    main() 