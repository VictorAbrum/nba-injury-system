import sqlite3
import pandas as pd


# ==========================
# CONFIG
# ==========================

DB_PATH = "instance/nba.db"

CSV_PATH = (
    "data/injury_history/"
    "historico_lesoes_gold.csv"
)


# ==========================
# CSV
# ==========================

df = pd.read_csv(
    CSV_PATH
)

print(
    f"\n📊 Lesões carregadas:"
    f" {len(df)}"
)

print(
    "\n📌 Colunas CSV:"
)

print(
    df.columns.tolist()
)


# ==========================
# BANCO
# ==========================

conn = sqlite3.connect(
    DB_PATH
)

cursor = conn.cursor()


# ==========================
# IMPORTAÇÃO
# ==========================

inseridos = 0
erros = 0

for _, row in df.iterrows():

    try:

        dias_fora = row.get(
            "dias_fora",
            0
        )

        dias_fora = (

            int(dias_fora)

            if pd.notna(
                dias_fora
            )

            else 0
        )

        data_lesao = row.get(
            "data_lesao",
            None
        )

        if pd.isna(
            data_lesao
        ):
            data_lesao = None

        data_retorno = row.get(
            "data_retorno",
            None
        )

        if pd.isna(
            data_retorno
        ):
            data_retorno = None

        cursor.execute(
            """
            INSERT INTO lesao (

                jogador,
                tipo_lesao,
                local_lesao,

                status,
                jogos_lesionado,

                data_lesao,
                retorno_previsto,

                observacoes

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,

            (

                row.get(
                    "jogador"
                ),

                row.get(
                    "tipo_lesao"
                ),

                row.get(
                    "grupo_corporal"
                ),

                "historico",

                dias_fora,

                data_lesao,

                data_retorno,

                row.get(
                    "tipo_lesao_original",
                    ""
                )
            )
        )

        inseridos += 1

    except Exception as e:

        erros += 1

        print(
            f"\n❌ ERRO:"
            f" {row.get('jogador')}"
        )

        print(e)


conn.commit()
conn.close()


# ==========================
# RESULTADO
# ==========================

print(
    f"\n✅ Inseridos:"
    f" {inseridos}"
)

print(
    f"❌ Erros:"
    f" {erros}"
)