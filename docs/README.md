# Documentação do Urbix

## Documentos essenciais

- `RELATORIO_AUDITORIA_ETL_IC.md`: resultado mais recente do ETL, com cobertura por eixo, fonte e município.
- `PROXIMOS_PASSOS_CONTINUIDADE_IC.md`: transição e continuidade da Iniciação Científica.
- `MATRIZ_FONTES_PUBLICAS_URBIX.md`: fontes públicas, indicadores e critérios metodológicos.
- `ARCHITECTURE.md`: arquitetura do sistema.
- `ARQUITETURA_TECNICA.md`: visão técnica complementar.
- `DEPLOYMENT_GUIDE_FINAL.md`: publicação e operação.
- `INTEGRATION_TESTING_GUIDE.md`: testes de integração.
- `ADVISOR_PRESENTATION_GUIDE.md`: roteiro de apresentação para orientação/banca.
- `ADVISOR_PRESENTATION_ONEPAGE.md`: resumo de uma página para apresentação.
- `DADOS_MANUAIS_HISTORICOS.md`: uso de dados manuais e histórico.
- `ETL_PROCESS_LOCAL_DATA.md`: processamento de dados locais.
- `ETL_RESUMO_ENTREGA.md`: resumo do pipeline ETL.

## Fontes e inventário

- `../dicionario_de_dados_etl.md`: inventário gerado por `scripts/map_data_lake.py`.
- `MATRIZ_FONTES_PUBLICAS_URBIX.md`: matriz metodológica de fontes.

## Regra de leitura

Documentos de implementação antigos foram removidos para evitar conflito com o código atual. Para números atuais, prevalecem:

1. `docs/RELATORIO_AUDITORIA_ETL_IC.md`;
2. `backend/app/etl_config.py`;
3. `backend/tools/local_etl_service.py`;
4. `backend/README.md` e `frontend/README.md`.
