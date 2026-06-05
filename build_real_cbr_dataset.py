import pandas as pd
import sqlite3


# ==========================
# CONFIG
# ==========================

INPUT_FILE = (
    "data/injury_history/"
    "historico_lesoes_gold.csv"
)

OUTPUT_FILE = (
    "data/"
    "cbr_nba_cases_real.csv"
)

DB_PATH = (
    "instance/nba.db"
)


# ==========================
# CARREGAR DATASET
# ==========================

df = pd.read_csv(
    INPUT_FILE
)

print(
    f"\n📊 Registros carregados:"
    f" {len(df)}"
)


# ==========================
# PEGAR JOGADORES DO BANCO
# ==========================

conn = sqlite3.connect(
    DB_PATH
)

jogadores = pd.read_sql(

    """
    SELECT
        jogador,
        idade,
        altura,
        peso,
        time,
        temporada,
        jogos_temporada
    FROM jogador
    """,

    conn
)

conn.close()

print(
    f"🏀 Jogadores banco:"
    f" {len(jogadores)}"
)


# ==========================
# MERGE
# ==========================

df = df.merge(

    jogadores,

    on="jogador",

    how="left",

    suffixes=(
        "",
        "_jogador"
    )
)


# ==========================
# CORRIGIR TIME
# ==========================

if "time" not in df.columns:

    if "time_jogador" in df.columns:

        df["time"] = df[
            "time_jogador"
        ]

    elif "team" in df.columns:

        df["time"] = df[
            "team"
        ]

    else:

        df["time"] = (
            "Unknown"
        )


# ==========================
# LIMPEZA
# ==========================

df = df.dropna(

    subset=[
        "tipo_lesao"
    ]
)

# ==========================
# FILL MÉDICO
# ==========================

def preencher_dias(row):

    dias = row["dias_fora"]

    if pd.notna(dias):
        return dias

    lesao = str(
        row["tipo_lesao"]
    ).lower()

    texto = str(
        row.get(
            "tipo_lesao_original",
            ""
        )
    ).lower()

    # Achilles Tear
    if "achilles tear" in lesao:
        return 240

    # ACL
    if "acl" in texto:
        return 240

    # fracture
    if "fracture" in texto:
        return 45

    # surgery
    if (
        "surgery" in texto
        or
        "repair" in texto
    ):
        return 60

    # out indefinitely
    if (
        "out indefinitely"
        in texto
    ):
        return 30

    # DTD
    if "dtd" in texto:
        return 3

    # default
    return 7


df["dias_fora"] = df.apply(
    preencher_dias,
    axis=1
)

# evitar negativos
df = df[
    df["dias_fora"] >= 0
]

# limitar absurdos
df.loc[

    df["dias_fora"] > 365,

    "dias_fora"

] = 365

print(
    f"✅ Casos válidos:"
    f" {len(df)}"
)

# ==========================
# CBR FEATURES
# ==========================

df["status"] = (
    "out"
)

df["local_lesao"] = (

    df[
        "grupo_corporal"
    ]

    .replace({

        "lower_body":
        "Perna",

        "upper_body":
        "Ombro",

        "general":
        "Geral"
    })
)

# histórico incremental
df["historico_lesoes"] = (

    df.groupby(
        "jogador"
    )

    .cumcount()
)

df["recorrencia"] = (

    df[
        "recorrencia"
    ]

    .fillna(
        "nao"
    )
)

df["resultado_final"] = (
    "retornou_bem"
)

df["dias_retorno_real"] = (
    df["dias_fora"]
)

df["retorno_estimado"] = (
    df["dias_fora"]
)

df["jogos_lesionado"] = (
    df["dias_fora"]
)

# padronizar temporada
df["temporada"] = (
    2025
)


# ==========================
# PREENCHER NULOS
# ==========================

df["idade"] = (

    df["idade"]

    .fillna(26)
)

df["altura"] = (

    df["altura"]

    .fillna(1.98)
)

df["peso"] = (

    df["peso"]

    .fillna(95)
)

df["time"] = (

    df["time"]

    .fillna(
        "Unknown"
    )
)


# ==========================
# COLUNAS FINAIS
# ==========================

colunas = [

    "jogador",

    "idade",
    "altura",
    "peso",
    "time",

    "tipo_lesao",
    "local_lesao",

    "status",
    "jogos_lesionado",

    "historico_lesoes",
    "temporada",

    "dias_retorno_real",
    "retorno_estimado",

    "recorrencia",
    "resultado_final"
]

df_final = df[
    colunas
].copy()


# ==========================
# SALVAR
# ==========================

df_final.to_csv(

    OUTPUT_FILE,

    index=False
)

print(
    f"\n✅ DATASET CBR REAL SALVO:"
)

print(
    OUTPUT_FILE
)

print(
    f"\n📊 Casos finais:"
    f" {len(df_final)}"
)

print(
    "\n📌 Top Lesões:"
)

print(

    df_final[
        "tipo_lesao"
    ]

    .value_counts()

    .head(20)
)
