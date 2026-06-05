from playwright.sync_api import sync_playwright
import pandas as pd
import sqlite3
import time


# =====================
# SCRAPER HISTÓRICO NBA
# =====================

def scrape_player_history(nome):

    rows = []
    vistos = set()

    with sync_playwright() as p:

        browser = p.chromium.connect_over_cdp(
            "http://localhost:9222"
        )

        context = browser.contexts[0]
        page = context.pages[0]

        print(
            f"\n🔎 Buscando {nome}\n"
        )

        page.goto(
            "https://www.prosportstransactions.com/"
            "basketball/Search/Search.php"
        )

        time.sleep(2)

        try:

            # =====================
            # LIMPAR PLAYER
            # =====================

            page.locator(
                'input[name="Player"]'
            ).fill("")

            page.locator(
                'input[name="Player"]'
            ).fill(nome)

            print(
                "✅ jogador preenchido"
            )

            # =====================
            # DESMARCAR CHECKBOXES
            # =====================

            checkboxes = page.locator(
                'input[type="checkbox"]'
            )

            total = checkboxes.count()

            for i in range(total):

                try:

                    if checkboxes.nth(i).is_checked():

                        checkboxes.nth(i).uncheck()

                except:
                    pass

            # =====================
            # MARCAR LESÃO
            # =====================

            labels = page.locator(
                "label"
            )

            marcou = False

            for i in range(
                labels.count()
            ):

                texto = labels.nth(
                    i
                ).inner_text()

                if (
                    "Missed games due to injury"
                    in texto
                ):

                    labels.nth(
                        i
                    ).click()

                    marcou = True

                    print(
                        "✅ checkbox lesão marcada"
                    )

                    break

            if not marcou:

                print(
                    "⚠️ fallback checkbox"
                )

                checkboxes.nth(
                    3
                ).check()

            # =====================
            # SEARCH
            # =====================

            page.locator(
                'input[value="Search"]'
            ).click()

            print(
                "\n⏳ esperando resultados..."
            )

            time.sleep(4)

            pagina = 1

            while True:

                print(
                    f"\n📄 Página {pagina}"
                )

                trs = page.locator(
                    "tr"
                ).all()

                adicionadas = 0

                for tr in trs:

                    tds = tr.locator(
                        "td"
                    )

                    if tds.count() < 5:
                        continue

                    data = tds.nth(
                        0
                    ).inner_text().strip()

                    time_nba = tds.nth(
                        1
                    ).inner_text().strip()

                    relinquished = tds.nth(
                        3
                    ).inner_text().strip()

                    lesao = tds.nth(
                        4
                    ).inner_text().strip()

                    # ignora header
                    if (
                        data == "Date"
                        or data == ""
                    ):
                        continue

                    # ignora transações
                    lixo = [

                        "draft",
                        "contract",
                        "trade",
                        "signed",
                        "option",
                        "extension"
                    ]

                    if any(

                        palavra in
                        lesao.lower()

                        for palavra in lixo
                    ):

                        continue

                    chave = (

                        data,
                        lesao,
                        relinquished
                    )

                    if chave in vistos:
                        continue

                    vistos.add(
                        chave
                    )

                    rows.append({

                        "jogador":
                        nome,

                        "data":
                        data,

                        "time":
                        time_nba,

                        "relinquished":
                        relinquished,

                        "lesao":
                        lesao
                    })

                    adicionadas += 1

                print(
                    f"✅ +{adicionadas} lesões"
                )

                # =====================
                # NEXT PAGE
                # =====================

                try:

                    next_btn = page.locator(
                        'a:has-text("Next")'
                    )

                    if (
                        next_btn.count()
                        == 0
                    ):

                        print(
                            "🏁 última página"
                        )

                        break

                    print(
                        "➡️ próxima página"
                    )

                    next_btn.first.click()

                    time.sleep(3)

                    pagina += 1

                except Exception:

                    print(
                        "🏁 fim"
                    )

                    break

        except Exception as e:

            print(
                f"\n❌ erro {nome}:",
                e
            )

    print(
        f"🔥 TOTAL {nome}: "
        f"{len(rows)} lesões\n"
    )

    return pd.DataFrame(
        rows
    )


# =====================
# MAIN
# =====================

if __name__ == "__main__":

    print(
        "\n🏀 INICIANDO SCRAPER NBA\n"
    )

    conn = sqlite3.connect(
        "instance/nba.db"
    )

    jogadores = pd.read_sql(

        """
        SELECT jogador
        FROM jogador
        """,

        conn
    )

    conn.close()

    jogadores = (

        jogadores[
            "jogador"
        ]

        .dropna()

        .unique()

        .tolist()
    )

    print(
        f"👥 Jogadores: {len(jogadores)}"
    )

    todos = []

    for i, jogador in enumerate(

        jogadores,
        start=1
    ):

        print(
            f"\n[{i}/{len(jogadores)}]"
        )

        try:

            df = scrape_player_history(
                jogador
            )

            if not df.empty:

                todos.append(
                    df
                )

        except Exception as e:

            print(
                f"❌ erro {jogador}:",
                e
            )

    if todos:

        df_final = pd.concat(
            todos,
            ignore_index=True
        )

        df_final = (

            df_final
            .drop_duplicates()
        )

        caminho = (
            "data/injury_history/"
            "historico_lesoes_nba.csv"
        )

        df_final.to_csv(

            caminho,

            index=False,

            encoding="utf-8-sig"
        )

        print(
            "\n✅ CSV SALVO:"
        )

        print(
            caminho
        )

        print(
            f"\n📊 Total registros:"
            f" {len(df_final)}"
        )

    else:

        print(
            "\n❌ Nenhum dado baixado"
        )