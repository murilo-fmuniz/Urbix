import csv
import gzip
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

import pandas as pd
import requests
from sqlalchemy import text

# Adiciona a raiz da pasta 'backend' ao sys.path para importar os módulos do FastAPI corretamente
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.database import SessionLocal, engine, Base
from app.models import ValorIndicador, Municipio
from app.etl_config import DADOS_BASE, INDICADORES
from tools.seed_metadata import seed_metadata

PLANILHAS_ROOT = backend_dir / "data" / "planilhas"
CATALOGO_IBGE = backend_dir / "app" / "data" / "ibge_catalog.json"
CHUNK_SIZE = 100_000


def _normalizar_texto(valor: str) -> str:
    texto = unicodedata.normalize("NFKD", str(valor))
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.strip().lower()
    texto = re.sub(r"\s+", " ", texto)
    return texto


def _carregar_catalogo_ibge() -> dict[str, str]:
    if not CATALOGO_IBGE.exists():
        return {}
    try:
        payload = json.loads(CATALOGO_IBGE.read_text(encoding="utf-8"))
        municipios = payload.get("municipalities", []) if isinstance(payload, dict) else payload
        lookup: dict[str, str] = {}
        for item in municipios:
            if not isinstance(item, dict):
                continue
            codigo = str(item.get("codigo_ibge") or item.get("codigo") or item.get("id") or "").strip()
            if codigo:
                lookup[codigo] = codigo.zfill(7)
                if len(codigo) >= 6:
                    lookup[codigo[:6]] = codigo
        return lookup
    except Exception:
        return {}


IBGE_LOOKUP = _carregar_catalogo_ibge()


def _escolher_melhor_coluna(colunas, alvo: str) -> str | None:
    alvo_norm = _normalizar_texto(alvo)
    for coluna in colunas:
        if _normalizar_texto(coluna) == alvo_norm:
            return coluna
    for coluna in colunas:
        if alvo_norm in _normalizar_texto(coluna):
            return coluna
    return None


def _normalizar_codigo_ibge(valor) -> str | None:
    if valor is None:
        return None
    codigo = re.sub(r"\D", "", str(valor)).strip()
    if not codigo:
        return None
        
    # Se o código tem 7 dígitos (ou mais), tenta achar no dicionário oficial
    if len(codigo) >= 7:
        codigo = codigo[-7:]
        # Só retorna se existir de verdade no IBGE_LOOKUP
        return IBGE_LOOKUP.get(codigo) or IBGE_LOOKUP.get(codigo[:6])
        
    # Se tem 6 dígitos, tenta achar também
    if len(codigo) == 6:
        return IBGE_LOOKUP.get(codigo)
        
    # Se não for nada disso, é lixo (como 0999999). Devolve None para o script ignorar.
    return None


def _ler_csv_flexivel(caminho: Path, kwargs: dict):
    """Retorna um reader em chunks para não carregar o arquivo inteiro na memória."""
    encodings = [kwargs.get("encoding"), "utf-8", "latin1", "cp1252"]
    encodings = [enc for enc in encodings if enc]
    sample_size = int(kwargs.get("sample_size", 8192))
    last_error: Exception | None = None

    def _infer_separator(sample_text: str) -> str:
        candidatos = [";", "\t", ",", "|"]
        try:
            return csv.Sniffer().sniff(sample_text, delimiters="".join(candidatos)).delimiter
        except Exception:
            for sep in candidatos:
                if sample_text.count(sep) > 0:
                    return sep
            return ";"

    for encoding in encodings:
        try:
            if caminho.name.lower().endswith(".gz"):
                with gzip.open(caminho, "rt", encoding=encoding, errors="replace") as handle:
                    sample = handle.read(sample_size)
            else:
                with caminho.open("r", encoding=encoding, errors="replace") as handle:
                    sample = handle.read(sample_size)

            sep = _infer_separator(sample)

            leitura_kwargs = dict(kwargs)
            for key in ["encoding", "sep", "usecols", "header", "sheet_name", "sample_size"]:
                leitura_kwargs.pop(key, None)

            leitura_kwargs.update({
                "encoding": encoding,
                "sep": sep,
                "on_bad_lines": "skip",
                "engine": "python",
                "chunksize": CHUNK_SIZE,
            })
            if caminho.name.lower().endswith(".gz"):
                leitura_kwargs["compression"] = "gzip"

            return pd.read_csv(caminho, **leitura_kwargs)
        except Exception as exc:
            last_error = exc
            continue

    raise last_error or RuntimeError(f"Falha ao ler CSV/TXT: {caminho}")


