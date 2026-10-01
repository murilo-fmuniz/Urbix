# Urbix — Resumo de uma página para a IC

Atualizado em **01/10/2026**.

## O que é

Plataforma para consolidar dados públicos municipais, normalizar indicadores e produzir rankings com TOPSIS, preservando fonte, ano e cobertura.

## Estado atual

- **5.571 municípios** cadastrados;
- **130.579 registros** com valor no histórico/snapshot;
- **19 indicadores** calculáveis no TOPSIS;
- Backend FastAPI + PostgreSQL;
- Frontend React/Vite;
- ETL nacional com SIDRA, SICONFI, MUNIC, SNIS, CAGED, CNES, FBSP e banda larga;
- auditoria de cobertura por eixo.

## Eixos

- Economia e Governança;
- Sociedade e Segurança;
- Educação e Inovação;
- Sustentabilidade e Smart City;
- Resiliência e Desastres;
- Conectividade.

## Indicadores de maior cobertura

- população, PIB e domicílios: aproximadamente 5.570 municípios;
- água SNIS: acima de 5.500;
- MUNIC de bombeiros e TIC: acima de 5.500;
- banda larga: 5.570;
- relação estudante/professor: 5.571.

## Limitações

- homicídios ainda possui cobertura insuficiente;
- indicadores de saúde digital aguardam fonte específica;
- eventos climáticos possuem cobertura regional;
- CAGED representa movimentação formal, não desemprego total;
- ausências não são convertidas em zero.

## Demonstração

1. Selecionar três municípios no frontend.
2. Executar o ranking.
3. Mostrar `pontuacao_topsis` e `valores_calculados`.
4. Mostrar fonte/ano no histórico.
5. Apresentar `RELATORIO_AUDITORIA_ETL_IC.md` como evidência de cobertura.

## Contribuição

O projeto demonstra uma arquitetura reprodutível para transformar fontes públicas heterogêneas em indicadores municipais comparáveis, incluindo tratamento explícito de ausência, cobertura e limitações semânticas.
