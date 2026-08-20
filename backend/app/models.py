from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Municipio(Base):
    """
    Tabela Dimensão: Cadastro dos 5.570 municípios brasileiros.
    """
    __tablename__ = "municipios"

    codigo_ibge = Column(String(7), primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    estado = Column(String(2), nullable=False) # UF (ex: PR, SP)

class Indicador(Base):
    """
    Tabela Dimensão: Define as regras de cada indicador da matriz.
    """
    __tablename__ = "indicadores"

    id = Column(String(50), primary_key=True, index=True) # ex: "homicidios_100k"
    nome = Column(String(255), nullable=False)
    norma_iso = Column(String(50), nullable=False) # ex: "ISO 37120"
    peso = Column(Float, nullable=False, default=0.02)
    impacto = Column(Integer, nullable=False, default=1) # 1 = Benefício, -1 = Custo

class ValorIndicador(Base):
    """
    Tabela Fato: O cruzamento entre Município, Indicador e o Valor em um determinado Ano.
    """
    __tablename__ = "valores_indicadores"

    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(String(7), ForeignKey("municipios.codigo_ibge"), index=True, nullable=False)
    id_indicador = Column(String(50), ForeignKey("indicadores.id"), index=True, nullable=False)
    ano_referencia = Column(Integer, nullable=False)
    valor = Column(Float, nullable=True) # Se for nulo, a cidade não informou o dado
    fonte = Column(String(255)) # ex: "br_fbsp.csv"

    # Relacionamentos (Opcional, mas excelente para o SQLAlchemy puxar dados cruzados)
    municipio = relationship("Municipio")
    indicador = relationship("Indicador")


class ValorIndicadorLatest(Base):
    """
    Snapshot auxiliar: mantém apenas o valor mais recente por Município + Indicador.
    Usado para acelerar o cálculo do TOPSIS em tempo de requisição.
    """
    __tablename__ = "valores_indicadores_latest"

    codigo_ibge = Column(String(7), ForeignKey("municipios.codigo_ibge"), primary_key=True, index=True, nullable=False)
    id_indicador = Column(String(50), ForeignKey("indicadores.id"), primary_key=True, index=True, nullable=False)
    ano_referencia = Column(Integer, nullable=False)
    valor = Column(Float, nullable=True)
    fonte = Column(String(255))
    id_origem = Column(Integer, nullable=False, index=True)

    municipio = relationship("Municipio")
    indicador = relationship("Indicador")