def _agrupar_valores_por_cidade(df_chunk: pd.DataFrame) -> pd.DataFrame:
    """Agrupa linhas repetidas por município para manter uma única observação por cidade/indicador/ano."""
    cols = ["codigo_ibge", "valor_numerico"]
    if df_chunk.empty:
        return df_chunk[cols].copy()

    return (
        df_chunk.loc[:, cols]
        .dropna(subset=["codigo_ibge", "valor_numerico"])
        .groupby("codigo_ibge", as_index=False)["valor_numerico"]
        .sum()
        .copy()
    )


def _deduplicar_mais_recente(registros: list[ValorIndicador]) -> list[ValorIndicador]:
    """Mantém somente o valor mais recente por cidade + indicador."""
    melhor_por_chave: dict[tuple[str, str], ValorIndicador] = {}

    for registro in registros:
        chave = (str(registro.codigo_ibge), str(registro.id_indicador))
        atual = melhor_por_chave.get(chave)
        if atual is None:
            melhor_por_chave[chave] = registro
            continue

        if registro.ano_referencia > atual.ano_referencia:
            melhor_por_chave[chave] = registro
            continue

        if registro.ano_referencia == atual.ano_referencia and getattr(registro, "id", 0) > getattr(atual, "id", 0):
            melhor_por_chave[chave] = registro

    return list(melhor_por_chave.values())


def _salvar_lote_streaming(db_session, registros: list[ValorIndicador], id_variavel: str, origem: str):
    if not registros:
        return 0

    registros = _deduplicar_mais_recente(registros)
    if not registros:
        return 0

    try:
        db_session.bulk_save_objects(registros)
        db_session.commit()
        total = len(registros)
        print(f"✅ {id_variavel}: {total} registros salvos em lote ({origem})")
        return total
    except Exception as e:
        db_session.rollback() # O nosso famoso escudo Anti-Dominó!
        print(f"❌ Lixo ignorado no lote de {id_variavel} ({origem}) - Transação protegida.")
        return 0


def _resolver_caminho_arquivo(arquivo: str) -> Path | None:
    """Resolve arquivos reais do projeto, inclusive o padrão pasta/arquivo-com-o-mesmo-nome."""
    if not arquivo or arquivo == "NÃO_BAIXADO":
        return None

    candidatos = [
        PLANILHAS_ROOT / arquivo,
        PLANILHAS_ROOT / arquivo / Path(arquivo).name,
    ]

    nome_arquivo = Path(arquivo).name
    if nome_arquivo:
        candidatos.append(PLANILHAS_ROOT / nome_arquivo)
        candidatos.append(PLANILHAS_ROOT / nome_arquivo / nome_arquivo)

    seen = set()
    for caminho in candidatos:
        key = str(caminho.resolve()) if caminho.exists() else str(caminho)
        if key in seen:
            continue
        seen.add(key)
        if caminho.exists() and caminho.is_file():
            return caminho

    return None


