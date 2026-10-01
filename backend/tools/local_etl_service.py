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


def _normalizar_filtro(valor) -> str:
    return _normalizar_texto(valor).replace("-", "")


def _aplicar_filtros(df: pd.DataFrame, filtros: dict, colunas: dict) -> pd.DataFrame:
    """Aplica filtros declarativos antes da agregação municipal."""
    for nome, esperado in (filtros or {}).items():
        coluna = colunas.get(nome)
        if not coluna or coluna not in df.columns:
            return df.iloc[0:0].copy()
        valores = esperado if isinstance(esperado, (list, tuple, set)) else [esperado]
        aceitos = {_normalizar_filtro(valor) for valor in valores}
        mascara = df[coluna].map(_normalizar_filtro).isin(aceitos)
        df = df.loc[mascara].copy()
    return df


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
    agregacao = str(config.get("agregacao", "sum")).lower()
    filtros = config.get("filtros", {})
    coluna_ano = config.get("coluna_ano")
    mapa_quali = config.get("mapa_qualitativo", {
        "Sim": "1", "Não": "0", "SIM": "1", "NÃO": "0",
        "NAO": "0", "sim": "1", "não": "0", "nao": "0",
        "S": "1", "N": "0", "Ativo": "1", "Ativa": "1",
        "Inativo": "0", "Inativa": "0",
    })
    faixa_valida = config.get("faixa_valida")

    if not col_codigo or not col_valor or col_valor == "VERIFICAR_NO_EXCEL":
        return

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
        else:
            df = pd.read_excel(caminho_completo, **kwargs)
            chunks = [df]

        # Acumulador global: mantém o resultado por cidade sem misturar anos
        acumulador_cidades = {}
        acumulador_anos = {}
        total_processado = 0

        for chunk_num, chunk in enumerate(chunks, start=1):
            if chunk is None or chunk.empty:
                continue

            colunas_reais = {
                nome: _escolher_melhor_coluna(chunk.columns, nome)
                for nome in set([col_codigo, col_valor, coluna_ano, *filtros.keys()])
                if nome
            }
            chunk = _aplicar_filtros(chunk, filtros, colunas_reais)
            col_codigo_real = colunas_reais.get(col_codigo)
            col_valor_real = colunas_reais.get(col_valor)
            if not col_codigo_real or not col_valor_real:
                continue

            col_ano_real = colunas_reais.get(coluna_ano) if coluna_ano else None
            colunas_leitura = [col_codigo_real, col_valor_real]
            if col_ano_real and col_ano_real not in colunas_leitura:
                colunas_leitura.append(col_ano_real)
            df_chunk = chunk[colunas_leitura].copy()
            df_chunk = df_chunk.dropna(subset=[col_codigo_real, col_valor_real]).copy()

            if df_chunk.empty:
                continue

            df_chunk[col_codigo_real] = df_chunk[col_codigo_real].astype(str).str.replace(r"\D", "", regex=True)
            df_chunk = df_chunk[df_chunk[col_codigo_real].str.len() >= 6].copy()

            df_chunk["codigo_ibge"] = df_chunk[col_codigo_real].map(_normalizar_codigo_ibge)
            df_chunk = df_chunk[df_chunk["codigo_ibge"].notna()].copy()

            df_chunk[col_valor_real] = df_chunk[col_valor_real].astype(str).str.strip()
            
            df_chunk[col_valor_real] = df_chunk[col_valor_real].replace(mapa_quali)

            # 🚀 TRATAMENTO INTELIGENTE DE NÚMEROS (Preserva decimais e corrige o bug de escala)
            def limpar_numero(val):
                if pd.isna(val):
                    return None
                if isinstance(val, (int, float)):
                    return float(val)
                
                texto = str(val).strip()
                # Se tem ponto e vírgula, assume padrão BR (ex: 1.234,56 -> 1234.56)
                if "," in texto and "." in texto:
                    texto = texto.replace(".", "").replace(",", ".")
                # Se tem apenas vírgula, substitui por ponto (ex: 1234,56 -> 1234.56)
                elif "," in texto:
                    texto = texto.replace(",", ".")
                
                # Remove caracteres inválidos mantendo apenas números, ponto e sinal de menos
                texto = re.sub(r"[^0-9.-]", "", texto)
                
                try:
                    return float(texto)
                except ValueError:
                    return None

            df_chunk["valor_numerico"] = df_chunk[col_valor_real].apply(limpar_numero)
            if faixa_valida and len(faixa_valida) == 2:
                minimo, maximo = faixa_valida
                df_chunk.loc[
                    (df_chunk["valor_numerico"] < minimo)
                    | (df_chunk["valor_numerico"] > maximo),
                    "valor_numerico",
                ] = pd.NA
            if col_ano_real:
                df_chunk["ano_numerico"] = pd.to_numeric(df_chunk[col_ano_real], errors="coerce")
            else:
                df_chunk["ano_numerico"] = float(ano_padrao)

            df_chunk = df_chunk.dropna(subset=["valor_numerico", "codigo_ibge"]).copy()
            if agregacao == "latest" and col_ano_real:
                df_chunk = (
                    df_chunk.sort_values(["codigo_ibge", "ano_numerico"])
                    .drop_duplicates(["codigo_ibge", "ano_numerico"], keep="last")
                )
            elif agregacao in {"mean", "max", "min"}:
                agrupador = df_chunk.groupby("codigo_ibge")["valor_numerico"]
                operador = getattr(agrupador, agregacao)()
                df_chunk = operador.reset_index()
                df_chunk["ano_numerico"] = float(ano_padrao)
            else:
                df_chunk = _agrupar_valores_por_cidade(df_chunk[["codigo_ibge", "valor_numerico"]]).copy()
                df_chunk["ano_numerico"] = float(ano_padrao)
            df_chunk = df_chunk.dropna(subset=["valor_numerico"]).copy()

            # Em vez de salvar no banco, nós acumulamos na memória!
            for row in df_chunk.itertuples(index=False):
                str_codigo = str(getattr(row, "codigo_ibge"))
                valor = getattr(row, "valor_numerico")
                
                if not str_codigo or pd.isna(valor) or str_codigo in ["0999999", "9999999"] or len(str_codigo) != 7:
                    continue
                    
                ano = float(getattr(row, "ano_numerico", ano_padrao))
                if agregacao == "latest" and col_ano_real:
                    if str_codigo not in acumulador_anos or ano >= acumulador_anos[str_codigo]:
                        acumulador_anos[str_codigo] = ano
                        acumulador_cidades[str_codigo] = float(valor)
                elif agregacao == "mean":
                    total, quantidade = acumulador_cidades.get(str_codigo, (0.0, 0))
                    acumulador_cidades[str_codigo] = (total + float(valor), quantidade + 1)
                elif agregacao == "max":
                    acumulador_cidades[str_codigo] = max(acumulador_cidades.get(str_codigo, float("-inf")), float(valor))
                elif agregacao == "min":
                    acumulador_cidades[str_codigo] = min(acumulador_cidades.get(str_codigo, float("inf")), float(valor))
                else:
                    acumulador_cidades[str_codigo] = acumulador_cidades.get(str_codigo, 0.0) + float(valor)

            total_processado += len(df_chunk)

        # 🚀 O GRAND FINALE: Salva o dicionário todo de uma vez só!
        registros_lote = []
        for codigo_ibge, valor_total in acumulador_cidades.items():
            ano_registro = acumulador_anos.get(codigo_ibge, ano_padrao)
            if agregacao == "mean":
                total, quantidade = valor_total
                valor_total = total / quantidade if quantidade else None
            if valor_total is None:
                continue
            registros_lote.append(
                ValorIndicador(
                    codigo_ibge=codigo_ibge,
                    id_indicador=id_variavel,
                    ano_referencia=int(ano_registro),
                    valor=valor_total,
                    fonte=caminho_completo.name,
                )
            )

        if registros_lote:
            _salvar_lote_streaming(db_session, registros_lote, id_variavel, "Carga Consolidada")
        elif total_processado == 0:
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
        max_tentativas = 3
        for tentativa in range(1, max_tentativas + 1):
            print(f"⏳ Aguardando SIDRA para {id_variavel} (Tentativa {tentativa}/{max_tentativas})...")
            try:
                # Aumentamos o timeout para 45s para dar tempo do servidor pensar
                response = requests.get(config["url"], timeout=45)
                response.raise_for_status()
                break # Se deu 200 OK, sai do loop de tentativas!
            except requests.exceptions.RequestException as e:
                if tentativa == max_tentativas:
                    raise e # Se falhou 3 vezes, desiste de vez
                import time
                print(f"⚠️ Servidor lento. Aguardando 5s para tentar de novo...")
                time.sleep(5)

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

            # 3. Puxa pela coluna dinâmica
            ibge_7 = str(registro.get(col_municipio, "")).strip()
            
            # Ignora lixos ou agregados estaduais/nacionais
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

