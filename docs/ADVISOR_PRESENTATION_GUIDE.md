# Guia atual para apresentação da IC

Atualizado em 01/10/2026.

## Mensagem central

O Urbix consolida dados públicos municipais em um datalake, normaliza indicadores por município e aplica TOPSIS para comparar cidades. O sistema prioriza rastreabilidade: fonte, ano, valor e cobertura ficam registrados.

## Estado demonstrável

- FastAPI e frontend React operacionais;
- ETL nacional com SIDRA, SICONFI, MUNIC, SNIS, CAGED, CNES, FBSP e banda larga;
- PostgreSQL com histórico e snapshot;
- 5.571 municípios cadastrados;
- 19 indicadores calculáveis no TOPSIS;
- auditoria por eixo em `RELATORIO_AUDITORIA_ETL_IC.md`;
- frontend e backend publicados.

## Demonstração sugerida

1. Abrir `https://urbix-two.vercel.app/ranking`.
2. Selecionar Apucarana, Londrina e Maringá.
3. Gerar o ranking.
4. Mostrar a pontuação e os valores em `valores_calculados`.
5. Abrir o histórico de uma cidade e mostrar fonte/ano.
6. Mostrar o relatório de auditoria por eixo.
7. Explicar por que indicadores sem cobertura ou semântica confirmada não entram no ranking.

## Indicadores de destaque

- população, PIB e domicílios via SIDRA;
- receitas e despesas via SICONFI;
- saneamento via SNIS;
- bombeiros e estrutura TIC via MUNIC;
- banda larga;
- relação estudante/professor;
- saldo de geração de empregos formais via CAGED.

## Limitações a declarar

- SICONFI possui cobertura parcial;
- esgoto SNIS tem cobertura inferior à de água;
- homicídios está temporariamente com cobertura insuficiente;
- indicadores de saúde digital e alguns indicadores de resiliência estão pendentes por falta de fonte semântica adequada;
- saldo CAGED não é taxa de desemprego;
- indicadores binários MUNIC representam presença/ausência.

## Conclusão para a banca

O resultado é um protótipo científico funcional de integração, auditoria e ranqueamento municipal. A contribuição não é apenas mostrar um ranking: é demonstrar uma arquitetura reprodutível para transformar fontes públicas heterogêneas em indicadores comparáveis, preservando limitações e ausência de dados.
