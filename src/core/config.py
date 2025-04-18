"""
Módulo responsável pelas configurações do sistema.
"""
from pathlib import Path

# Diretórios
DIR_BASE = Path(__file__).parent.parent.parent
DIR_DATA = DIR_BASE / "data"
DIR_OUTPUT = DIR_DATA / "output"
DIR_INPUT = DIR_DATA / "input"

# Configurações de Excel
ORDEM_COLUNAS = [
    "Tipo",
    "Identificação",
    "Marca",
    "Modelo",
    "Número de Série",
    "Capacidade",
    "Divisão",
    "Classe",
    "Status",
    "Certificado",
    "Validade",
    "Spg e Ensaio"
]

# Configurações de formatação
FORMATO_TITULO = {
    "font": "Arial",
    "size": 14,
    "bold": True,
    "align": "center",
    "valign": "center"
}

FORMATO_CABECALHO = {
    "font": "Arial",
    "size": 11,
    "bold": True,
    "align": "center",
    "valign": "center",
    "bg_color": "#1F4E78",
    "font_color": "white"
}

FORMATO_DADOS = {
    "font": "Arial",
    "size": 10,
    "align": "center",
    "valign": "center"
}

# Configurações de cores para formatação condicional
CORES_STATUS = {
    "ATIVO": "#00B050",  # Verde
    "BLOQUEADO": "#FF0000"  # Vermelho
}

CORES_CERTIFICADO = {
    "valido": "#00B050",  # Verde
    "expirado": "#FFC000",  # Amarelo
    "sem_certificado": "#FF0000"  # Vermelho
} 