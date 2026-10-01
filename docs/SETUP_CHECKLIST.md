# Checklist atual de setup

## Backend

- [ ] Criar/ativar `backend/venv`.
- [ ] Instalar `backend/requirements.txt`.
- [ ] Criar `backend/.env` com `DATABASE_URL` do PostgreSQL.
- [ ] Confirmar acesso ao banco.
- [ ] Subir `python -m uvicorn app.main:app --reload`.
- [ ] Abrir `http://localhost:8000/docs`.

## ETL

- [ ] Confirmar arquivos em `backend/data/planilhas`.
- [ ] Executar `backend/tools/local_etl_service.py` para todos os municípios.
- [ ] Gerar `backend/tools/audit_etl_runtime.py`.
- [ ] Revisar `docs/RELATORIO_AUDITORIA_ETL_IC.md`.
- [ ] Confirmar que o snapshot foi atualizado.

## Frontend

- [ ] Instalar Node.js e dependências com `npm install`.
- [ ] Configurar `frontend/.env.local` com `VITE_API_URL=http://localhost:8000`.
- [ ] Executar `npm run dev`.
- [ ] Abrir `/ranking`.
- [ ] Selecionar ao menos duas cidades.
- [ ] Confirmar resposta do ranking e valores calculados.

## Validação final

- [ ] `POST /topsis/ranking-hibrido` retorna HTTP 200.
- [ ] A resposta contém pontuação e indicadores.
- [ ] Histórico apresenta fonte e ano.
- [ ] O relatório de auditoria foi salvo.
- [ ] Nenhuma credencial ou dado bruto foi adicionado ao Git.
