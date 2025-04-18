"""
Módulo responsável pela interface gráfica principal.
"""
from pathlib import Path
from typing import Optional

import pandas as pd
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (QComboBox, QFileDialog, QHBoxLayout, QLabel,
                            QMainWindow, QMessageBox, QProgressBar, QPushButton,
                            QVBoxLayout, QWidget)

from src.core.config import DIR_OUTPUT
from src.core.data_manager import DataManager
from src.core.excel_manager import ExcelManager
from src.core.sharepoint_manager import SharePointManager


class GeradorTabelaThread(QThread):
    """Thread para gerar a tabela em segundo plano."""
    
    progresso = pyqtSignal(str)
    erro = pyqtSignal(str)
    finalizado = pyqtSignal(Path)
    
    def __init__(self, arquivo_excel: Path, pasta_saida: Path, spg: Optional[str] = None,
                 ensaio: Optional[str] = None):
        """
        Inicializa a thread.
        
        Args:
            arquivo_excel: Caminho do arquivo Excel com os dados.
            pasta_saida: Pasta onde a tabela será salva.
            spg: SPG selecionado (opcional).
            ensaio: Ensaio selecionado (opcional).
        """
        super().__init__()
        self.arquivo_excel = arquivo_excel
        self.pasta_saida = pasta_saida
        self.spg = spg
        self.ensaio = ensaio
        self.data_manager = DataManager()
        self.excel_manager = ExcelManager(pasta_saida)
    
    def run(self):
        """Executa a geração da tabela."""
        try:
            # Carrega os dados
            self.progresso.emit("Carregando dados...")
            dados = self.data_manager.carregar_dados(self.arquivo_excel)
            
            # Gera a tabela
            self.progresso.emit("Gerando tabela...")
            if self.spg and self.ensaio:
                # Filtra os dados pelo SPG e ensaio
                dados_filtrados = self.data_manager.filtrar_por_spg_ensaio(
                    dados, self.spg, self.ensaio
                )
                # Cria a planilha do ensaio
                caminho_arquivo = self.excel_manager.criar_planilha_ensaio(
                    dados_filtrados, self.spg, self.ensaio
                )
            else:
                # Cria a planilha geral
                caminho_arquivo = self.excel_manager.criar_planilha_geral(dados)
            
            self.progresso.emit("Tabela gerada com sucesso!")
            self.finalizado.emit(caminho_arquivo)
            
        except Exception as e:
            self.erro.emit(str(e))


class CarregarDadosSharePointThread(QThread):
    """Thread para carregar dados do SharePoint em segundo plano."""
    
    progresso = pyqtSignal(str)
    erro = pyqtSignal(str)
    finalizado = pyqtSignal(Path)
    
    def __init__(self, site_url: str, username: str, password: str, pasta_saida: Path):
        """
        Inicializa a thread.
        
        Args:
            site_url: URL do site do SharePoint.
            username: Nome de usuário para autenticação.
            password: Senha para autenticação.
            pasta_saida: Pasta onde o arquivo Excel será salvo.
        """
        super().__init__()
        self.site_url = site_url
        self.username = username
        self.password = password
        self.pasta_saida = pasta_saida
        self.sharepoint_manager = SharePointManager(site_url, username, password)
    
    def run(self):
        """Executa o carregamento dos dados."""
        try:
            # Conecta ao SharePoint
            self.progresso.emit("Conectando ao SharePoint...")
            self.sharepoint_manager.conectar()
            
            # Obtém os dados
            self.progresso.emit("Obtendo dados dos instrumentos...")
            dados = self.sharepoint_manager.obter_lista_instrumentos()
            
            # Salva os dados em um arquivo Excel
            self.progresso.emit("Salvando dados em arquivo Excel...")
            caminho_arquivo = self.pasta_saida / "instrumentos.xlsx"
            self.sharepoint_manager.salvar_dados_excel(dados, caminho_arquivo)
            
            # Desconecta do SharePoint
            self.sharepoint_manager.desconectar()
            
            self.progresso.emit("Dados carregados com sucesso!")
            self.finalizado.emit(caminho_arquivo)
            
        except Exception as e:
            self.erro.emit(str(e))


