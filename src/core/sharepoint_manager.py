"""
Módulo responsável pela comunicação com o SharePoint.
"""
import requests
import json
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Union, Any
import warnings
from urllib.parse import urljoin
from collections import Counter, defaultdict
import os

# Configuração de logging
logger = logging.getLogger(__name__)

# Suprimir avisos do pandas
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

class SharePointManager:
    """Classe para gerenciar a comunicação com o SharePoint."""
    
    def __init__(self, site_url: str, username: str, password: str):
        """
        Inicializa o gerenciador do SharePoint.
        
        Args:
            site_url: URL do site do SharePoint
            username: Nome de usuário para autenticação
            password: Senha para autenticação
        """
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.dados_instrumentos = None
        
        # Headers padrão
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Verificar credenciais
        if not all([self.username, self.password]):
            raise ValueError("Credenciais do SharePoint não configuradas")
    
    def conectar(self) -> None:
        """
        Estabelece a conexão com o SharePoint.
        
        Raises:
            ConnectionError: Se não for possível conectar ao SharePoint
        """
        logger.info("Iniciando conexão com o SharePoint...")
        
        try:
            # Obter página de login
            login_url = f"{self.site_url}/login"
            logger.info(f"Acessando página de login: {login_url}")
            
            response = self.session.get(login_url)
            response.raise_for_status()
            
            # Extrair formulário de login
            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.find('form')
            
            if not form:
                raise ValueError("Formulário de login não encontrado")
            
            # Dados para login
            form_data = {
                "user": self.username,
                "password": self.password
            }
            
            # Adicionar campos ocultos do formulário
            for hidden in form.find_all("input", type="hidden"):
                name = hidden.get('name')
                if name:
                    form_data[name] = hidden.get('value', '')
            
            # Headers para requisição
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Fazer login
            logger.info("Enviando formulário de login...")
            response = self.session.post(
                login_url,
                data=form_data,
                headers=headers,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Verificar se o login foi bem sucedido
            if 'login' in response.url.lower():
                raise ValueError("Falha na autenticação. Verifique suas credenciais.")
            
            # Testar se a conexão está funcionando
            test_url = f"{self.site_url}/instruments"
            logger.info(f"Testando conexão com: {test_url}")
            response = self.session.get(test_url)
            response.raise_for_status()
            
            # Verificar se estamos realmente autenticados
            if "login" in response.url.lower() or "login" in response.text.lower():
                raise ValueError("Não foi possível autenticar no SharePoint")
            
            logger.info("Conexão estabelecida com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao SharePoint: {str(e)}")
            raise
    
    def desconectar(self) -> None:
        """Encerra a conexão com o SharePoint."""
        try:
            self.session.close()
            self.session = None
            logger.info("Desconectado do SharePoint")
        except Exception as e:
            logger.error(f"Erro ao desconectar do SharePoint: {str(e)}")
            raise
    
    def obter_lista_instrumentos(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de instrumentos do SharePoint.
        
        Returns:
            Lista de dicionários com os dados dos instrumentos
            
        Raises:
            ConnectionError: Se não for possível obter os dados
            ValueError: Se os dados obtidos não estiverem no formato esperado
        """
        if not self.session:
            raise ConnectionError("Não há conexão ativa com o SharePoint")
        
        logger.info("Obtendo lista de instrumentos do SharePoint...")
        
        try:
            # Acessar página de instrumentos
            instruments_url = f"{self.site_url}/instruments"
            logger.info(f"Acessando página de instrumentos: {instruments_url}")
            response = self.session.get(instruments_url)
            response.raise_for_status()
            
            # Verificar se estamos realmente autenticados
            if "login" in response.url.lower() or "login" in response.text.lower():
                raise ValueError("Sessão expirada ou não autenticado. Tente conectar novamente.")
            
            # Extrair dados do JavaScript
            dados_instrumentos = self._extrair_dados_instrumentos(response.text)
            
            # Validar dados
            if not dados_instrumentos:
                raise ValueError("Nenhum dado de instrumento encontrado")
            
            # Verificar campos importantes no primeiro instrumento
            primeiro_inst = dados_instrumentos[0]
            campos_importantes = ['name', 'type', 'brand', 'model']
            campos_encontrados = [campo for campo in campos_importantes if campo in primeiro_inst]
            
            # Verificar campo essencial
            if 'name' not in primeiro_inst:
                logger.warning("Campo 'name' não encontrado. Alguns instrumentos podem ficar sem identificação.")
            
            logger.info(f"Encontrados {len(dados_instrumentos)} instrumentos")
            
            # Processar e armazenar os dados
            self.dados_instrumentos = self._processar_dados_instrumentos(dados_instrumentos)
            
            # Salvar dados em JSON
            self._salvar_dados_json(self.dados_instrumentos)
            
            return self.dados_instrumentos
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter dados do SharePoint: {str(e)}")
            raise ConnectionError(f"Erro ao obter dados do SharePoint: {str(e)}")
        except Exception as e:
            logger.error(f"Erro ao processar dados do SharePoint: {str(e)}")
            raise ValueError(f"Erro ao processar dados do SharePoint: {str(e)}")
    
    def _extrair_dados_instrumentos(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extrai os dados dos instrumentos do conteúdo HTML.
        
        Args:
            html_content: Conteúdo HTML da página
            
        Returns:
            Lista de dicionários com os dados dos instrumentos
            
        Raises:
            ValueError: Se não for possível extrair os dados
        """
        # Tentar diferentes padrões de busca
        dados_instrumentos = []
        
        # 1. Procurar array JSON de instrumentos
        match = re.search(r'JSON\.parse\((\'|")(\[.*?\])(\'|")\)', html_content, re.DOTALL)
        if match:
            try:
                json_str = match.group(2)
                json_str = json_str.replace('\\"', '"').replace('\\/', '/')
                json_str = bytes(json_str, 'utf-8').decode('unicode_escape')
                json_str = json_str.encode('latin1').decode('utf-8')
                dados_instrumentos = json.loads(json_str)
                logger.info("Dados extraídos usando JSON.parse")
            except Exception as e:
                logger.warning(f"Erro ao processar JSON.parse: {str(e)}")
        
        # 2. Procurar arrays JSON em tags script
        if not dados_instrumentos:
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup.find_all('script'):
                if script.string:
                    # Procurar por arrays JSON
                    matches = re.findall(r'(\[[\s\S]*?\])', script.string)
                    for match in matches:
                        try:
                            data = json.loads(match)
                            if isinstance(data, list) and len(data) > 0:
                                # Verificar se parece ser uma lista de instrumentos
                                if all(isinstance(item, dict) for item in data):
                                    dados_instrumentos = data
                                    logger.info("Dados extraídos de tag script")
                                    break
                        except:
                            continue
                    if dados_instrumentos:
                        break
        
        # 3. Procurar dados em atributos data-*
        if not dados_instrumentos:
            soup = BeautifulSoup(html_content, 'html.parser')
            for element in soup.find_all(attrs={"data-instrument": True}):
                try:
                    data = json.loads(element['data-instrument'])
                    if isinstance(data, dict):
                        dados_instrumentos.append(data)
                except:
                    continue
            if dados_instrumentos:
                logger.info("Dados extraídos de atributos data-*")
        
        # 4. Procurar dados em tabelas HTML
        if not dados_instrumentos:
            soup = BeautifulSoup(html_content, 'html.parser')
            for table in soup.find_all('table'):
                headers = []
                for th in table.find_all('th'):
                    headers.append(th.text.strip())
                
                if headers:
                    for tr in table.find_all('tr')[1:]:  # Pular cabeçalho
                        cells = tr.find_all('td')
                        if len(cells) == len(headers):
                            instrumento = {}
                            for i, cell in enumerate(cells):
                                instrumento[headers[i]] = cell.text.strip()
                            dados_instrumentos.append(instrumento)
            
            if dados_instrumentos:
                logger.info("Dados extraídos de tabelas HTML")
        
        if not dados_instrumentos:
            raise ValueError("Dados dos instrumentos não encontrados no HTML")
        
        return dados_instrumentos
    
    def _processar_dados_instrumentos(self, dados: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa os dados brutos dos instrumentos.
        
        Args:
            dados: Lista de dicionários com dados brutos dos instrumentos
            
        Returns:
            Lista de dicionários com dados processados
        """
        logger.info("Iniciando processamento dos dados dos instrumentos...")
        instrumentos_processados = []
        
        for idx, instrumento in enumerate(dados):
            try:
                logger.debug(f"Processando instrumento {idx + 1}/{len(dados)}")
                
                # Mapeamento de campos com valores padrão
                instrumento_processado = {
                    'SPG': '-',
                    'Ensaio': '-',
                    'Instrumento': '-',
                    'Tipo': '-',
                    'Marca': '-',
                    'Modelo': '-',
                    'Número de Série': '-',
                    'Localização': '-',
                    'Faixa': '-',
                    'Unidade': '-',
                    'Status': '-',
                    'Classe': '-',
                    'Certificado': '-',
                    'Descrição': '-',
                    'ValidadeCertificado': '-',
                    'CriterioAceitacao': '-',
                    'IntervaloOperacao': '-'
                }
                
                # Mapeamento direto dos campos com base na estrutura real
                if 'name' in instrumento:
                    instrumento_processado['Instrumento'] = str(instrumento['name'])
                
                if 'type' in instrumento:
                    instrumento_processado['Tipo'] = str(instrumento['type'])
                
                if 'brand' in instrumento:
                    instrumento_processado['Marca'] = str(instrumento['brand'])
                
                if 'model' in instrumento:
                    instrumento_processado['Modelo'] = str(instrumento['model'])
                
                if 'serial_num' in instrumento:
                    instrumento_processado['Número de Série'] = str(instrumento['serial_num'])
                
                if 'location' in instrumento:
                    instrumento_processado['Localização'] = str(instrumento['location'])
                
                if 'range' in instrumento:
                    instrumento_processado['Faixa'] = str(instrumento['range'])
                
                if 'description' in instrumento:
                    instrumento_processado['Descrição'] = str(instrumento['description'])
                
                if 'certif_num' in instrumento:
                    instrumento_processado['Certificado'] = str(instrumento['certif_num'])
                
                if 'certif_end_date' in instrumento:
                    instrumento_processado['ValidadeCertificado'] = str(instrumento['certif_end_date'])
                
                if 'acceptance_status' in instrumento:
                    instrumento_processado['CriterioAceitacao'] = str(instrumento['acceptance_status'])
                
                # Extrair SPG e Ensaio do campo exp_name
                if 'exp_name' in instrumento:
                    exp_name = str(instrumento['exp_name'])
                    # Formato esperado: "[SPG0121] Ensaio 102"
                    spg_match = re.search(r'\[(SPG\d+)\]', exp_name)
                    ensaio_match = re.search(r'Ensaio\s+(\d+)', exp_name)
                    
                    if spg_match:
                        instrumento_processado['SPG'] = spg_match.group(1)
                    
                    if ensaio_match:
                        instrumento_processado['Ensaio'] = f"Ensaio {ensaio_match.group(1)}"
                
                # Extrair Status
                if 'sensor_status' in instrumento:
                    status = instrumento['sensor_status']
                    if status == 1:
                        instrumento_processado['Status'] = 'Ativo'
                    elif status == 0:
                        instrumento_processado['Status'] = 'Bloqueado'
                
                # Extrair Intervalo de Operação
                if 'inst_range' in instrumento and isinstance(instrumento['inst_range'], list) and instrumento['inst_range']:
                    range_info = instrumento['inst_range'][0]
                    if isinstance(range_info, dict):
                        min_val = range_info.get('min', '0')
                        max_val = range_info.get('max', '')
                        unit = range_info.get('unit', '')
                        if max_val and unit:
                            instrumento_processado['IntervaloOperacao'] = f"{min_val} - {max_val} {unit}"
                
                # Remover campos vazios
                instrumento_processado = {k: v for k, v in instrumento_processado.items() if v != '-'}
                
                # Validar campos obrigatórios
                campos_obrigatorios = ['Instrumento', 'Tipo']
                campos_faltantes = [campo for campo in campos_obrigatorios if campo not in instrumento_processado]
                if campos_faltantes:
                    logger.warning(f"Instrumento {idx + 1} está faltando campos obrigatórios: {campos_faltantes}")
                    continue
                
                instrumentos_processados.append(instrumento_processado)
                
            except Exception as e:
                logger.error(f"Erro ao processar instrumento {idx + 1}: {str(e)}")
                logger.debug(f"Dados do instrumento com erro: {instrumento}")
                continue
        
        logger.info(f"Processamento concluído. {len(instrumentos_processados)} instrumentos processados com sucesso.")
        return instrumentos_processados
    
    @lru_cache(maxsize=128)
    def _limpar_texto(self, valor: Optional[Union[str, bytes]]) -> str:
        """
        Limpa e formata strings (com cache para melhor performance).
        
        Args:
            valor: Valor a ser limpo
            
        Returns:
            String limpa e formatada
        """
        if valor is None or valor == '':
            return '-'
            
        try:
            if isinstance(valor, bytes):
                valor = valor.decode('utf-8')
            
            valor = str(valor).strip()
            substituicoes = {
                'Ã©': 'é', 'Ã£': 'ã', 'Ã¢': 'â',
                'Ã§': 'ç', 'Ãª': 'ê', 'Ã³': 'ó',
                'Ã¡': 'á'
            }
            for antigo, novo in substituicoes.items():
                valor = valor.replace(antigo, novo)
                
            return valor if valor else '-'
        except:
            return '-'
    
    def _formatar_data(self, data: Optional[str]) -> str:
        """
        Formata a data para o padrão ISO 8601 (YYYY-MM-DD).
        
        Args:
            data: String com a data a ser formatada
            
        Returns:
            String com a data formatada em ISO 8601 ou '-' se inválida
        """
        if not data:
            return '-'
            
        try:
            # Remove espaços extras
            data = data.strip()
            
            # Lista de formatos possíveis
            formatos = [
                '%Y-%m-%d',           # 2024-04-18
                '%d/%m/%Y',           # 18/04/2024
                '%d-%m-%Y',           # 18-04-2024
                '%Y/%m/%d',           # 2024/04/18
                '%d/%m/%Y %H:%M:%S',  # 18/04/2024 14:30:00
                '%Y-%m-%d %H:%M:%S',  # 2024-04-18 14:30:00
                '%d-%m-%Y %H:%M:%S',  # 18-04-2024 14:30:00
                '%Y/%m/%d %H:%M:%S'   # 2024/04/18 14:30:00
            ]
            
            # Tenta cada formato
            for formato in formatos:
                try:
                    data_obj = datetime.strptime(data, formato)
                    return data_obj.strftime('%Y-%m-%d')  # Formato ISO 8601
                except ValueError:
                    continue
                    
            # Se nenhum formato funcionou, retorna '-'
            logger.warning(f"Formato de data não reconhecido: {data}")
            return '-'
            
        except Exception as e:
            logger.warning(f"Erro ao formatar data '{data}': {str(e)}")
            return '-'
    
    def _obter_intervalo_operacao(self, intervalo: Optional[Union[List, Dict]]) -> str:
        """
        Extrai e formata o intervalo de operação.
        
        Args:
            intervalo: Dados do intervalo de operação
            
        Returns:
            String com o intervalo formatado ou '-' se inválido
        """
        if not intervalo:
            return '-'
            
        try:
            if isinstance(intervalo, list) and intervalo:
                range_info = intervalo[0]
                if isinstance(range_info, dict):
                    min_val = range_info.get('min', '0')
                    max_val = range_info.get('max', '')
                    unit = range_info.get('unit', '')
                    if max_val and unit:
                        return f"{min_val} - {max_val} {unit}"
            return '-'
        except:
            return '-'
    
    def obter_estatisticas_dados(self) -> Dict[str, Any]:
        """
        Obtém estatísticas dos dados dos instrumentos.
        
        Returns:
            Dicionário com as estatísticas calculadas
        """
        logger.info("Calculando estatísticas dos dados...")
        
        try:
            # Obter lista de instrumentos processados
            instrumentos = self.obter_lista_instrumentos()
            
            if not instrumentos:
                logger.warning("Nenhum instrumento encontrado para calcular estatísticas")
                return {
                    'total_instrumentos': 0,
                    'total_por_spg': Counter(),
                    'total_por_ensaio': Counter(),
                    'total_por_status': Counter(),
                    'instrumentos_por_classe': Counter(),
                    'valores_nulos': Counter()
                }
            
            # Inicializar contadores
            total_por_spg = Counter()
            total_por_ensaio = Counter()
            total_por_status = Counter()
            instrumentos_por_classe = Counter()
            valores_nulos = Counter()
            
            # Calcular estatísticas
            for idx, instrumento in enumerate(instrumentos):
                try:
                    # Contar por SPG
                    if 'SPG' in instrumento:
                        total_por_spg[instrumento['SPG']] += 1
                    
                    # Contar por Ensaio
                    if 'Ensaio' in instrumento:
                        total_por_ensaio[instrumento['Ensaio']] += 1
                    
                    # Contar por Status
                    if 'Status' in instrumento:
                        total_por_status[instrumento['Status']] += 1
                    
                    # Contar por Classe (usando Tipo como classe)
                    if 'Tipo' in instrumento:
                        instrumentos_por_classe[instrumento['Tipo']] += 1
                    
                    # Contar valores nulos
                    for campo, valor in instrumento.items():
                        if not valor or valor == '-':
                            valores_nulos[campo] += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao processar estatísticas do instrumento {idx + 1}: {str(e)}")
                    continue
            
            # Log das estatísticas calculadas
            logger.info(f"Total de instrumentos: {len(instrumentos)}")
            logger.info(f"Total de SPGs diferentes: {len(total_por_spg)}")
            logger.info(f"Total de Ensaios diferentes: {len(total_por_ensaio)}")
            logger.info(f"Total de Status diferentes: {len(total_por_status)}")
            logger.info(f"Total de Classes diferentes: {len(instrumentos_por_classe)}")
            
            # Retornar estatísticas
            return {
                'total_instrumentos': len(instrumentos),
                'total_por_spg': total_por_spg,
                'total_por_ensaio': total_por_ensaio,
                'total_por_status': total_por_status,
                'instrumentos_por_classe': instrumentos_por_classe,
                'valores_nulos': valores_nulos
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {str(e)}")
            raise
    
    def _obter_valor_alternativo(self, dados: Dict[str, Any], campos: List[str]) -> str:
        """
        Obtém o valor de um campo usando uma lista de alternativas possíveis.
        
        Args:
            dados: Dicionário com os dados do instrumento
            campos: Lista de nomes de campos possíveis
            
        Returns:
            Valor do primeiro campo encontrado ou '-' se nenhum campo tiver valor
        """
        if not dados:
            logger.debug("Dados vazios recebidos em _obter_valor_alternativo")
            return '-'
            
        for campo in campos:
            try:
                valor = dados.get(campo)
                if valor is not None:
                    # Converter para string e limpar
                    valor_str = str(valor).strip()
                    if valor_str:
                        return valor_str
            except Exception as e:
                logger.debug(f"Erro ao processar campo {campo}: {str(e)}")
                continue
                
        return '-'
    
    def _salvar_dados_json(self, dados: List[Dict[str, Any]]) -> None:
        """
        Salva os dados dos instrumentos em um arquivo JSON.
        
        Args:
            dados: Lista de dicionários com os dados dos instrumentos
        """
        try:
            # Criar nome do arquivo com timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"data/json/instrumentos_{timestamp}.json"
            
            # Garantir que o diretório existe
            os.makedirs(os.path.dirname(nome_arquivo), exist_ok=True)
            
            # Salvar dados em JSON
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Dados salvos em {nome_arquivo}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados em JSON: {str(e)}")
            raise 