def extrair_dados_locais(id_variavel: str, config: dict, db_session, ano_padrao=2024):
    arquivo = config.get("arquivo")
    caminho_completo = _resolver_caminho_arquivo(arquivo)
    if not caminho_completo:
        print(f"❌ {id_variavel}: Arquivo não encontrado -> {arquivo}")
        return

    col_codigo = config.get("coluna_codigo")
    col_valor = config.get("coluna_valor")
    kwargs = dict(config.get("pandas_kwargs", {}))

    if not col_codigo or not col_valor or col_valor == "VERIFICAR_NO_EXCEL":
        return

    # -------------------------------------------------------------
    # 🚀 O SEGREDO 1: Cadastra o 'numerador' como um indicador base!
    # Sem isso, o banco bloqueia dizendo que o indicador não existe.
    # -------------------------------------------------------------
    try:
        db_session.execute(text(f"""
            INSERT INTO indicadores (id, nome, norma_iso, peso, impacto)
            VALUES ('{id_variavel}', '{id_variavel}', 'Base', 1.0, 1)
            ON CONFLICT (id) DO NOTHING;
        """))
        db_session.commit()
    except Exception:
        db_session.rollback()

    print(f"🔄 Lendo {id_variavel} ({caminho_completo.name}) em streaming...")

    try:
        if caminho_completo.name.lower().endswith((".txt", ".csv", ".gz")):
            reader = _ler_csv_flexivel(caminho_completo, kwargs)
            chunks = reader
            has_iterator = True
        else:
            df = pd.read_excel(caminho_completo, **kwargs)
            chunks = [df]
            has_iterator = False

        total_processado = 0
        for chunk_num, chunk in enumerate(chunks, start=1):
            if chunk is None or chunk.empty:
                continue

            col_codigo_real = _escolher_melhor_coluna(chunk.columns, col_codigo)
            col_valor_real = _escolher_melhor_coluna(chunk.columns, col_valor)
            if not col_codigo_real or not col_valor_real:
                continue

            df_chunk = chunk[[col_codigo_real, col_valor_real]].copy()
            df_chunk = df_chunk.dropna(subset=[col_codigo_real, col_valor_real]).copy()

            if df_chunk.empty:
                continue

            df_chunk[col_codigo_real] = df_chunk[col_codigo_real].astype(str).str.replace(r"\D", "", regex=True)
            df_chunk = df_chunk[df_chunk[col_codigo_real].str.len() >= 6].copy()

            df_chunk["codigo_ibge"] = df_chunk[col_codigo_real].map(_normalizar_codigo_ibge)
            df_chunk = df_chunk[df_chunk["codigo_ibge"].notna()].copy()

            df_chunk[col_valor_real] = df_chunk[col_valor_real].astype(str)
            df_chunk["valor_numerico"] = (
                df_chunk[col_valor_real]
                .str.replace(r"[^0-9,.-]", "", regex=True)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            df_chunk["valor_numerico"] = pd.to_numeric(df_chunk["valor_numerico"], errors="coerce")
            df_chunk = _agrupar_valores_por_cidade(df_chunk[["codigo_ibge", "valor_numerico"]]).copy()
            df_chunk = df_chunk.dropna(subset=["valor_numerico"]).copy()

            registros_lote = []
            for row in df_chunk.itertuples(index=False):
                codigo_ibge = getattr(row, "codigo_ibge")
                valor = getattr(row, "valor_numerico")
                
                # -------------------------------------------------------------
                # 🚀 O SEGREDO 2: Filtra os lixos oficiais antes de salvar!
                # -------------------------------------------------------------
                str_codigo = str(codigo_ibge)
                if not str_codigo or pd.isna(valor) or str_codigo in ["0999999", "9999999"] or len(str_codigo) != 7:
                    continue
                    
                registros_lote.append(
                    ValorIndicador(
                        codigo_ibge=str_codigo,
                        id_indicador=id_variavel,
                        ano_referencia=ano_padrao,
                        valor=float(valor),
                        fonte=caminho_completo.name,
                    )
                )

            total_processado += _salvar_lote_streaming(db_session, registros_lote, id_variavel, f"chunk {chunk_num}")

        if total_processado == 0:
            print(f"⚠️ {id_variavel}: nenhum registro foi processado.")

    except Exception as exc:
        print(f"❌ ERRO em {id_variavel}: {exc}")

# ==============================================================================
# NOVOS MOTORES HÍBRIDOS (API PÚBLICA SIDRA E SICONFI)
# ==============================================================================
def extrair_dado_base_sidra(id_variavel: str, config: dict, db_session):
    """Bate no endpoint direto do IBGE e processa o JSON de forma nativa e rápida."""
    print(f"🌐 Buscando {id_variavel} via API SIDRA (IBGE)...")
    try:
        print(f"⏳ Aguardando resposta da API SIDRA para {id_variavel}...")
        response = requests.get(config["url"], timeout=30)
        response.raise_for_status()
        print(f"📡 SIDRA {id_variavel}: status={response.status_code}, bytes={len(response.content)}")

        try:
            dados = response.json()
        except ValueError as exc:
            print(f"❌ JSON inválido na API SIDRA {id_variavel}: {exc}")
            return

        if not isinstance(dados, list) or len(dados) == 0:
            print(f"❌ Resposta inesperada da API SIDRA {id_variavel}: tipo={type(dados).__name__}")
            return

        # 1. A MÁGICA: Descobre dinamicamente a coluna correta do IBGE lendo o cabeçalho
        header = dados[0]
        col_municipio = None
        for key, value in header.items():
            if value == "Município (Código)":
                col_municipio = key
                break
                
        if not col_municipio:
            print(f"❌ Coluna de município não encontrada no payload de {id_variavel}.")
            return

        registros_lote = []
        # 2. Pula o cabeçalho (dados[1:]) e processa só os valores
        for registro in dados[1:]:
            if not isinstance(registro, dict):
                continue

            if id_variavel == "forca_de_trabalho":
                # O IBGE atualizou a API. Agora filtramos pelo Total (D4N e D5N)
                if registro.get("D4N") != "Total" or registro.get("D5N") != "Total":
                    continue

            # 3. Puxa pela coluna dinâmica
            ibge_7 = str(registro.get(col_municipio, "")).strip()
            
            # Ignora lixos ou agregados estaduais/nacionais (município sempre tem 7 dígitos)
            if not ibge_7 or len(ibge_7) != 7:
                continue

            try:
                valor_float = float(registro["V"])
                if id_variavel == "pib_absoluto":
                    valor_float *= 1000
            except (TypeError, ValueError):
                continue

            registros_lote.append(
                ValorIndicador(
                    codigo_ibge=ibge_7,
                    id_indicador=id_variavel,
                    ano_referencia=config["ano"],
                    valor=valor_float,
                    fonte=config["fonte"],
                )
            )

        if registros_lote:
            db_session.bulk_save_objects(registros_lote)
            db_session.commit()
            print(f"✅ API {id_variavel}: {len(registros_lote)} municípios populados do IBGE!")
        else:
            print(f"⚠️ API {id_variavel}: nenhuma linha válida foi extraída do payload.")

    except Exception as e:
        # 4. PREVINE O EFEITO DOMINÓ: Limpa a transação com erro para as próximas APIs funcionarem
        db_session.rollback()
        print(f"❌ ERRO API {id_variavel}: {e}")

def extrair_receita_siconfi(id_variavel: str, db_session):
    """Faz loops em todos os municípios cadastrados consultando o Tesouro Nacional com micro-sessões."""
    print(f"🌐 Buscando {id_variavel} via API SICONFI (Tesouro Nacional)...")

    # A db_session original é usada APENAS para buscar a lista de cidades no começo
    cidades = db_session.query(Municipio.codigo_ibge).order_by(Municipio.codigo_ibge.asc()).all()
    if not cidades:
        print("⚠️ SICONFI: nenhuma cidade disponível na base para consulta.")
        return

    registros_lote = []
    base_url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    total_cidades = len(cidades)
    total_inseridos = 0 

    for index, (ibge,) in enumerate(cidades, start=1):
        if index % 50 == 0:
            print(f"🌐 Processando cidade {index}/{total_cidades}: {ibge}...")
            
        params = {
            "an_exercicio": 2023,
            "nr_periodo": 6,
            "co_tipo_demonstrativo": "RREO",
            "no_anexo": "RREO-Anexo 03",
            "id_ente": ibge,
        }
        try:
            res = requests.get(base_url, params=params, timeout=10)
            if res.status_code == 200:
                payload = res.json()
                items = payload.get("items", []) if isinstance(payload, dict) else []
                for item in items:
                    if item.get("cod_conta") == "RREO3ReceitaCorrenteLiquida":
                        valor = item.get("valor")
                        if valor is not None:
                            registros_lote.append(
                                ValorIndicador(
                                    codigo_ibge=ibge,
                                    id_indicador=id_variavel,
                                    ano_referencia=2023,
                                    valor=float(valor),
                                    fonte="API SICONFI / RREO",
                                )
                            )
                        break
        except Exception:
            pass 

        time.sleep(0.15)

        # ---------------------------------------------------------
        # 🚀 O SEGREDO: Abre uma NOVA sessão "Miojo" só pra salvar e fecha
        # ---------------------------------------------------------
        if len(registros_lote) >= 200:
            temp_db = SessionLocal() # Abre conexão fresca!
            try:
                temp_db.bulk_save_objects(registros_lote)
                temp_db.commit()
                total_inseridos += len(registros_lote)
                print(f"💾 Lote salvo com conexão nova! ({total_inseridos} receitas garantidas)")
            except Exception as e:
                temp_db.rollback()
                print(f"❌ Erro ao salvar lote parcial: {e}")
            finally:
                temp_db.close() # Mata a conexão para o Neon não reclamar
                registros_lote = [] 

    # Salva os últimos registros que sobraram
    if registros_lote:
        temp_db = SessionLocal()
        try:
            temp_db.bulk_save_objects(registros_lote)
            temp_db.commit()
            total_inseridos += len(registros_lote)
        except Exception as e:
            temp_db.rollback()
        finally:
            temp_db.close()

    print(f"✅ API SICONFI: {total_inseridos} municípios inseridos com cobertura completa da base!")



def atualizar_snapshot_latest(db_session):
    """Atualiza tabela materializada com o valor mais recente por cidade + indicador."""
    print("\n--- ATUALIZANDO SNAPSHOT DE VALORES MAIS RECENTES ---")
    db_session.execute(text("DELETE FROM valores_indicadores_latest"))

    db_session.execute(text("""
        INSERT INTO valores_indicadores_latest (codigo_ibge, id_indicador, ano_referencia, valor, fonte, id_origem)
        SELECT v.codigo_ibge, v.id_indicador, v.ano_referencia, v.valor, v.fonte, v.id
        FROM valores_indicadores v
        JOIN (
            SELECT codigo_ibge, id_indicador, MAX(ano_referencia) AS ano_max
            FROM valores_indicadores
            GROUP BY codigo_ibge, id_indicador
        ) a
          ON v.codigo_ibge = a.codigo_ibge
         AND v.id_indicador = a.id_indicador
         AND v.ano_referencia = a.ano_max
        JOIN (
            SELECT codigo_ibge, id_indicador, ano_referencia, MAX(id) AS id_max
            FROM valores_indicadores
            GROUP BY codigo_ibge, id_indicador, ano_referencia
        ) b
          ON v.codigo_ibge = b.codigo_ibge
         AND v.id_indicador = b.id_indicador
         AND v.ano_referencia = b.ano_referencia
         AND v.id = b.id_max
    """))

    db_session.commit()
    total = db_session.execute(text("SELECT COUNT(*) FROM valores_indicadores_latest")).scalar()
    print(f"✅ Snapshot atualizado: {total} linhas em valores_indicadores_latest")


def deduplicar_historico_mesmo_ano(db_session):
    """
    Remove duplicatas de carga mantendo apenas a linha mais recente por
    cidade + indicador + ano_referencia.
    Preserva histórico anual e reduz drasticamente o custo do TOPSIS.
    """
    print("\n--- DEDUPLICANDO HISTÓRICO (cidade+indicador+ano) ---")

    total_antes = db_session.execute(text("SELECT COUNT(*) FROM valores_indicadores")).scalar() or 0

    db_session.execute(text("""
        DELETE FROM valores_indicadores
        WHERE id IN (
            SELECT id FROM (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY codigo_ibge, id_indicador, ano_referencia
                        ORDER BY id DESC
                    ) AS rn
                FROM valores_indicadores
            ) t
            WHERE t.rn > 1
        )
    """))

    db_session.commit()

    total_depois = db_session.execute(text("SELECT COUNT(*) FROM valores_indicadores")).scalar() or 0
    removidos = max(0, total_antes - total_depois)
    print(f"✅ Deduplicação concluída: removidos={removidos} | antes={total_antes} | depois={total_depois}")


def run():
    print("=" * 60)
    print("🚀 INICIANDO PIPELINE ETL URBIX HÍBRIDO (STREAMING + APIS)")
    print("=" * 60)

    # 🧹 FAXINA GERAL: Apaga as tabelas sujas do Neon antes de recriar
    #  Base.metadata.drop_all(bind=engine)
    
    Base.metadata.create_all(bind=engine)
    print("ℹ️ Semeando metadados de municípios e indicadores antes da carga de fatos.")
    metadata_status = seed_metadata()
    print(f"✅ Metadados semeados: {metadata_status}")

    db = SessionLocal()

    print("ℹ️ Cadastrando indicadores base no banco de dados...")
    try:
        db.execute(text("""
            INSERT INTO indicadores (id, nome, norma_iso, peso, impacto) VALUES 
            ('populacao_total', 'População Total', 'Base', 1.0, 1),
            ('pib_absoluto', 'PIB Absoluto', 'Base', 1.0, 1),
            ('forca_de_trabalho', 'Força de Trabalho', 'Base', 1.0, 1),
            ('total_domicilios', 'Total de Domicílios', 'Base', 1.0, 1),
            ('receita_total_municipio', 'Receita Total do Município', 'Base', 1.0, 1)
            ON CONFLICT (id) DO NOTHING;
        """))
        db.commit()
        print("✅ Indicadores base cadastrados com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"⚠️ Aviso ao criar indicadores base: {e}")

    print("ℹ️ ETL em modo incremental: mantendo dados históricos existentes e inserindo/atualizando novas cargas.")
    print("\n--- EXTRAINDO DADOS BASE VIA APIS PÚBLICAS ---")
    apis_ibge = {
        "populacao_total": {"url": "https://apisidra.ibge.gov.br/values/t/6579/p/2025/n6/all/v/9324?formato=json", "ano": 2025, "fonte": "SIDRA (6579)"},
        "pib_absoluto": {"url": "https://apisidra.ibge.gov.br/values/t/5938/p/2023/n6/all/v/37?formato=json", "ano": 2023, "fonte": "SIDRA (5938)"},
        "forca_de_trabalho": {"url": "https://apisidra.ibge.gov.br/values/t/6580/p/2022/n6/all/v/1641?formato=json", "ano": 2022, "fonte": "SIDRA Censo (6580)"},
        "total_domicilios": {"url": "https://apisidra.ibge.gov.br/values/t/9922/p/2022/n6/all/v/381/c1/6795?formato=json", "ano": 2022, "fonte": "SIDRA Censo (9922)"},
    }

    ''' DADOS DE APIS SIDRA E SICONFI DESATIVADOS TEMPORARIAMENTE PARA TESTES LOCAIS
    for id_var, config in apis_ibge.items():
        extrair_dado_base_sidra(id_var, config, db)

    extrair_receita_siconfi("receita_total_municipio", db)
    '''


    # -------------------------------------------------------------
    # 🔄 O SEGREDO: Refrescar a conexão principal depois de muita demora!
    # -------------------------------------------------------------
    print("\n🔄 Atualizando conexão principal com o banco (Anti-Timeout)...")
    db.close()              # Fecha a conexão velha que ficou ociosa
    db = SessionLocal()     # Abre uma conexão novinha em folha!

    print("\n--- EXTRAINDO PLANILHAS LOCAIS COMPLEXAS (STREAMING POR CHUNKS) ---")
    for dominio, indicadores in INDICADORES.items():
        for id_ind, regras in indicadores.items():
            if regras["tipo_calculo"] == "direto":
                extrair_dados_locais(id_ind, regras["variavel_direta"], db)
            else:
                extrair_dados_locais(f"{id_ind}_numerador", regras["numerador"], db)

    deduplicar_historico_mesmo_ano(db)
    atualizar_snapshot_latest(db)

    db.close()
    print("\n🎉 ETL FINALIZADO COM SUCESSO!")


if __name__ == "__main__":
    run()