# Urbix Backend

Backend FastAPI, ETL nacional e motor TOPSIS do Urbix.

## Componentes

- `app/main.py`: aplicação FastAPI.
- `app/etl_config.py`: fontes, indicadores, status e regras de cálculo.
- `app/services/topsis_core.py`: matriz e algoritmo TOPSIS.
- `tools/local_etl_service.py`: ETL nacional híbrido.
- `tools/audit_etl_runtime.py`: relatório de cobertura para a IC.
- `tools/run_etl_apucarana.py`: teste isolado de Apucarana.
- `data/planilhas/`: datalake local, não deve ser versionado.

## Banco e ambiente

O ambiente de produção usa PostgreSQL configurado por `DATABASE_URL` no `.env`.
Nunca versione `.env`, credenciais, dumps ou dados brutos.

## Instalação

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## API

```powershell
python -m uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Produção: `https://urbix-api.onrender.com/`

## ETL nacional

O ETL padrão processa todos os municípios cadastrados:

```powershell
cd backend\tools
..\venv\Scripts\python.exe local_etl_service.py
```

A execução consulta:

- SIDRA/IBGE: população, PIB, força de trabalho e domicílios;
- SICONFI/Tesouro: receita, receita própria e despesas de capital;
- datalake local: MUNIC, SNIS, CAGED, CNES, FBSP e banda larga.

O ETL é idempotente por indicador e ano: substitui a carga anterior da mesma versão antes de gravar a nova.

## Auditoria

Depois do ETL:

```powershell
..\venv\Scripts\python.exe audit_etl_runtime.py
```

Relatório gerado em:

`docs/RELATORIO_AUDITORIA_ETL_IC.md`

O relatório mostra cobertura municipal por eixo, fonte, ano, registros no histórico, registros no snapshot e indicadores pendentes.

## Teste limitado

Para testar somente Apucarana:

```powershell
..\venv\Scripts\python.exe run_etl_apucarana.py
```

Esse script não substitui a execução nacional.

## Cuidados metodológicos

- Não transformar ausência em zero.
- Não usar CNES como proxy de prontuário eletrônico, consultas remotas ou gerador hospitalar sem fonte semântica adequada.
- Não chamar saldo CAGED de taxa de desemprego.
- Registrar sempre fonte, ano e cobertura.
- Revisar o relatório de auditoria antes de publicar resultados.
