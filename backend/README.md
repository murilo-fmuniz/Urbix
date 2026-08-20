# ⚙️ Urbix - Motor Backend (FastAPI & ETL)

Este módulo é responsável por toda a inteligência de dados, processamento matemático e APIs do projeto Urbix. Desenvolvido em Python moderno, ele garante que os cálculos multicritério sejam rápidos e baseados em dados reais extraídos de um Data Lake local governamental.

## 🚀 Tecnologias Principais
*   **Framework API:** FastAPI (com Pydantic para validação estrita).
*   **Engenharia de Dados (ETL):** Pandas, xlrd.
*   **Banco de Dados:** SQLite (via SQLAlchemy e Alembic para migrações).
*   **Motor Matemático:** Implementação customizada do algoritmo TOPSIS.

## 📂 Estrutura de Destaque
*   `app/services/topsis_core.py`: O coração do sistema, responsável por gerar a matriz normalizada e calcular o ranking Híbrido sem persistir simulações temporárias no banco.
*   `app/etl_config.py`: Dicionário de dados que roteia e mapeia como cada indicador (ex: homicídios, PIB, saneamento) deve ser lido dos arquivos brutos do Data Lake (`.csv`, `.xls`, `.ods`).
*   `tools/`: Scripts de varredura, inspeção semântica e carregamento do banco de dados (ETL).

## 💻 Como rodar localmente

1. Crie e ative o ambiente virtual:
    python -m venv venv
    
    # No Windows:
    .\venv\Scripts\activate
    
    # No Linux/Mac:
    source venv/bin/activate

2. Instale as dependências:
    pip install -r requirements.txt

3. Inicie o servidor FastAPI:
    uvicorn app.main:app --reload

A API estará disponível em `http://localhost:8000`. Acesse `/docs` para visualizar a documentação interativa (Swagger).