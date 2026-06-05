import sqlite3
import pandas as pd


# ==========================
# CONFIG
# ==========================

DB_PATH = (
    "instance/nba.db"
)

INPUT_FILE = (
    "data/injury_history/"
    "historico_lesoes_gold.csv"
)

OUTPUT_FILE = (
    "data/injury_history/"
    "dataset_ml.csv"
)


# ==========================
# BANCO NBA
# ==========================

conn = sqlite3.connect(
    DB_PATH
)

jogadores_db = pd.read_sql(

    """
    SELECT
        jogador,
        idade,
        altura,
        peso,
        temporada,
        jogos_temporada,
        time
    FROM jogador
    """,

    conn
)

conn.close()


# ==========================
# DATASET LESÕES
# ==========================

df = pd.read_csv(
    INPUT_FILE
)

df["data_lesao"] = pd.to_datetime(
    df["data_lesao"]
)

df = df.sort_values(

    ["jogador", "data_lesao"]
)


# ==========================
# MERGE
# ==========================

df = df.merge(

    jogadores_db,

    on="jogador",

    how="left",

    suffixes=("", "_db")
)


# ==========================
# HISTÓRICO JOGADOR
# ==========================

historico_lesoes = []
dias_totais = []

for jogador in df["jogador"].unique():

    jogador_df = df[
        df["jogador"]
        ==
        jogador
    ]

    total_lesoes = 0
    total_dias = 0

    for idx in jogador_df.index:

        historico_lesoes.append(
            total_lesoes
        )

        dias_totais.append(
            total_dias
        )

        total_lesoes += 1

        dias = df.loc[
            idx,
            "dias_fora"
        ]

        if pd.notna(dias):

            total_dias += dias


df[
    "historico_lesoes"
] = historico_lesoes

df[
    "dias_totais_lesionado"
] = dias_totais


# ==========================
# LIMPEZA ML
# ==========================

# apenas casos com retorno real
df = df.dropna(
    subset=["dias_fora"]
)

# remove lesão sem nome
df = df.dropna(
    subset=["tipo_lesao"]
)

# dias válidos
df = df[
    (df["dias_fora"] >= 0)
    &
    (df["dias_fora"] <= 365)
]

# preencher físicos faltantes
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

# ==========================
# SALVAR
# ==========================

df.to_csv(

    OUTPUT_FILE,

    index=False
)

print(
    "\n✅ DATASET ML SALVO"
)

print(
    f"\n📊 Registros:"
    f" {len(df)}"
)

print(
    "\n📌 Colunas:"
)

print(
    df.columns
)

print(
    "\n📌 Exemplo:"
)

print(
    df.head()
)