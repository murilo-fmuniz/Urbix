# URBIX - Relatório Final de Cobertura de Indicadores TOPSIS

## 📊 Status: 27 IDs Necessários ao Cálculo

### ✅ COM DADOS COMPLETOS OU PARCIAIS (15 IDs)

| ID | Registros | Status | Impacto |
|----|-----------|--------|--------|
| populacao_total | 5.572 | ✓ Base | 5 indicadores dependem |
| forca_de_trabalho | 5.570 | ✓ Base | 3 indicadores dependem |
| total_domicilios | 4 | ⚠️ Crítico | Colapse após dedup |
| bombeiros_numerador | 11.110 | ✓ | Habilitado |
| densidade_banda_larga | 1.171.839 | ✓ | Habilitado |
| empregos_informais_numerador | 4.504.137 | ✓ | Habilitado |
| empregos_tic_numerador | 4.504.137 | ✓ | Habilitado |
| homicidios_numerador | 189 | ✓ | Habilitado |
| medidores_inteligentes_agua | 105.325 | ✓ | Habilitado |
| orcamento_per_capita | 83.535 | ✓ | Habilitado |
| relacao_estudante_professor | 56.895 | ✓ | Habilitado |
| sem_teto_numerador | 38.997 | ✓ | Habilitado |
| sobrevivencia_negocios_numerador | 4.504.137 | ✓ | Habilitado |

### ❌ FALTAM COMPLETAMENTE (12 IDs)

#### CRÍTICO: Denominadores Base (5)
Precisam ser extraídos de fontes estruturadas para viabilizar 5 indicadores:

| ID | Fonte | Indicador Bloqueado | Prioridade |
|----|-------|-------------------|-----------|
| Total Escolas (INEP) | MUNIC 2024 ou INEP Dados | escolas_conectadas_telegestao | 🔴 ALTA |
| Total Hospitais (CNES) | CNES | hospitais_gerador_backup | 🔴 ALTA |
| Total Pontos Iluminação (MUNIC) | MUNIC 2024 | iluminacao_telegestao | 🔴 ALTA |
| Total Serviços Ofertados (MUNIC) | MUNIC 2024 | servicos_urbanos_online | 🔴 ALTA |
| Total Unidades Saúde (CNES) | CNES | prontuario_eletronico | 🔴 ALTA |

#### SECUNDÁRIO: Numeradores Faltantes (7)
Alguns já têm numerador, outros precisam confirmação de fonte:

| ID | Status Requerido |
|----|----------------|
| consultas_remotas_numerador | Extrair de CNES |
| escolas_conectadas_telegestao_numerador | Extrair de MUNIC (Mtic12a1) |
| hospitais_gerador_backup_numerador | Extrair de CNES |
| iluminacao_telegestao_numerador | Extrair de MUNIC (Mtic06) |
| moradias_inadequadas_numerador | Fonte pendente |
| prontuario_eletronico_numerador | Extrair de CNES |
| servicos_urbanos_online_numerador | Extrair de MUNIC (Mtic10) |

## 🚨 Problema Crítico Identificado

**total_domicilios caiu de 11.143 para 4 registros** após dedup na escala nacional!
- Causa: Deduplicação cirúrgica de base IDs pode ter efeito colateral
- Impacto: Bloquearia `moradias_inadequadas` se/quando numerador for adicionado
- **Ação urgente**: Reprocessar `total_domicilios` via SIDRA com validação

## 📈 Impacto de Implementação

### Cenário Atual (sem fix)
- **Indicadores disponíveis no TOPSIS**: ~13-15
- **Cobertura média**: 40-50% (muitos IDs com poucos registros)

### Cenário Otimista (com 5 denominadores MUNIC/CNES)
- **Indicadores disponíveis no TOPSIS**: ~18
- **Cobertura média**: 60-70%
- **Tempo endpoint**: ~3-5s (estimado)

## ✅ Recomendações Imediatas

### Prioridade 1: Corrigir total_domicilios
```
python tools/backfill_base_indicators.py --all --skip-siconfi --skip-snapshot
# Validar contagem de total_domicilios pós-execução
```

### Prioridade 2: Extrair 5 Denominadores MUNIC/CNES
```
python tools/extract_denominators_munic_cnes.py
# Extrai: Total Escolas, Pontos Iluminação, Serviços, Hospitais, Unidades Saúde
```

### Prioridade 3: Validar e Medir
```
python tools/coverage_simple.py
# Verificar nova cobertura após extrações
```

