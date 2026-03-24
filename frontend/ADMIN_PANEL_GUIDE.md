# 🏛️ AdminPage - Painel de Administração Urbix

## Visão Geral

O **AdminPage** é a interface administrativa da plataforma Urbix para inserir e gerenciar dados de novos municípios. O sistema segue o padrão **ISO 37122:2019** para indicadores de cidades inteligentes e sustentáveis.

## 📊 Indicadores Disponíveis

O sistema possui **37 indicadores** organizados em 8 categorias:

### 1️⃣ **Economia** (ECO)
- **ECO.1**: População Total
- **ECO.2**: Área Total (km²)
- **ECO.3**: PIB Total
- **ECO.4**: Despesas em Ativos Fixos (CAPEX)
- **ECO.5**: Novos Negócios/Empresas

### 2️⃣ **Educação** (EDU)
- **EDU.1**: População Economicamente Ativa (PEA)
- **EDU.2**: Desemprego
- **EDU.3**: Acesso a Internet de Banda Larga
- **EDU.4**: Diplomados em STEM
- **EDU.5**: Alunos Matriculados na Rede Pública
- **EDU.6**: Dispositivos Digitais nas Escolas

### 3️⃣ **Governança** (GOV)
- **GOV.1**: Eleitores Registrados
- **GOV.2**: Comparecimento Eleitoral
- **GOV.3**: Despesas Totais do Município
- **GOV.4**: Serviços Urbanos Oferecidos
- **GOV.5**: Serviços 100% Online
- **GOV.6**: Visitas ao Portal de Dados Abertos

### 4️⃣ **Saúde** (SAU)
- **SAU.1**: Cobertura de Plano de Saúde Privado
- **SAU.2**: Teleconsultas Realizadas
- **SAU.3**: Total de Hospitais
- **SAU.4**: Hospitais com Gerador de Energia

### 5️⃣ **Habitação** (HAB)
- **HAB.1**: Pessoas em Moradias Inadequadas
- **HAB.2**: Total de Edifícios/Imóveis
- **HAB.3**: Edifícios Vulneráveis a Desastres

### 6️⃣ **Ambiente** (AMB)
- **AMB.1**: Área Gerida por SIG
- **AMB.2**: Área Coberta por Copas de Árvores
- **AMB.3**: Volume de Água Potável Distribuído
- **AMB.4**: Volume de Água com Monitoramento Quality
- **AMB.5**: Plástico Gerado
- **AMB.6**: Plástico Reciclado

### 7️⃣ **Segurança** (SEG)
- **SEG.1**: Efetivo Total de Policiais
- **SEG.2**: Homicídios
- **SEG.3**: Área Coberta por Câmeras de Segurança

### 8️⃣ **Resiliência** (RES)
- **RES.1**: Total de Equipes de Emergência
- **RES.2**: Equipes com Treinamento para Desastres
- **RES.3**: Pessoas Evacuadas/Desalojadas
- **RES.4**: Perda Financeira por Desastres

## 🚀 Como Usar

### 1. **Acesso ao Painel**

```
URL: http://localhost:3000/admin
```

Navegue até a seção "Admin" no menu principal ou acesse diretamente via URL.

### 2. **Preenchimento do Formulário**

#### Informações Obrigatórias:
- **Cidade**: Nome da cidade (ex: "Maringá", "Londrina")
- **Estado**: Sigla do estado com 2 letras (ex: "PR", "SP")
- **Ano de Referência**: Ano dos dados (padrão: 2026)

#### Seções de Dados:
O formulário está organizado em 6 grandes seções. Preencha os campos com base nos dados disponíveis para a cidade:

1. **Denominadores Universais** - Dados base da cidade
2. **Dados Demográficos** - Informações populacionais
3. **Prefeitura e Finanças** - Dados orçamentários e serviços
4. **Infraestrutura e Saúde** - Educação, telecomunicações, saúde
5. **Segurança Pública** - Recursos de segurança e desastres
6. **Meio Ambiente** - Recursos naturais e sustentabilidade

### 3. **Submissão**

**Botão**: "✅ Inserir Dados da Cidade"

O sistema irá:
1. ✅ Validar entrada obrigatória (Cidade e Estado)
2. ✅ Filtrar campos vazios
3. ✅ Criar coletas para cada indicador preenchido
4. ✅ Registrar auditoria automática
5. ✅ Exibir confirmação de sucesso

### 4. **Feedback**

- ✅ **Sucesso**: Mensagem verde mostrando quantos indicadores foram inseridos
- ❌ **Erro**: Mensagem vermelha com detalhes do problema

## 🔧 Configuração do Backend

### Pré-requisitos

1. **Python 3.14+** com venv ativado
2. **Banco de dados** com tabelas criadas (Alembic)
3. **Indicadores seeded** (ISO 37122)

### Passos de Configuração

