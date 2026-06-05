import cbrkit
import cbrkit.sim.numbers

import config


# =====================
# CBRKIT LINEAR
# =====================

cbrkit_linear = (
    cbrkit.sim.numbers.linear(
        max=20
    )
)


# =====================
# SIMILARIDADE GLOBAL
# =====================

def minha_similaridade_global(
    query,
    case
):

    score_total = 0.0
    peso_total = 0.0

    # =====================
    # PESOS MÉDICOS
    # =====================

    pesos = {

        # físico
        "idade": 0.5,
        "altura": 0.3,
        "peso": 0.3,

        # histórico
        "jogos_lesionado": 1.0,
        "historico_lesoes": 1.5,

        # pouco importante
        "temporada": 0.2,
        "time": 0.1,

        # MAIS IMPORTANTE
        "tipo_lesao": 12.0,
        "local_lesao": 6.0,
        "recorrencia": 4.0,

        # suporte
        "status": 1.0,
        "resultado_final": 1.0
    }

    # =====================
    # NUMÉRICOS
    # =====================

    for campo in config.FEATURES_NUMERIC:

        val_q = query.get(
            campo,
            0
        )

        val_c = case.get(
            campo,
            0
        )

        try:

            sim = cbrkit_linear(

                float(val_q),

                float(val_c)
            )

        except:

            sim = 0.0

        peso = pesos.get(
            campo,
            1.0
        )

        score_total += (
            sim * peso
        )

        peso_total += peso

    # =====================
    # CATEGÓRICOS
    # =====================

    for campo in config.FEATURES_CATEGORICAL:

        val_q = str(

            query.get(
                campo,
                ""
            )

        ).strip().lower()

        val_c = str(

            case.get(
                campo,
                ""
            )

        ).strip().lower()

        # =====================
        # LESÃO (ESPECIAL)
        # =====================

        if campo == "tipo_lesao":

            # igual
            if val_q == val_c:

                sim = 1.0

            # Achilles
            elif (
                "achilles" in val_q
                and
                "achilles" in val_c
            ):

                # tear vs injury
                if (
                    "tear" in val_q
                    and
                    "injury" in val_c
                ) or (
                    "injury" in val_q
                    and
                    "tear" in val_c
                ):

                    sim = 0.20

                else:

                    sim = 0.50

            # Knee
            elif (
                "knee" in val_q
                and
                "knee" in val_c
            ):

                sim = 0.40

            # Hamstring
            elif (
                "hamstring" in val_q
                and
                "hamstring" in val_c
            ):

                sim = 0.50

            # Calf
            elif (
                "calf" in val_q
                and
                "calf" in val_c
            ):

                sim = 0.50

            else:

                sim = 0.0

        # =====================
        # OUTROS CAMPOS
        # =====================

        else:

            sim = (
                1.0
                if val_q == val_c
                else 0.0
            )

        peso = pesos.get(
            campo,
            1.0
        )

        score_total += (
            sim * peso
        )

        peso_total += peso

    # =====================
    # TEXTO
    # =====================

    for campo in config.FEATURES_TEXT:

        set_q = set(

            str(

                query.get(
                    campo,
                    ""
                )

            )
            .lower()
            .split()
        )

        set_c = set(

            str(

                case.get(
                    campo,
                    ""
                )

            )
            .lower()
            .split()
        )

        if set_q or set_c:

            sim = len(

                set_q.intersection(
                    set_c
                )

            ) / float(

                len(
                    set_q.union(
                        set_c
                    )
                )
            )

        else:

            sim = 0.0

        peso = pesos.get(
            campo,
            1.0
        )

        score_total += (
            sim * peso
        )

        peso_total += peso

    return (

        score_total /
        peso_total

        if peso_total > 0

        else 0.0
    )


# =====================
# RETRIEVE CASES
# =====================

def retrieve_cases(
    query_data,
    df,
    k=3
):

    casebase = df.to_dict(
        orient="index"
    )

    ranking = []

    for _, case_data in casebase.items():

        # evitar comparar consigo mesmo
        if (
            case_data.get(
                "jogador"
            )
            ==
            query_data.get(
                "jogador"
            )
        ):
            continue

        score = (
            minha_similaridade_global(
                query_data,
                case_data
            )
        )

        ranking.append(
            (
                case_data,
                score
            )
        )

    ranking.sort(

        key=lambda x:
        x[1],

        reverse=True
    )

    print(
        "\n🧠 CBRKIT NBA ATIVO\n"
    )

    return ranking[:k]