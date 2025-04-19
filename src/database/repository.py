"""Repositório para operações com instrumentos."""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import Instrumento

logger = logging.getLogger("instrumentos")

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
            logger.info(f"✅ Instrumento criado com sucesso: {instrumento.id}")
            return instrumento
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Erro ao criar instrumento: {e}")
            raise

    def criar_em_massa(self, instrumentos: List[Instrumento]) -> List[Instrumento]:
        """Cria múltiplos instrumentos no banco de dados."""
        try:
            self.db.bulk_save_objects(instrumentos)
            self.db.commit()
            logger.info(f"✅ {len(instrumentos)} instrumentos criados com sucesso")
            return instrumentos
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Erro ao criar instrumentos em massa: {e}")
            raise

    def limpar_tabela(self) -> None:
        """Limpa todos os registros da tabela de instrumentos."""
        try:
            self.db.query(Instrumento).delete()
            self.db.commit()
            logger.info("🧹 Tabela de instrumentos limpa com sucesso")
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Erro ao limpar tabela de instrumentos: {e}")
            raise

    def sincronizar_dados(self, instrumentos_json: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Sincroniza os dados do JSON com o banco de dados.
        
        Args:
            instrumentos_json: Lista de dicionários com dados dos instrumentos do JSON
            
        Returns:
            Dict com estatísticas de sincronização (adicionados, atualizados, removidos)
        """
        try:
            # Obter todos os instrumentos existentes no banco
            instrumentos_existentes = self.db.query(Instrumento).all()
            logger.info(f"📊 Encontrados {len(instrumentos_existentes)} instrumentos no banco de dados")
            
            # Criar dicionários para facilitar a busca
            instrumentos_por_numero_serie = {inst.numero_serie: inst for inst in instrumentos_existentes if inst.numero_serie}
            instrumentos_por_nome = {inst.nome: inst for inst in instrumentos_existentes if inst.nome}
            
            # Contadores para estatísticas
            adicionados = 0
            atualizados = 0
            removidos = 0
            avisos = 0
            
            # Conjunto para rastrear instrumentos processados
            processados = set()
            
            # Processar cada instrumento do JSON
            for inst_json in instrumentos_json:
                nome = inst_json.get('Instrumento')
                numero_serie = inst_json.get('Número de Série')
                
                # Tentar encontrar o instrumento pelo número de série ou nome
                instrumento = None
                if numero_serie and numero_serie in instrumentos_por_numero_serie:
                    instrumento = instrumentos_por_numero_serie[numero_serie]
                elif nome and nome in instrumentos_por_nome:
                    instrumento = instrumentos_por_nome[nome]
                
                # Converter a data de validade se existir
                validade = None
                if inst_json.get('ValidadeCertificado') and inst_json.get('ValidadeCertificado') != '-':
                    try:
                        from datetime import datetime
                        validade = datetime.strptime(inst_json['ValidadeCertificado'], '%Y-%m-%d').date()
                    except ValueError:
                        logger.warning(f"⚠️ Data de validade inválida para o instrumento {nome}: {inst_json.get('ValidadeCertificado')}")
                        avisos += 1
                
                if instrumento:
                    # Atualizar instrumento existente
                    instrumento.spg = inst_json.get('SPG')
                    instrumento.ensaio = inst_json.get('Ensaio')
                    instrumento.nome = nome
                    instrumento.tipo = inst_json.get('Tipo')
                    instrumento.marca = inst_json.get('Marca')
                    instrumento.modelo = inst_json.get('Modelo')
                    instrumento.numero_serie = numero_serie
                    instrumento.localizacao = inst_json.get('Localização')
                    instrumento.faixa = inst_json.get('Faixa')
                    instrumento.unidade = inst_json.get('Unidade')
                    instrumento.status = inst_json.get('Status')
                    instrumento.classe = inst_json.get('Classe')
                    instrumento.certificado = inst_json.get('Certificado')
                    instrumento.descricao = inst_json.get('Descrição')
                    instrumento.validade_certificado = validade
                    instrumento.criterio_aceitacao = inst_json.get('CriterioAceitacao')
                    instrumento.intervalo_operacao = inst_json.get('IntervaloOperacao')
                    
                    atualizados += 1
                else:
                    # Criar novo instrumento
                    novo_instrumento = Instrumento(
                        spg=inst_json.get('SPG'),
                        ensaio=inst_json.get('Ensaio'),
                        nome=nome,
                        tipo=inst_json.get('Tipo'),
                        marca=inst_json.get('Marca'),
                        modelo=inst_json.get('Modelo'),
                        numero_serie=numero_serie,
                        localizacao=inst_json.get('Localização'),
                        faixa=inst_json.get('Faixa'),
                        unidade=inst_json.get('Unidade'),
                        status=inst_json.get('Status'),
                        classe=inst_json.get('Classe'),
                        certificado=inst_json.get('Certificado'),
                        descricao=inst_json.get('Descrição'),
                        validade_certificado=validade,
                        criterio_aceitacao=inst_json.get('CriterioAceitacao'),
                        intervalo_operacao=inst_json.get('IntervaloOperacao')
                    )
                    self.db.add(novo_instrumento)
                    adicionados += 1
                
                # Marcar como processado
                if numero_serie:
                    processados.add(numero_serie)
                elif nome:
                    processados.add(nome)
            
            # Identificar instrumentos a serem removidos (não estão mais no JSON)
            for inst in instrumentos_existentes:
                identificador = inst.numero_serie or inst.nome
                if identificador and identificador not in processados:
                    self.db.delete(inst)
                    removidos += 1
            
            # Commit das alterações
            self.db.commit()
            
            # Retornar estatísticas
            estatisticas = {
                "adicionados": adicionados,
                "atualizados": atualizados,
                "removidos": removidos,
                "avisos": avisos
            }
            
            logger.info(f"✅ Sincronização concluída: {adicionados} adicionados, {atualizados} atualizados, {removidos} removidos, {avisos} avisos")
            return estatisticas
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Erro ao sincronizar dados: {e}")
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
                logger.info(f"✅ Instrumento {instrumento_id} atualizado com sucesso")
            return instrumento
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Erro ao atualizar instrumento {instrumento_id}: {e}")
            raise

    def deletar(self, instrumento_id: int) -> bool:
        """Deleta um instrumento pelo ID."""
        try:
            instrumento = self.obter_por_id(instrumento_id)
            if instrumento:
                self.db.delete(instrumento)
                self.db.commit()
                logger.info(f"✅ Instrumento {instrumento_id} deletado com sucesso")
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Erro ao deletar instrumento {instrumento_id}: {e}")
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
            logger.error(f"❌ Erro ao importar dados JSON: {e}")
            raise 