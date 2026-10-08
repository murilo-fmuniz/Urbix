# Urbix — Continuidade da Iniciação Científica

Atualizado em **01/10/2026**, após a execução nacional do ETL.

## Estado atual

- Backend FastAPI com PostgreSQL.
- ETL nacional híbrido com SIDRA, SICONFI e datalake local.
- Snapshot `valores_indicadores_latest` usado pelo TOPSIS.
- Frontend React/Vite publicado na Vercel.
- Backend publicado no Render.
- 19 indicadores atualmente calculáveis no ranking.
- 5.571 municípios cadastrados.
- 130.381 registros com valor no histórico e no snapshot atual.

Os números detalhados e a cobertura por eixo estão em `RELATORIO_AUDITORIA_ETL_IC.md`.

## Indicadores com melhor cobertura

- população, PIB, força de trabalho e domicílios: aproximadamente 5.570 municípios;
- relação estudante/professor: 5.571;
- saneamento SNIS de água: acima de 5.500;
- bombeiros e estrutura TIC MUNIC: acima de 5.550;
- banda larga: 5.570;
- SICONFI: 5.275 respostas válidas em 5.571 consultas; cobertura persistida de aproximadamente 3.000 municípios por indicador;
- esgoto SNIS: aproximadamente 3.400 municípios.

## Indicadores que permanecem pendentes

- IDEB: arquivo não disponível no caminho configurado;
- homicídios: cobertura atual de apenas 27 municípios;
- CAGED TIC: precisa de filtro CBO;
- sobrevivência de negócios: proxy inadequado;
- empregos informais: proxy inadequado;
- prontuário eletrônico e consultas remotas: CNES não comprova esses conceitos;
- gerador hospitalar: fonte atual não comprova a infraestrutura;
- moradias inadequadas: coluna MUNIC ainda não confirmada;
- eventos climáticos: cobertura regional, principalmente RS;
- CadÚnico: arquivo não disponível no datalake atual.

## Como executar o ETL nacional

```powershell
cd backend\tools
..\venv\Scripts\python.exe local_etl_service.py
```

O comando nacional não recebe filtro de município. O arquivo `run_etl_apucarana.py` é apenas um teste isolado.

Depois da carga:

```powershell
..\venv\Scripts\python.exe audit_etl_runtime.py
```

O relatório é salvo em `docs/RELATORIO_AUDITORIA_ETL_IC.md`.

## Arquitetura de dados

- `valores_indicadores`: histórico por município, indicador, ano, valor e fonte;
- `valores_indicadores_latest`: último valor usado no TOPSIS;
- `backend/app/etl_config.py`: catálogo de fontes, status e regras;
- `backend/tools/local_etl_service.py`: executor do ETL;
- `scripts/map_data_lake.py`: inventário dos arquivos e colunas do datalake.

## Regras metodológicas

1. Ausência não vira zero.
2. Proxies devem ser nomeados e justificados.
3. CAGED não deve ser apresentado como desemprego populacional.
4. CNES não deve ser apresentado como prontuário eletrônico sem campo específico.
5. Indicadores binários MUNIC devem ser descritos como presença/ausência.
6. SNIS usa o último ano disponível por município; os anos podem variar.
7. Eventos climáticos não devem ser interpretados como cobertura nacional.
8. Toda publicação deve acompanhar fonte, ano e cobertura.

## Próximos passos recomendados

### Alta prioridade

- obter e mapear o arquivo real do IDEB;
- ampliar/corrigir a base municipal de homicídios;
- documentar os códigos MREH e MUNIC usados;
- criar testes automatizados para cobertura mínima;
- registrar o log de cada execução nacional do ETL.

### Média prioridade

- implementar filtro CBO para empregos TIC;
- avaliar fontes oficiais para participação eleitoral e mulheres eleitas;
- revisar os indicadores de resiliência;
- transformar a auditoria em artefato obrigatório do pipeline.

### Baixa prioridade

- explorar PDFs de ODS como referência conceitual;
- integrar novas fontes ambientais;
- ampliar indicadores de mobilidade e saúde somente após validação semântica.

## Para a apresentação da IC

Apresentar o Urbix como um núcleo funcional de ingestão, normalização e ranking municipal. O sistema possui dados reais e ampla cobertura em economia, conectividade, educação básica, saneamento e infraestrutura municipal, mas mantém indicadores pendentes fora do TOPSIS quando a fonte ou a semântica não é suficiente.
