# ✅ Setup Checklist - Urbix Admin Panel

Guia passo a passo para configurar e testar o painel administrativo completo.

## 🔧 Backend Setup

- [ ] **1. Ativar Virtual Environment**
  ```bash
  cd backend
  .\venv\Scripts\activate
  ```

- [ ] **2. Criar Database Schema**
  ```bash
  alembic upgrade head
  ```
  ✅ Esperado: Migrations executadas com sucesso

- [ ] **3. Semear Indicadores ISO 37122**
  ```bash
  python seed_indicadores.py
  ```
  ✅ Esperado: 37 indicadores criados

- [ ] **4. Iniciar Backend Server**
  ```bash
  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```
  ✅ Esperado: "Application startup complete" na console

- [ ] **5. Verificar Backend**
  ```bash
  curl http://localhost:8000/docs
  # Abrir em navegador para ver Swagger UI
  ```

## 🎨 Frontend Setup

- [ ] **1. Instalar Dependências**
  ```bash
  cd frontend
  npm install
  ```

- [ ] **2. Iniciar Dev Server**
  ```bash
  npm run dev
  ```
  ✅ Esperado: "VITE v... ready in ... ms" na console

- [ ] **3. Abrir Navegador**
  ```
  http://localhost:5173/
  ```

## 🧪 Testes Funcionais

### Dashboard

- [ ] **Acessar Dashboard**
  - URL: `http://localhost:5173/dashboard`
  - ✅ Deve exibir lista de indicadores

- [ ] **Testar Filtros**
  - Filtro por Cidade: Funciona?
  - Filtro por Norma: Funciona?
  - Filtro por Grande Área: Funciona?

- [ ] **Verificar Cards**
  - Cards exibem dados corretos?
  - Auditoria information is visible?
  - Status badge funciona?

### Admin Panel

- [ ] **Acessar Admin Panel**
  - URL: `http://localhost:5173/admin`
  - ✅ Formulário com 6 seções deve aparecer

- [ ] **Preencher Formulário**
  1. Cidade: "Londrina"
  2. Estado: "PR"
  3. Ano: 2026
  4. Preencher pelo menos um field de cada seção

- [ ] **Submeter Formulário**
  - Clicar "✅ Inserir Dados da Cidade"
  - ✅ Deve exibir mensagem de sucesso verde

- [ ] **Verificar Dashboard**
  - Ir para Dashboard
  - Filtrar por "Londrina"
  - ✅ Novos indicadores devem aparecer

## 🔍 Verificação de Dados

### Via Terminal

```bash
# 1. Verificar count de indicadores
curl http://localhost:8000/api/v1/indicadores | jq 'length'
# Esperado: 37

# 2. Verificar um indicador específico
curl http://localhost:8000/api/v1/indicadores/ECO.1 | jq '.'

# 3. Via SQLite
sqlite3 urbix.db "SELECT COUNT(*) FROM indicadores;"
sqlite3 urbix.db "SELECT codigo_indicador, nome FROM indicadores LIMIT 5;"
```

## 📝 Teste Completo de Fluxo

Scenario: Inserir dados de 3 cidades via Admin Panel

### Cidade 1: Maringá

1. Abrir Admin: `http://localhost:5173/admin`
2. Preencher:
   - Cidade: **Maringá**
   - Estado: **PR**
   - População: **130134**
   - Área: **556.99**
   - PIB: **5000000000**
   - Mais alguns campos...
3. Submeter
4. ✅ Verificar sucesso

### Cidade 2: Londrina

1. (Repetir para Londrina)
2. Preencher dados de Londrina
3. Submeter

### Cidade 3: Apucarana

1. (Repetir para Apucarana)
2. Preencher dados de Apucarana
3. Submeter

### Verificação Final

1. Ir para Dashboard
2. Filtrar por: **Cidade = "Maringá"**
   - ✅ Deve mostrar dados de Maringá
3. Filtrar por: **Grande Área = "Saúde"**
   - ✅ Deve mostrar indicadores de saúde
4. Limpar filtros
   - ✅ Deve mostrar todas as 3 cidades

## 🐛 Troubleshooting

| Problema | Causa | Solução |
|----------|-------|---------|
| 404 Backend | Server não rodando | `python -m uvicorn app.main:app --reload` |
| 404 Frontend | Dev server não rodando | `npm run dev` |
| "Erro ao inserir dados" | API error | Ver devtools (F12) / console backend |
| Nenhum indicador no Dashboard | Seed não rodou | `python seed_indicadores.py` |
| Banco sem tabelas | Alembic não executado | `alembic upgrade head` |
| CORS error | Configuração API | Verificar `src/services/api.js` baseURL |

## 📊 Estrutura de Pastas

```
Urbix/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   └── indicadores.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   └── main.py
│   ├── data/
│   │   └── seed_indicadores_iso37122.json ✅
│   ├── seed_indicadores.py ✅
│   ├── SEED_GUIDE.md ✅
│   └── alembic/
│       └── versions/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── AdminPage.jsx ✅
│   │   │   └── DashboardPage.jsx
│   │   ├── components/
│   │   └── services/
│   │       └── api.js
│   ├── ADMIN_PANEL_GUIDE.md ✅
│   └── package.json
└── SETUP_CHECKLIST.md ✅ (você está aqui)
```

## 🎯 Próximas Etapas

Após completar este checklist:

1. **Testes Automatizados**
   ```bash
   cd backend
   pytest tests/test_indicadores.py -v
   ```

2. **Configuração de Produção**
   - Usar PostgreSQL em vez de SQLite
   - Configurar variáveis de ambiente
   - Setup do `.env`

3. **Funcionalidades Avançadas**
   - [ ] Upload de arquivo CSV
   - [ ] Validação de dados por indicador
   - [ ] Histórico de alterações
   - [ ] Comparação entre períodos

## 💡 Dicas

- **Debug**: Usar `jq` para pretty-print JSON no terminal
- **Logs**: Frontend: F12 DevTools | Backend: Console do terminal
- **Refresh**: `Ctrl+Shift+R` para limpar cache do navegador
- **Restart**: Às vezes é necessário restart do backend/frontend após mudanças

---

**Status**: ✅ Pronto para começar!  
**Data**: 15 de Março de 2026  
**Versão**: 1.0
