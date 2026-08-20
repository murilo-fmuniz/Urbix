from pydantic import BaseModel, Field
from typing import Optional, List, Dict

# ==========================================
# 🏛️ SCHEMAS DE LEITURA DO BANCO DE DADOS
# ==========================================

class Municipio(BaseModel):
    codigo_ibge: str
    nome: str
    estado: str

    class Config:
        from_attributes = True

class Indicador(BaseModel):
    id: str
    nome: str
    norma_iso: str
    peso: float
    impacto: int # 1 para Benefício, -1 para Custo

    class Config:
        from_attributes = True

class ValorIndicador(BaseModel):
    id: int
    codigo_ibge: str
    id_indicador: str
    ano_referencia: int
    valor: Optional[float] = None
    fonte: Optional[str] = None

    class Config:
        from_attributes = True


# ==========================================
# 🎛️ SCHEMAS DO SIMULADOR (FRONTEND -> API)
# ==========================================

class DadosManuaisSimulador(BaseModel):
    """
    Estrutura que o Frontend envia quando o usuário altera os dados na tela.
    Os dados aqui são BRUTOS (ex: número absoluto de habitantes ou homicídios).
    O motor TOPSIS fará o cálculo das taxas em tempo real.
    """
    codigo_ibge: str = Field(..., description="Código IBGE da cidade simulada")
    valores_brutos: Dict[str, float] = Field(
        default_factory=dict,
        description="Dicionário chave-valor com o id da variável e o valor bruto digitado. Ex: {'populacao_total': 150000, 'homicidios': 12}"
    )

class TopsisSimulationRequest(BaseModel):
    """
    Payload principal para a rota de geração do Ranking Híbrido.
    """
    cidades_ibge: List[str] = Field(..., description="Lista de cidades para comparar no ranking")
    simulacoes: Optional[List[DadosManuaisSimulador]] = Field(
        default=None, 
        description="Dados alterados manualmente pelo usuário para sobrepor o banco de dados oficial"
    )

class TopsisRankingResponse(BaseModel):
    """
    Resposta do Motor Matemático devolvida ao Frontend.
    """
    codigo_ibge: str
    nome_cidade: str
    pontuacao_topsis: float
    distancia_positiva: float
    distancia_negativa: float
    valores_calculados: Dict[str, float] = Field(
        description="Os valores finais já processados (taxas/porcentagens) usados na matriz"
    )