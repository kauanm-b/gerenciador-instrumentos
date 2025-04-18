"""
Modelos para as tabelas do banco de dados.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Date, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime

class Base(DeclarativeBase):
    """Classe base para todos os modelos."""
    pass

class Instrumento(Base):
    """Modelo para Instrumentos."""
    
    __tablename__ = 'instrumentos'
    
    # Identificação básica
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    marca = Column(String(100))
    modelo = Column(String(100))
    numero_serie = Column(String(100))
    descricao = Column(Text)
    
    # Características técnicas
    faixa = Column(String(100))
    unidade = Column(String(50))
    classe = Column(String(50))
    criterio_aceitacao = Column(String(200))
    intervalo_operacao = Column(String(200))
    
    # Localização e organização
    spg = Column(String(50), index=True)
    ensaio = Column(String(100))
    localizacao = Column(String(200))
    
    # Status e certificação
    status = Column(String(50))
    certificado = Column(String(100))
    validade_certificado = Column(Date)
    
    # Metadados
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        """Representação string do objeto."""
        return f"<Instrumento(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')>"

    def to_dict(self):
        """Converte o instrumento para um dicionário."""
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "marca": self.marca,
            "modelo": self.modelo,
            "numero_serie": self.numero_serie,
            "descricao": self.descricao,
            "faixa": self.faixa,
            "unidade": self.unidade,
            "classe": self.classe,
            "criterio_aceitacao": self.criterio_aceitacao,
            "intervalo_operacao": self.intervalo_operacao,
            "spg": self.spg,
            "ensaio": self.ensaio,
            "localizacao": self.localizacao,
            "status": self.status,
            "certificado": self.certificado,
            "validade_certificado": self.validade_certificado.isoformat() if self.validade_certificado else None,
            "data_criacao": self.data_criacao.isoformat() if self.data_criacao else None,
            "data_atualizacao": self.data_atualizacao.isoformat() if self.data_atualizacao else None
        } 