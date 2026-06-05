def adapt(retrieved_cases, query):

    best_cases = [

        c[0]

        for c in retrieved_cases
    ]

    if not best_cases:

        return None

    # =====================
    # MÉDIAS
    # =====================

    media_retorno = round(

        sum(

            float(
                c["dias_retorno_real"]
            )

            for c in best_cases

        ) / len(best_cases)

    )

    media_jogos = round(

        sum(

            float(
                c["jogos_lesionado"]
            )

            for c in best_cases

        ) / len(best_cases),

        1
    )

    # =====================
    # RISCO
    # =====================

    historico = int(

        query.get(
            "historico_lesoes",
            0
        )
    )

    recorrencia = str(

        query.get(
            "recorrencia",
            "nao"
        )

    ).lower()

    if historico >= 4:

        risco = "alto"

    elif historico >= 2:

        risco = "medio"

    else:

        risco = "baixo"

    if recorrencia == "sim":

        if risco == "baixo":

            risco = "medio"

        elif risco == "medio":

            risco = "alto"

    # =====================
    # RECOMENDAÇÃO
    # =====================

    tipo = str(

        query.get(
            "tipo_lesao",
            ""
        )

    ).lower()

    local = str(

        query.get(
            "local_lesao",
            ""
        )

    ).lower()

    recomendacao = (
        "Monitoramento médico padrão."
    )

    if "hamstring" in tipo:

        recomendacao = (
            "Retorno gradual e "
            "monitoramento muscular."
        )

    elif "knee" in tipo:

        recomendacao = (
            "Evitar sobrecarga "
            "e monitorar impacto."
        )

    elif "ankle" in tipo:

        recomendacao = (
            "Reforço de estabilidade "
            "e prevenção de recaída."
        )

    elif "joelho" in local:

        recomendacao = (
            "Acompanhamento "
            "fisioterapêutico intensivo."
        )

    # =====================
    # RESULTADO
    # =====================

    return {

        "dias_estimados":
            media_retorno,

        "media_jogos":
            media_jogos,

        "risco":
            risco,

        "recomendacao":
            recomendacao,

        "casos_similares":
            retrieved_cases
    }