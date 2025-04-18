"""
Módulo responsável pelo gerenciamento de dados.
"""
from pathlib import Path
from typing import List, Optional

import pandas as pd


class DataManager:
    """Classe responsável pelo gerenciamento de dados."""
    
    def __init__(self):
        """Inicializa o gerenciador de dados."""
        self.dados: Optional[pd.DataFrame] = None
    
    def carregar_dados(self, arquivo_excel: Path) -> pd.DataFrame:
        """
        Carrega os dados do arquivo Excel.
        
        Args:
            arquivo_excel: Caminho do arquivo Excel.
            
        Returns:
            DataFrame com os dados carregados.
            
        Raises:
            ValueError: Se o arquivo não existir ou não tiver as colunas necessárias.
        """
        if not arquivo_excel.exists():
            raise ValueError(f"Arquivo não encontrado: {arquivo_excel}")
        
        # Carrega os dados
        self.dados = pd.read_excel(arquivo_excel)
        
        # Verifica as colunas necessárias
        colunas_necessarias = [
            "SPG",
            "Ensaio",
            "Instrumento",
            "Tag",
            "Localização",
            "Faixa",
            "Unidade",
            "Classe",
            "Última Calibração",
            "Próxima Calibração",
            "Status"
        ]
        
        colunas_faltantes = [col for col in colunas_necessarias if col not in self.dados.columns]
        if colunas_faltantes:
            raise ValueError(
                f"Colunas necessárias não encontradas no arquivo: {', '.join(colunas_faltantes)}"
            )
        
        return self.dados
    
    def obter_spgs(self) -> List[str]:
        """
        Obtém a lista de SPGs disponíveis.
        
        Returns:
            Lista de SPGs.
            
        Raises:
            ValueError: Se os dados não foram carregados.
        """
        if self.dados is None:
            raise ValueError("Dados não carregados")
        
        return sorted(self.dados["SPG"].unique().tolist())
    
    def obter_ensaios(self, spg: str) -> List[str]:
        """
        Obtém a lista de ensaios disponíveis para um SPG.
        
        Args:
            spg: SPG selecionado.
            
        Returns:
            Lista de ensaios.
            
        Raises:
            ValueError: Se os dados não foram carregados.
        """
        if self.dados is None:
            raise ValueError("Dados não carregados")
        
        return sorted(
            self.dados[self.dados["SPG"] == spg]["Ensaio"].unique().tolist()
        )
    
    def filtrar_por_spg_ensaio(
        self,
        dados: pd.DataFrame,
        spg: str,
        ensaio: str
    ) -> pd.DataFrame:
        """
        Filtra os dados por SPG e ensaio.
        
        Args:
            dados: DataFrame com os dados.
            spg: SPG selecionado.
            ensaio: Ensaio selecionado.
            
        Returns:
            DataFrame com os dados filtrados.
            
        Raises:
            ValueError: Se não houver dados para o SPG e ensaio selecionados.
        """
        dados_filtrados = dados[
            (dados["SPG"] == spg) &
            (dados["Ensaio"] == ensaio)
        ]
        
        if dados_filtrados.empty:
            raise ValueError(
                f"Não há instrumentos para o SPG '{spg}' e ensaio '{ensaio}'"
            )
        
        return dados_filtrados 