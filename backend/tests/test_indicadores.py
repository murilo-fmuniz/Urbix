from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base


# Configure in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
# Use StaticPool so the in-memory DB is shared across connections during tests
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables in the in-memory DB
Base.metadata.create_all(bind=engine)

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_get_indicadores_empty_list():
    resp = client.get("/api/v1/indicadores")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_post_indicador_and_get():
    payload = {
        "codigo_indicador": "TST001",
        "nome": "Indicador Teste",
        "norma": "Norma X",
        "grande_area": "Saude",
        "eixo": "Eixo 1",
        "tipo": "Taxa",
        "descricao": "Descrição do indicador de teste",
        "metodologia": {
            "desc_numerador": "Num",
            "desc_denominador": "Den",
            "multiplicador": 1.0,
            "unidade_medida": "%"
        },
        "dados_coleta": [
            {
                "cidade": "CidadeA",
                "estado": "EstadoA",
                "ano_referencia": 2020,
                "valor_numerador": 10.0,
                "valor_denominador": 20.0,
                "valor_final": 50.0,
                "dado_disponivel": True,
                "auditoria": {
                    "fonte_nome": "Fonte X",
                    "fonte_url": "http://fonte.example",
                    "data_extracao": "2020-01-01",
                    "observacoes": "ok"
                }
            }
        ]
    }

    resp = client.post("/api/v1/indicadores", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["codigo_indicador"] == "TST001"
    assert data["metodologia"]["desc_numerador"] == "Num"
    assert len(data["dados_coleta"]) == 1

    # agora o GET deve retornar ao menos este indicador
    resp2 = client.get("/api/v1/indicadores")
    assert resp2.status_code == 200
    lista = resp2.json()
    assert any(item.get("codigo_indicador") == "TST001" for item in lista)