def extrair_receita_siconfi(variaveis: list):
    """
    Busca dados no SICONFI de forma atômica. 
    Usa Context Managers (with SessionLocal() as db) para abrir e fechar 
    conexões rapidamente, evitando bloqueios SSL no Neon DB.
    """
    import requests
    import time
    from app.database import SessionLocal
    from app.models import Municipio, ValorIndicador

    print(f"\n🌐 Buscando dados contábeis via API SICONFI (Tesouro Nacional)...")

    # 1. Pega os municípios e fecha o banco imediatamente
    with SessionLocal() as db:
        cidades = db.query(Municipio.codigo_ibge).order_by(Municipio.codigo_ibge.asc()).all()

    if not cidades:
        print("⚠️ SICONFI: nenhuma cidade disponível na base para consulta.")
        return

    mapa_siconfi = {
        "receita_total_municipio": "ReceitasCorrentes",
        "receita_propria_numerador": "Impostos",
        "despesas_capital_numerador": "Investimentos"
    }

    variaveis_buscar = [v for v in variaveis if v in mapa_siconfi]
    registros_lote = []
    total_inseridos = 0
    total_cidades = len(cidades)
    base_url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"

    # 2. Roda as chamadas HTTP com o banco FECHADO
    for index, (ibge,) in enumerate(cidades, start=1):
        if index % 50 == 0:
            print(f"🌐 Processando cidade {index}/{total_cidades}: {ibge}...")
            
        params = {
            "an_exercicio": 2023,
            "nr_periodo": 6,
            "co_tipo_demonstrativo": "RREO",
            "no_anexo": "RREO-Anexo 01",
            "id_ente": ibge,
        }
        
        try:
            res = requests.get(base_url, params=params, timeout=10)
            if res.status_code == 200:
                payload = res.json()
                items = payload.get("items", []) if isinstance(payload, dict) else []
                
                for item in items:
                    cod_conta = item.get("cod_conta", "")
                    coluna = item.get("coluna", "")
                    valor = item.get("valor")

                    # Proteção estrita contra JSON sujo do governo
                    if valor is not None and isinstance(coluna, str):
                        if "Até o Bimestre" in coluna or "EMPENHADAS ATÉ O BIMESTRE" in coluna:
                            for var_urbix in variaveis_buscar:
                                if cod_conta == mapa_siconfi[var_urbix]:
                                    registros_lote.append(
                                        ValorIndicador(
                                            codigo_ibge=ibge,
                                            id_indicador=var_urbix,
                                            ano_referencia=2023,
                                            valor=float(valor),
                                            fonte="API SICONFI / RREO-01",
                                        )
                                    )
        except requests.exceptions.RequestException:
            pass # Pula timeout/queda de internet isolada

        time.sleep(0.15) # Rate limit do governo

        # 3. Quando o lote enche, abre uma conexão ultra-rápida só para salvar
        if len(registros_lote) >= 300:
            with SessionLocal() as db_lote:
                db_lote.bulk_save_objects(registros_lote)
                db_lote.commit()
            total_inseridos += len(registros_lote)
            print(f"  💾 Lote SICONFI salvo! ({total_inseridos} registros totais)")
            registros_lote = []

    # 4. Salva o restinho
    if registros_lote:
        with SessionLocal() as db_lote:
            db_lote.bulk_save_objects(registros_lote)
            db_lote.commit()
        total_inseridos += len(registros_lote)

    print(f"✅ API SICONFI: {total_inseridos} dados financeiros inseridos com sucesso!")

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

    inicio_etl = time.time()

    print("=" * 60)
    print("🚀 INICIANDO PIPELINE ETL URBIX HÍBRIDO (STREAMING + APIS)")
    print("=" * 60)

    # 🧹 FAXINA GERAL: Apaga as tabelas sujas do Neon antes de recriar
    # Base.metadata.drop_all(bind=engine)
    
    Base.metadata.create_all(bind=engine)
    print("ℹ️ Semeando metadados de municípios e indicadores antes da carga de fatos.")
    metadata_status = seed_metadata()
    print(f"✅ Metadados semeados: {metadata_status}")

    # ---------------------------------------------------------
    # BLOCO 1: CADASTRO DOS INDICADORES BASE
    # ---------------------------------------------------------
    print("ℹ️ Cadastrando indicadores base no banco de dados...")
    with SessionLocal() as db_base:
        try:
            db_base.execute(text("""
                INSERT INTO indicadores (id, nome, norma_iso, peso, impacto) VALUES 
                ('populacao_total', 'População Total', 'Base', 1.0, 1),
                ('pib_absoluto', 'PIB Absoluto', 'Base', 1.0, 1),
                ('forca_de_trabalho', 'Força de Trabalho', 'Base', 1.0, 1),
                ('total_domicilios', 'Total de Domicílios', 'Base', 1.0, 1),
                ('receita_total_municipio', 'Receita Total do Município', 'Base', 1.0, 1),
                ('receita_propria_numerador', 'Impostos Arrecadados (Numerador)', 'Base', 1.0, 1),
                ('despesas_capital_numerador', 'Investimentos Empenhados (Numerador)', 'Base', 1.0, 1)
                ON CONFLICT (id) DO NOTHING;
            """))
            db_base.commit()
            print("✅ Indicadores base cadastrados com sucesso!")
        except Exception as e:
            db_base.rollback()
            print(f"⚠️ Aviso ao criar indicadores base: {e}")

    print("ℹ️ ETL em modo incremental: mantendo dados históricos existentes e inserindo/atualizando novas cargas.")
    print("\n--- EXTRAINDO DADOS BASE VIA APIS PÚBLICAS ---")
    
    apis_ibge = {
        "populacao_total": {"url": "https://apisidra.ibge.gov.br/values/t/6579/p/2025/n6/all/v/9324?formato=json", "ano": 2025, "fonte": "SIDRA (6579)"},
        "pib_absoluto": {"url": "https://apisidra.ibge.gov.br/values/t/5938/p/2023/n6/all/v/37?formato=json", "ano": 2023, "fonte": "SIDRA (5938)"},
        "forca_de_trabalho": {"url": "https://apisidra.ibge.gov.br/values/t/6580/p/2022/n6/all/v/1641?formato=json", "ano": 2022, "fonte": "SIDRA Censo (6580)"},
        "total_domicilios": {"url": "https://apisidra.ibge.gov.br/values/t/9922/p/2022/n6/all/v/381/c1/6795?formato=json", "ano": 2022, "fonte": "SIDRA Censo (9922)"},
    }

    # ---------------------------------------------------------
    # BLOCO 2: APIS DO IBGE
    # ---------------------------------------------------------
    with SessionLocal() as db_ibge:
        for id_var, config in apis_ibge.items():
            extrair_dado_base_sidra(id_var, config, db_ibge)
        db_ibge.commit()

    # ---------------------------------------------------------
    # BLOCO 3: SICONFI (A função gerencia suas próprias sessões)
    # ---------------------------------------------------------
    '''extrair_receita_siconfi([
        "receita_total_municipio", 
        "receita_propria_numerador", 
        "despesas_capital_numerador"
    ])'''

    print("\n--- EXTRAINDO PLANILHAS LOCAIS COMPLEXAS (STREAMING POR CHUNKS) ---")
    
    # ---------------------------------------------------------
    # BLOCO 4: PLANILHAS LOCAIS
    # ---------------------------------------------------------
    with SessionLocal() as db_local:
        for dominio, indicadores in INDICADORES.items():
            for id_ind, regras in indicadores.items():
                status = str(regras.get("status", "")).strip().lower()
                if any(token in status for token in ("pendente", "incompleto", "nao_baixado", "implementacao")):
                    print(f"⏭️ {id_ind}: ignorado nesta carga (status={status})")
                    continue
                if regras["tipo_calculo"] == "direto":
                    config = regras["variavel_direta"]
                    if config.get("arquivo") not in {"API", "NÃO_BAIXADO"}:
                        extrair_dados_locais(id_ind, config, db_local)
                    else:
                        print(f"⏭️ {id_ind}: fonte externa mantida fora da carga local ({config.get('arquivo')})")
                else:
                    config = regras["numerador"]
                    if config.get("arquivo") not in {"API", "NÃO_BAIXADO"}:
                        extrair_dados_locais(f"{id_ind}_numerador", config, db_local)
                    else:
                        print(f"⏭️ {id_ind}: numerador externo mantido fora da carga local ({config.get('arquivo')})")
        db_local.commit()

    print("\n--- DEDUPLICANDO HISTÓRICO E ATUALIZANDO SNAPSHOT ---")
    
    # ---------------------------------------------------------
    # BLOCO 5: LIMPEZA E SNAPSHOT TOPSIS
    # ---------------------------------------------------------
    with SessionLocal() as db_final:
        deduplicar_historico_mesmo_ano(db_final)
        atualizar_snapshot_latest(db_final)
        db_final.commit()

    fim_etl = time.time() # ⏱️ PARA O CRONÔMETRO AQUI
    minutos_totais = (fim_etl - inicio_etl) / 60

    print(f"\n🎉 ETL FINALIZADO COM SUCESSO!")
    print(f"⏱️ Tempo total de execução: {minutos_totais:.2f} minutos")

if __name__ == "__main__":
    run()