class MainWindow(QMainWindow):
    """Janela principal da aplicação."""
    
    def __init__(self):
        """Inicializa a janela principal."""
        super().__init__()
        
        self.setWindowTitle("Gerador de Tabelas de Instrumentos")
        self.setMinimumSize(600, 200)
        
        # Inicializa gerenciadores
        self.data_manager = DataManager()
        
        # Inicializa variáveis
        self.arquivo_excel: Optional[Path] = None
        self.pasta_saida: Optional[Path] = None
        self.thread: Optional[QThread] = None
        
        # Configura a interface
        self._configurar_interface()
    
    def _configurar_interface(self):
        """Configura a interface do usuário."""
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Layout principal
        layout = QVBoxLayout()
        widget_central.setLayout(layout)
        
        # Área de seleção de arquivo
        layout_arquivo = QHBoxLayout()
        self.label_arquivo = QLabel("Nenhum arquivo selecionado")
        self.btn_arquivo = QPushButton("Selecionar Arquivo")
        self.btn_arquivo.clicked.connect(self.selecionar_arquivo)
        layout_arquivo.addWidget(self.label_arquivo)
        layout_arquivo.addWidget(self.btn_arquivo)
        layout.addLayout(layout_arquivo)
        
        # Botão para carregar dados do SharePoint
        self.btn_sharepoint = QPushButton("Carregar Dados do SharePoint")
        self.btn_sharepoint.clicked.connect(self.carregar_dados_sharepoint)
        layout.addWidget(self.btn_sharepoint)
        
        # Área de seleção de SPG e Ensaio
        layout_spg_ensaio = QHBoxLayout()
        
        # Seleção de SPG
        layout_spg = QVBoxLayout()
        layout_spg.addWidget(QLabel("SPG:"))
        self.combo_spg = QComboBox()
        self.combo_spg.currentTextChanged.connect(self.atualizar_ensaios)
        layout_spg.addWidget(self.combo_spg)
        layout_spg_ensaio.addLayout(layout_spg)
        
        # Seleção de Ensaio
        layout_ensaio = QVBoxLayout()
        layout_ensaio.addWidget(QLabel("Ensaio:"))
        self.combo_ensaio = QComboBox()
        layout_ensaio.addWidget(self.combo_ensaio)
        layout_spg_ensaio.addLayout(layout_ensaio)
        
        layout.addLayout(layout_spg_ensaio)
        
        # Botões de geração
        layout_botoes = QHBoxLayout()
        
        # Botão de gerar tabela geral
        self.btn_geral = QPushButton("Gerar Tabela Geral")
        self.btn_geral.clicked.connect(self.gerar_tabela_geral)
        self.btn_geral.setEnabled(False)
        layout_botoes.addWidget(self.btn_geral)
        
        # Botão de gerar tabela por SPG/Ensaio
        self.btn_spg_ensaio = QPushButton("Gerar Tabela SPG/Ensaio")
        self.btn_spg_ensaio.clicked.connect(self.gerar_tabela_ensaio)
        self.btn_spg_ensaio.setEnabled(False)
        layout_botoes.addWidget(self.btn_spg_ensaio)
        
        layout.addLayout(layout_botoes)
        
        # Barra de progresso
        self.barra_progresso = QProgressBar()
        self.barra_progresso.setTextVisible(True)
        self.barra_progresso.hide()
        layout.addWidget(self.barra_progresso)
        
        # Status bar
        self.statusBar().showMessage("Pronto")
        
        # Label de status
        self.label_status = QLabel()
        layout.addWidget(self.label_status)
    
    def carregar_dados_sharepoint(self):
        """Carrega os dados dos instrumentos do SharePoint."""
        # Configura a pasta de saída
        self.pasta_saida = Path.home() / "Documents" / "Instrumentos" / "output"
        self.pasta_saida.mkdir(parents=True, exist_ok=True)
        
        # Desabilita os widgets
        self.btn_arquivo.setEnabled(False)
        self.btn_sharepoint.setEnabled(False)
        self.btn_geral.setEnabled(False)
        self.btn_spg_ensaio.setEnabled(False)
        self.combo_spg.setEnabled(False)
        self.combo_ensaio.setEnabled(False)
        
        # Mostra a barra de progresso
        self.barra_progresso.show()
        self.barra_progresso.setRange(0, 0)
        
        # Cria e inicia a thread
        self.thread = CarregarDadosSharePointThread(
            "http://10.1.1.82:1206",  # URL do SharePoint local
            "kauam.barcellos",
            "S!78576@a",
            self.pasta_saida
        )
        self.thread.progresso.connect(self.atualizar_progresso)
        self.thread.erro.connect(self.mostrar_erro)
        self.thread.finalizado.connect(self.finalizar_carregamento_sharepoint)
        self.thread.start()
    
    def finalizar_carregamento_sharepoint(self, caminho_arquivo: Path):
        """
        Finaliza o carregamento dos dados do SharePoint.
        
        Args:
            caminho_arquivo: Caminho do arquivo Excel gerado.
        """
        # Atualiza o arquivo Excel
        self.arquivo_excel = caminho_arquivo
        self.label_arquivo.setText(f"Arquivo: {self.arquivo_excel.name}")
        
        # Carrega os dados e atualiza os combos
        self.carregar_dados()
        
        # Habilita os botões
        self.btn_arquivo.setEnabled(True)
        self.btn_sharepoint.setEnabled(True)
        self.btn_geral.setEnabled(True)
        self.btn_spg_ensaio.setEnabled(True)
        self.combo_spg.setEnabled(True)
        self.combo_ensaio.setEnabled(True)
        
        # Esconde a barra de progresso
        self.barra_progresso.hide()
        
        # Mostra mensagem de sucesso
        QMessageBox.information(
            self,
            "Sucesso",
            f"Dados carregados com sucesso!\nArquivo: {caminho_arquivo.name}"
        )
    
    def selecionar_arquivo(self):
        """Abre o diálogo para selecionar o arquivo Excel."""
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Arquivo Excel",
            "",
            "Arquivos Excel (*.xlsx *.xls)"
        )
        
        if arquivo:
            self.arquivo_excel = Path(arquivo)
            self.pasta_saida = self.arquivo_excel.parent / "output"
            self.label_arquivo.setText(f"Arquivo: {self.arquivo_excel.name}")
            
            # Carrega os dados e atualiza os combos
            self.carregar_dados()
            
            # Habilita os botões
            self.btn_geral.setEnabled(True)
            self.btn_spg_ensaio.setEnabled(True)
    
    def carregar_dados(self):
        """Carrega os dados do arquivo Excel."""
        try:
            # Carrega os dados
            dados = self.data_manager.carregar_dados(self.arquivo_excel)
            
            # Atualiza o combo de SPGs
            spgs = self.data_manager.obter_spgs()
            self.combo_spg.clear()
            self.combo_spg.addItems(spgs)
            
            # Atualiza o combo de ensaios
            self.atualizar_ensaios()
            
            self.statusBar().showMessage("Arquivo carregado com sucesso")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
    
    def atualizar_ensaios(self):
        """Atualiza o combo de ensaios com base no SPG selecionado."""
        try:
            # Obtém os ensaios do SPG selecionado
            self.combo_ensaio.clear()
            self.combo_ensaio.addItems(self.data_manager.obter_ensaios(self.combo_spg.currentText()))
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
    
    def gerar_tabela_geral(self):
        """Inicia a geração da tabela geral."""
        self.iniciar_geracao()
    
    def gerar_tabela_ensaio(self):
        """Inicia a geração da tabela de ensaio."""
        spg = self.combo_spg.currentText()
        ensaio = self.combo_ensaio.currentText()
        
        if not spg or not ensaio:
            QMessageBox.warning(
                self,
                "Aviso",
                "Selecione um SPG e um ensaio."
            )
            return
        
        self.iniciar_geracao(spg, ensaio)
    
    def iniciar_geracao(self, spg: Optional[str] = None, ensaio: Optional[str] = None):
        """
        Inicia a geração da tabela.
        
        Args:
            spg: SPG selecionado (opcional).
            ensaio: Ensaio selecionado (opcional).
        """
        # Desabilita os widgets
        self.btn_arquivo.setEnabled(False)
        self.btn_sharepoint.setEnabled(False)
        self.btn_geral.setEnabled(False)
        self.btn_spg_ensaio.setEnabled(False)
        self.combo_spg.setEnabled(False)
        self.combo_ensaio.setEnabled(False)
        
        # Mostra a barra de progresso
        self.barra_progresso.show()
        self.barra_progresso.setRange(0, 0)
        
        # Cria e inicia a thread
        self.thread = GeradorTabelaThread(
            self.arquivo_excel,
            self.pasta_saida,
            spg,
            ensaio
        )
        self.thread.progresso.connect(self.atualizar_progresso)
        self.thread.erro.connect(self.mostrar_erro)
        self.thread.finalizado.connect(self.finalizar_geracao)
        self.thread.start()
    
    def atualizar_progresso(self, mensagem: str):
        """
        Atualiza a mensagem de progresso.
        
        Args:
            mensagem: Mensagem a ser exibida.
        """
        self.label_status.setText(mensagem)
    
    def mostrar_erro(self, mensagem: str):
        """
        Mostra uma mensagem de erro.
        
        Args:
            mensagem: Mensagem de erro.
        """
        QMessageBox.critical(self, "Erro", mensagem)
        self.finalizar_geracao()
    
    def finalizar_geracao(self, caminho_arquivo: Optional[Path] = None):
        """
        Finaliza a geração da tabela.
        
        Args:
            caminho_arquivo: Caminho do arquivo gerado.
        """
        # Habilita os widgets
        self.btn_arquivo.setEnabled(True)
        self.btn_sharepoint.setEnabled(True)
        self.btn_geral.setEnabled(True)
        self.btn_spg_ensaio.setEnabled(True)
        self.combo_spg.setEnabled(True)
        self.combo_ensaio.setEnabled(True)
        
        # Esconde a barra de progresso
        self.barra_progresso.hide()
        
        # Mostra mensagem de sucesso
        if caminho_arquivo:
            QMessageBox.information(
                self,
                "Sucesso",
                f"Tabela gerada com sucesso!\nArquivo: {caminho_arquivo.name}"
            ) 