#### 1. Criar Migrations (primeira vez)

```bash
cd backend
alembic upgrade head
```

#### 2. Semear Indicadores

```bash
python seed_indicadores.py
```

**Esperado:**
```
🌱 Iniciando semeadura de indicadores ISO 37122...

✅ Indicador criado: ECO.1 - População Total
✅ Indicador criado: ECO.2 - Área Total
...
============================================================
📊 Resumo:
  ✅ Indicadores criados: 37
  ⏭️  Indicadores existentes: 0
  📈 Total de indicadores no arquivo: 37
============================================================
```

#### 3. Iniciar Backend

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Esperado:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

#### 4. Iniciar Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📡 API Endpoints

### GET - Listar Indicadores

```bash
curl "http://localhost:8000/api/v1/indicadores"
```

**Filtros opcionais:**
- `?cidade=Maringá`
- `?norma=ISO 37122`
- `?grande_area=Saúde`

### POST - Criar Coleta

```bash
curl -X POST "http://localhost:8000/api/v1/indicadores/ECO.1/coletas" \
  -H "Content-Type: application/json" \
  -d '{
    "cidade": "Maringá",
    "estado": "PR",
    "ano_referencia": 2026,
    "valor_final": 130134,
    "dado_disponivel": true,
    "auditoria": {
      "fonte_nome": "Admin",
      "data_extracao": "2026-03-15",
      "observacoes": "Dados inseridos via painel admin"
    }
  }'
```

## 💾 Estrutura de Dados

### Fluxo de Submissão

```
AdminPage (Frontend)
    ↓
getIndicadores() [carrega lista de indicadores]
    ↓
handleSubmit() [Processa formulário]
    ↓
criarColeta(codigo, dados) [Para cada indicador preenchido]
    ↓
POST /api/v1/indicadores/{codigo}/coletas [Backend API]
    ↓
DadosColeta + Auditoria criados no banco
```

### Modelo de Dados

```
Indicador (mestre)
├── codigo_indicador: "ECO.1"
├── nome: "População Total"
├── norma: "ISO 37122:2019"
├── grande_area: "Economia"
├── metodologia: {...}
└── dados_coleta: [
    {
      id: 1,
      cidade: "Maringá",
      estado: "PR",
      ano_referencia: 2026,
      valor_final: 130134,
      dado_disponivel: true,
      auditoria: {
        fonte_nome: "Admin",
        data_extracao: "2026-03-15",
        observacoes: "Dados inseridos via painel admin"
      }
    }
  ]
```

## 📝 Exemplo de Uso Completo

### 1. Acessar AdminPage

Navegue para: `http://localhost:3000/admin`

### 2. Preencher Dados de Maringá (2026)

| Seção | Campo | Valor |
|-------|-------|-------|
| Básico | Cidade | Maringá |
| Básico | Estado | PR |
| Básico | Ano | 2026 |
| Denominadores | População Total | 130134 |
| Denominadores | Área Total | 556.99 |
| Denominadores | PIB Total | 5000000000 |
| ... | ... | ... |

### 3. Submeter

Clicar em "✅ Inserir Dados da Cidade"

### 4. Verificar no Dashboard

Ir para: `http://localhost:3000/dashboard`
- Filtrar por cidade: "Maringá"
- Ver indicadores inseridos

## 🐛 Troubleshooting

### Erro: "Erro ao inserir dados"

**Possíveis causas:**
- Backend não está rodando
- URL base incorreta (verificar `api.js`)
- Formato de dados inválido

**Solução:**
```bash
# 1. Verificar se backend está running
curl http://localhost:8000/docs

# 2. Verificar logs do backend
# Procurar por mensagens de erro no terminal

# 3. Testar API diretamente
curl "http://localhost:8000/api/v1/indicadores/ECO.1"
```

### Erro: "Indicador não encontrado"

**Causa:** Indicador não foi seeded

**Solução:**
```bash
python seed_indicadores.py
```

### Erro: "no such table: indicadores"

**Causa:** Migrations não foram executadas

**Solução:**
```bash
alembic upgrade head
```

## 📚 Recursos Adicionais

- [ISO 37122:2019](https://www.iso.org/standard/69050.html) - Smart cities and communities - Indicators for city services and quality of life
- [Backend Documentation](../backend/MIGRACAO_SQLITE_POSTGRESQL.md)
- [API Response Structure](../backend/app/schemas.py)

## 🎯 Próximos Passos

- [ ] Implementar upload de arquivo CSV para inserção em massa
- [ ] Adicionar validação de dados (limites mín/máx por indicador)
- [ ] Criar histórico de alterações (versioning)
- [ ] Implementar dashboard de monitoramento de qualidade de dados
- [ ] Adicionar comparação entre períodos

---

**Versão:** 1.0  
**Última atualização:** 15 de Março de 2026  
**Status:** ✅ Produção
