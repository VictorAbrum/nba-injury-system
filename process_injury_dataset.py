import pandas as pd
import numpy as np

from medical_mapper import (
    normalize_injury,
    get_body_region,
    get_injury_family
)


# ==========================
# CONFIG
# ==========================

INPUT_FILE = (
    "data/injury_history/"
    "historico_lesoes_nba.csv"
)

OUTPUT_FILE = (
    "data/injury_history/"
    "historico_lesoes_gold.csv"
)


# ==========================
# TERMOS
# ==========================

RETURN_TERMS = [

    "returned to lineup",
    "returned",
    "activated from il",
    "activated",
    "cleared to play",
    "available to play"
]

IGNORE_TERMS = [

    "trade",
    "signed",
    "waived",
    "released",
    "contract",
    "draft",
    "option",
    "g league",
    "assigned",
    "recalled",
    "rest"
]


# ==========================
# SCORE GRAVIDADE
# ==========================

def get_gravity(texto):

    texto = str(
        texto
    ).lower()

    grave = [

        "surgery",
        "repair",
        "rupture",
        "torn",
        "tear",
        "acl",
        "out for season"
    ]

    moderada = [

        "fracture",
        "sprain",
        "strain",
        "out indefinitely",
        "injury"
    ]

    leve = [

        "dtd",
        "day-to-day",
        "sore",
        "tightness",
        "questionable"
    ]

    if any(
        x in texto
        for x in grave
    ):
        return (
            "grave",
            3
        )

    if any(
        x in texto
        for x in moderada
    ):
        return (
            "moderada",
            2
        )

    if any(
        x in texto
        for x in leve
    ):
        return (
            "leve",
            1
        )

    return (
        "leve",
        1
    )


# ==========================
# RETORNO
# ==========================

def is_return_event(texto):

    texto = str(
        texto
    ).lower()

    return any(

        termo in texto

        for termo in
        RETURN_TERMS
    )


# ==========================
# LOAD
# ==========================

print(
    "\n📥 Carregando CSV..."
)

df = pd.read_csv(
    INPUT_FILE
)

print(
    f"📊 Registros:"
    f" {len(df)}"
)

df["data"] = pd.to_datetime(

    df["data"],

    errors="coerce"
)

df = df.dropna(
    subset=["data"]
)

df = df.sort_values(

    ["jogador", "data"]
)

df = df.drop_duplicates()


# ==========================
# PROCESSAMENTO
# ==========================

registros = []

for jogador in df["jogador"].dropna().unique():

    jogador_df = df[

        df["jogador"]
        ==
        jogador

    ].copy()

    jogador_df = jogador_df.sort_values(
        "data"
    )

    historico = []

    for i in range(
        len(jogador_df)
    ):

        row = jogador_df.iloc[i]

        texto_original = str(
            row["lesao"]
        )

        texto_lower = (
            texto_original
            .lower()
        )

        # ignora lixo
        if any(

            termo in texto_lower

            for termo in
            IGNORE_TERMS
        ):
            continue

        # ignora evento de retorno
        if is_return_event(
            texto_original
        ):
            continue

        data_lesao = row[
            "data"
        ]

        tipo_lesao = (
            normalize_injury(
                texto_original
            )
        )

        grupo = (
            get_body_region(
                tipo_lesao
            )
        )

        familia = (
            get_injury_family(
                tipo_lesao
            )
        )

        gravidade, score_grav = (

            get_gravity(
                texto_original
            )
        )

        # ======================
        # RETORNO
        # ======================

        data_retorno = None
        dias_fora = None

        for j in range(
            i + 1,
            len(jogador_df)
        ):

            prox = jogador_df.iloc[j]

            prox_texto = str(
                prox["lesao"]
            )

            prox_data = prox[
                "data"
            ]

            diferenca = (

                prox_data
                -
                data_lesao

            ).days

            # muito longe = nova lesão
            if diferenca > 180:
                break

            # retorno oficial
            if is_return_event(
                prox_texto
            ):

                if diferenca >= 0:

                    data_retorno = (
                        prox_data
                    )

                    dias_fora = (
                        diferenca
                    )

                break


        # ======================
        # VALIDAÇÃO MÉDICA
        # ======================

        tipo_lower = (
            tipo_lesao.lower()
        )

        if dias_fora is not None:

            # Achilles Tear
            if (
                "achilles tear"
                in tipo_lower
                and dias_fora < 45
            ):

                dias_fora = None
                data_retorno = None

            # ACL
            elif (
                "acl" in texto_lower
                and dias_fora < 90
            ):

                dias_fora = None
                data_retorno = None

            # Fratura
            elif (
                "fracture" in texto_lower
                and dias_fora < 14
            ):

                dias_fora = None
                data_retorno = None
                
        # ======================
        # RECORRÊNCIA
        # ======================

        recorrencia = (

            "sim"

            if tipo_lesao
            in historico

            else "nao"
        )

        score_rec = (

            2
            if recorrencia
            == "sim"
            else 1
        )

        historico.append(
            tipo_lesao
        )

        risco = min(

            score_grav
            +
            score_rec,

            5
        )

        registros.append({

            "jogador":
            jogador,

            "time":
            row.get(
                "time",
                None
            ),

            "data_lesao":
            data_lesao,

            "data_retorno":
            data_retorno,

            "dias_fora":
            dias_fora,

            "tipo_lesao_original":
            texto_original,

            "tipo_lesao":
            tipo_lesao,

            "grupo_corporal":
            grupo,

            "familia_lesao":
            familia,

            "gravidade":
            gravidade,

            "recorrencia":
            recorrencia,

            "gravidade_score":
            score_grav,

            "recorrencia_score":
            score_rec,

            "risco_score":
            risco
        })


# ==========================
# FINAL
# ==========================

final_df = pd.DataFrame(
    registros
)

final_df = (

    final_df

    .drop_duplicates()

    .sort_values(

        [
            "jogador",
            "data_lesao"
        ]
    )
)

print(
    f"\n✅ Casos válidos:"
    f" {len(final_df)}"
)

print(
    "\n📌 Top lesões:"
)

print(

    final_df[
        "tipo_lesao"
    ]
    .value_counts()
    .head(20)
)

print(
    "\n📌 Dias fora médios:"
)

print(

    final_df.groupby(
        "tipo_lesao"
    )["dias_fora"]

    .mean()

    .sort_values(
        ascending=False
    )

    .head(15)
)

final_df.to_csv(

    OUTPUT_FILE,

    index=False,

    encoding="utf-8-sig"
)

print(
    "\n✅ GOLD CSV SALVO:"
)

print(
    OUTPUT_FILE
)