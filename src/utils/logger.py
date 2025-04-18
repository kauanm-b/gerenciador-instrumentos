"""
Módulo de configuração de logging.
"""
import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logger(
    level: int = logging.INFO,
    log_file: bool = True,
    console: bool = True
) -> logging.Logger:
    """
    Configura e retorna um logger.
    
    Args:
        level: Nível de logging (default: logging.INFO)
        log_file: Se True, salva logs em arquivo (default: True)
        console: Se True, exibe logs no console (default: True)
        
    Returns:
        Logger configurado
    """
    # Criar logger
    logger = logging.getLogger('instrumentos')
    logger.setLevel(level)
    
    # Formato do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Adicionar handler de console se solicitado
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Adicionar handler de arquivo se solicitado
    if log_file:
        # Criar diretório de logs se não existir
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Nome do arquivo de log com data
        data_atual = datetime.now().strftime('%Y%m%d')
        log_file = log_dir / f'instrumentos_{data_atual}.log'
        
        # Configurar handler de arquivo
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger 