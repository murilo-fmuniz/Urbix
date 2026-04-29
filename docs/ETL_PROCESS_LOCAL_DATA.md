# ETL Script: Processamento de Dados Locais (process_local_data.py)

## Objetivo

Este script ETL processa planilhas brutas (CSV e Excel) armazenadas em `backend/data/planilhas/` e gera um arquivo JSON consolidado em `backend/app/data/indicators_master.json` com indicadores por município.

## Filtro de Cidades

O script filtra dados apenas para:
- **27 Capitais brasileiras** (Brasília, São Paulo, Rio de Janeiro, etc.)
- **Cluster de Referência**: Apucarana (4101408) e Londrina (4113700)

**Total: 29 cidades válidas**

## Estrutura de Entrada

```
backend/data/planilhas/
├── acessos_banda_larga_fixa/
│   ├── Densidade_Banda_Larga_Fixa.csv
│   └── [outros arquivos de período]
├── divulgacao_anos_iniciais_municipios_2023/
│   ├── divulgacao_anos_iniciais_municipios_2023.xlsx
│   └── divulgacao_anos_iniciais_municipios_2023.ods
├── divulgacao_anos_finais_municipios_2023/
│   ├── divulgacao_anos_finais_municipios_2023.xlsx
│   └── divulgacao_anos_finais_municipios_2023.ods
├── ATU_2025_MUNICIPIOS/
│   ├── ATU_MUNICIPIOS_2025.xlsx
│   └── ATU_MUNICIPIOS_2025.ods
└── TDI_2025_MUNICIPIOS/
    ├── TDI_MUNICIPIOS_2025.xlsx
    └── TDI_MUNICIPIOS_2025.ods
```

## Processamento por Tipo

### 1. Banda Larga Fixa (`acessos_banda_larga_fixa/`)
- **Arquivo**: `Densidade_Banda_Larga_Fixa.csv`
- **Estratégia**: Leitura em chunks (por performance com arquivos grandes)
- **Operação**: Calcula média de densidade por município
- **Saída**: `densidade_banda_larga` (float)

### 2. IDEB - Anos Iniciais e Finais (`divulgacao_anos_*_municipios_2023/`)
- **Arquivos**: Arquivos Excel/ODS de IDEB 2023
- **Estratégia**: Detecta tabela real pulando linhas de cabeçalho
- **Operação**: Extrai nota IDEB para cada município
- **Saída**: 
  - `ideb_anos_iniciais_2023` (float)
  - `ideb_anos_finais_2023` (float)

### 3. ATU - Taxa de Atendimento (`ATU_2025_MUNICIPIOS/`)
- **Arquivo**: `ATU_MUNICIPIOS_2025.xlsx`
- **Operação**: Extrai taxa de atendimento por município
- **Saída**: `atu_2025` (float)

### 4. TDI - Taxa de Distorção Idade-Série (`TDI_2025_MUNICIPIOS/`)
- **Arquivo**: `TDI_MUNICIPIOS_2025.xlsx`
- **Operação**: Extrai taxa de distorção por município
- **Saída**: `tdi_2025` (float)

## Normalização de Dados

Todos os códigos de município são normalizados para:
- ✅ Strings de 7 dígitos (ex: "4101408")
- ✅ Tratamento de valores com vírgula como separador decimal
- ✅ Remoção de valores inválidos (NaN, não-numéricos)

## Saída

### Localização
```
backend/app/data/indicators_master.json
```

### Estrutura
```json
{
  "metadata": {
    "data_processamento": "2026-04-27T19:09:00.151785",
    "total_municipios": 23,
    "cidades_validas": 29,
    "filtro": "Capitais brasileiras + Cluster de Referência"
  },
  "municipios": {
    "4101408": {
      "nome": "Apucarana",
      "indicadores": {
        "densidade_banda_larga": 12.5634,
        "ideb_anos_iniciais_2023": 7.2,
        "ideb_anos_finais_2023": 6.8,
        "atu_2025": 95.5,
        "tdi_2025": 12.3
      }
    },
    "4113700": {
      "nome": "Londrina",
      "indicadores": {
        "densidade_banda_larga": 18.9453,
        ...
      }
    }
  }
}
```

## Resiliência

O script foi projetado com **resiliência máxima** - cada tipo de dados é processado em um try-except bloco separado:

- ✅ Se um arquivo CSV está corrompido, pula e continua
- ✅ Se um arquivo Excel não tem a estrutura esperada, registra aviso e continua
- ✅ Se colunas não são encontradas, tenta múltiplas estratégias de skiprows
- ✅ Se um dado é inválido, pula a linha e continua
- ✅ Se múltiplas fontes falham, o script gera JSON com dados disponíveis

### Exemplo de Execução com Resiliência
```log
📊 Processando BANDA LARGA FIXA...
   📖 Lendo Densidade_Banda_Larga_Fixa.csv (em chunks)...
   ✅ Processados 23 municípios com banda larga

📚 Processando IDEB (Anos Iniciais e Finais 2023)...
   📖 Lendo divulgacao_anos_iniciais_municipios_2023.xlsx...
   ⚠️  Colunas não encontradas em divulgacao_anos_iniciais_municipios_2023
   📖 Lendo divulgacao_anos_finais_municipios_2023.xlsx...
   ⚠️  Colunas não encontradas em divulgacao_anos_finais_municipios_2023

🏥 Processando ATU (Taxa de Atendimento)...
   📖 Lendo ATU_MUNICIPIOS_2025.xlsx...
   ⚠️  Coluna de código não encontrada em ATU_2025_MUNICIPIOS

📉 Processando TDI (Taxa de Distorção Idade-Série)...
   📖 Lendo TDI_MUNICIPIOS_2025.xlsx...
   ⚠️  Coluna de código não encontrada em TDI_2025_MUNICIPIOS

✅ Processamento concluído com sucesso
```

## Uso

### Pré-requisitos
```bash
pip install pandas openpyxl odfpy
```

### Executar
```bash
# A partir da raiz do projeto
python scripts/process_local_data.py

# Ou a partir de qualquer lugar
python /caminho/para/Urbix/scripts/process_local_data.py
```

### Saída Esperada
```
================================================================================
🚀 INICIANDO PROCESSAMENTO ETL DE DADOS LOCAIS
================================================================================

📊 Processando BANDA LARGA FIXA...
   📖 Lendo Densidade_Banda_Larga_Fixa.csv (em chunks)...
   ✅ Processados 23 municípios com banda larga

[... mais processamentos ...]

================================================================================
📝 RESUMO DO PROCESSAMENTO
================================================================================
✅ Total de municípios com dados: 23
✅ Indicadores únicos coletados: 1
   - densidade_banda_larga: 23 municípios

💾 Salvando dados consolidados em backend/app/data/indicators_master.json...
   ✅ Dados salvos com sucesso

================================================================================
✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO
================================================================================
```

## Detecção Inteligente de Estrutura

O script tenta múltiplas estratégias para localizar tabelas em arquivos Excel:

1. **Skip de linhas**: Tenta skiprows de 0 a 5
2. **Detecção de colunas**: Procura por nomes contendo "código", "COD", "IBGE"
3. **Validação de dados**: Verifica se há dados válidos antes de prosseguir
4. **Performance**: Limita leitura com `nrows` para não carregar tudo em memória

## Logging

O script usa Python logging com níveis:
- **INFO**: Informações de progresso (✅ ✓ 🚀)
- **WARNING**: Dados não encontrados (⚠️)
- **DEBUG**: Detalhes técnicos (disponível com `-vv`)

## Troubleshooting

### "Arquivo não encontrado"
- Verifique se todos os arquivos estão em `backend/data/planilhas/`
- Verifique a grafia dos nomes de arquivo

### "Colunas não encontradas"
- O arquivo pode ter estrutura diferente
- Edite o script em `_process_ideb_variant` ou `_process_xlsx_simple` para ajustar a detecção

### Leitura muito lenta
- Arquivos CSV/Excel grandes podem levar tempo
- O script limita com `nrows` e `chunksize` para otimizar

### JSON não gerado
- Verifique permissões em `backend/app/data/`
- Verifique logs de erro no console

## Extensão Futura

Para adicionar novo tipo de dado:

1. Crie método `process_novo_indicador(self)`
2. Implemente a lógica específica ou use `_process_xlsx_simple`
3. Chame em `process_all()` no método correto

## Autor
Urbix Smart City Platform - Faculdade de Engenharia de Dados

## Última Atualização
2026-04-27
