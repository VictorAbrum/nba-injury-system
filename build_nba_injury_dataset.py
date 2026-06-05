import sqlite3
import pandas as pd
import time

from nba_injury_history_scraper import (
    scrape_player_history
)


# =====================
# CONFIG
# =====================

DB_PATH = (
    "instance/nba.db"
)

OUTPUT_FOLDER = (
    "data/injury_history/"
)

OUTPUT_FILE = (

    OUTPUT_FOLDER
    +
    "historico_lesoes_nba.csv"
)


# =====================
# PEGAR JOGADORES
# =====================

conn = sqlite3.connect(
    DB_PATH
)

query = """

SELECT jogador
FROM jogador

ORDER BY jogador

"""

jogadores_df = pd.read_sql(

    query,

    conn
)

conn.close()

jogadores = jogadores_df[
    "jogador"
].dropna().unique()

print(
    f"\n🏀 Jogadores encontrados:"
    f" {len(jogadores)}\n"
)

todos_dados = []


# =====================
# LOOP JOGADORES
# =====================

for i, jogador in enumerate(

    jogadores,

    start=1
):

    print(
        f"\n[{i}/{len(jogadores)}]"
        f" {jogador}"
    )

    try:

        df = scrape_player_history(
            jogador
        )

        if not df.empty:

            todos_dados.append(
                df
            )

            print(
                f"✅ {len(df)} registros"
            )

        else:

            print(
                "⚠️ sem histórico"
            )

    except Exception as e:

        print(
            f"❌ erro:"
            f" {e}"
        )

    # não bombardear site
    time.sleep(2)


# =====================
# SALVAR CSV FINAL
# =====================

if todos_dados:

    final_df = pd.concat(

        todos_dados,

        ignore_index=True
    )

    final_df.to_csv(

        OUTPUT_FILE,

        index=False
    )

    print(
        f"\n✅ Dataset salvo:"
        f" {OUTPUT_FILE}"
    )

    print(
        f"📊 Registros:"
        f" {len(final_df)}"
    )

else:

    print(
        "\n❌ Nenhum dado coletado"
    )