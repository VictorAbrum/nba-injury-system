from flask import (

    Flask,

    render_template,

    request,

    redirect,

    url_for,

    jsonify
)

from database.models import (
    bd,
    Jogador,
    Lesao
)

import pandas as pd
import os
import joblib
import numpy as np

from nba_roster_scraper import (
    TEAM_LOGOS
)

from cbr_nba_engine import (
    retrieve_cases
)

from nba_adaptation import (
    adapt
)

from medical_mapper import (

    normalize_injury,

    get_body_region,

    get_injury_family
)

app = Flask(__name__)

# banco
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///nba.db"

app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False

bd.init_app(app)

with app.app_context():

    bd.create_all()

# ==========================
# MODELO ML
# ==========================

modelo_recuperacao = joblib.load(

    "modelos/"
    "recovery_model_v3.pkl"
)

# ==========================
# PREVER RECUPERAÇÃO
# ==========================

def prever_recuperacao_ml(

    jogador_obj,

    tipo_lesao,

    gravidade="moderada",

    recorrencia="nao"
):

    try:

        gravidade_score = {

            "leve": 1,
            "moderada": 2,
            "grave": 3

        }.get(
            gravidade,
            2
        )

        recorrencia_score = (

            1
            if recorrencia == "sim"
            else 0
        )

        risco_score = (

            gravidade_score
            +
            recorrencia_score
        )

        # features médicas
        texto = tipo_lesao.lower()

        entrada = pd.DataFrame([{

            "tipo_lesao":
            tipo_lesao,

            "grupo_corporal":
            "lower_body",

            "gravidade":
            gravidade,

            "gravidade_score":
            gravidade_score,

            "recorrencia_score":
            recorrencia_score,

            "risco_score":
            risco_score,

            "idade":
            jogador_obj.idade,

            "altura":
            jogador_obj.altura,

            "peso":
            jogador_obj.peso,

            "temporada":
            2025,

            "jogos_temporada":
            jogador_obj.jogos_temporada,

            "historico_lesoes":
            3,

            "dias_totais_lesionado":
            60,

            # features médicas
            "teve_cirurgia":
            int(
                "surgery"
                in texto
            ),

            "teve_ruptura":
            int(
                "rupture"
                in texto
            ),

            "teve_fratura":
            int(
                "fracture"
                in texto
            ),

            "teve_torn":
            int(
                "tear"
                in texto
                or
                "torn"
                in texto
            ),

            "teve_strain":
            int(
                "strain"
                in texto
            ),

            "teve_sprain":
            int(
                "sprain"
                in texto
            ),

            "out_for_season":
            int(
                "out for season"
                in texto
            ),

            "out_indefinitely":
            int(
                "out indefinitely"
                in texto
            ),

            "dtd":
            int(
                "dtd"
                in texto
            ),

            "questionable":
            0,

            "probable":
            0,

            "soreness":
            int(
                "soreness"
                in texto
            ),

            "medical_risk_score":
            0
        }])

        pred_log = modelo_recuperacao.predict(
            entrada
        )[0]

        dias = round(

            np.expm1(
                pred_log
            )
        )

        dias = max(
            dias,
            1
        )

        return dias

    except Exception as e:

        print(
            "\n❌ ERRO ML:",
            e
        )

        return None

# =========================
# HOME
# =========================
@app.route("/")
def home():

    # =====================
    # MÉTRICAS PRINCIPAIS
    # =====================

    total_lesoes = (
        Lesao.query.count()
    )

    jogadores_out = (
        Lesao.query.filter_by(
            status="out"
        ).count()
    )

    jogadores_questionavel = (
        Lesao.query.filter_by(
            status="questionavel"
        ).count()
    )

    lesoes = (
        Lesao.query.all()
    )

    # jogos perdidos
    total_jogos_perdidos = sum(

        lesao.jogos_lesionado or 0

        for lesao in lesoes
    )


    # =====================
    # GRÁFICOS
    # =====================

    status_count = {

        "out": 0,

        "questionavel": 0,

        "ativo": 0
    }

    tipos_lesao = {}

    for lesao in lesoes:

        # status
        if lesao.status in status_count:

            status_count[
                lesao.status
            ] += 1

        # tipo lesão
        tipo = lesao.tipo_lesao

        if tipo:

            tipos_lesao[tipo] = (

                tipos_lesao.get(
                    tipo,
                    0
                )

                + 1
            )


    # =====================
    # TOP 10 LESÕES
    # =====================

    tipos_ordenados = sorted(

        tipos_lesao.items(),

        key=lambda x: x[1],

        reverse=True

    )[:10]


    # =====================
    # ÚLTIMAS LESÕES
    # =====================

    ultimas_lesoes = (

        Lesao.query

        .order_by(
            Lesao.id.desc()
        )

        .limit(5)

        .all()
    )


    # =====================
    # TOP LESIONADOS
    # =====================

    top_lesionados = {}

    for lesao in lesoes:

        jogador = (
            lesao.jogador
        )

        top_lesionados[
            jogador
        ] = (

            top_lesionados.get(
                jogador,
                0
            )

            + 1
        )

    top_lesionados = sorted(

        top_lesionados.items(),

        key=lambda x: x[1],

        reverse=True

    )[:5]


    # =====================
    # TIMES MAIS LESIONADOS
    # =====================

    times_lesoes = {}

    for lesao in lesoes:

        jogador_obj = (

            Jogador.query

            .filter_by(
                jogador=
                lesao.jogador
            )

            .first()
        )

        if jogador_obj:

            time = (
                jogador_obj.time
            )

            times_lesoes[
                time
            ] = (

                times_lesoes.get(
                    time,
                    0
                )

                + 1
            )

    top_times = sorted(

        times_lesoes.items(),

        key=lambda x: x[1],

        reverse=True

    )[:5]


    # =====================
    # INSIGHTS
    # =====================

    tipo_mais_comum = (

        max(

            tipos_lesao,

            key=
            tipos_lesao.get

        )

        if tipos_lesao

        else "N/A"
    )

    media_lesoes = round(

        total_lesoes /

        max(

            len(

                set(

                    x.jogador

                    for x in lesoes
                )
            ),

            1
        ),

        1
    )

    total_jogadores = (

        Jogador.query.count()
    )


    # =====================
    # RENDER
    # =====================

    return render_template(

        "home.html",

        # KPIs
        total_lesoes=
        total_lesoes,

        jogadores_out=
        jogadores_out,

        jogadores_questionavel=
        jogadores_questionavel,

        total_jogos_perdidos=
        total_jogos_perdidos,

        total_jogadores=
        total_jogadores,

        media_lesoes=
        media_lesoes,

        tipo_mais_comum=
        tipo_mais_comum,

        # gráficos
        status_count=
        status_count,

        tipos_labels=
        [x[0] for x in tipos_ordenados],

        tipos_values=
        [x[1] for x in tipos_ordenados],

        # dashboard
        ultimas_lesoes=
        ultimas_lesoes,

        top_lesionados=
        top_lesionados,

        top_times=
        top_times
    )

# =========================
# ADICIONAR LESÃO
# =========================
@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():

    from flask import request, redirect

    if request.method == "POST":

        nova_lesao = Lesao(

            jogador=request.form["jogador"],
            tipo_lesao=request.form["tipo_lesao"],
            local_lesao=request.form["local_lesao"],

            status=request.form["status"],

            jogos_lesionado=request.form["jogos_lesionado"],

            data_lesao=request.form["data_lesao"],

            retorno_previsto=request.form["retorno_previsto"],

            observacoes=request.form["observacoes"]
        )

        bd.session.add(nova_lesao)
        bd.session.commit()

        return redirect("/")

    return render_template("adicionar.html")

# =========================
# PERFIL JOGADOR
# =========================
@app.route("/jogador/<nome>")
def jogador(nome):

    jogador = Jogador.query.filter_by(
        jogador=nome
    ).first()

    if not jogador:

        return redirect(
            url_for(
                "jogadores"
            )
        )

    lesoes = Lesao.query.filter_by(
        jogador=nome
    ).all()

    # ordenar mais recente
    lesoes = sorted(

        lesoes,

        key=lambda x:
        x.data_lesao or "",

        reverse=True
    )

    total_lesoes = len(
        lesoes
    )

    total_jogos_perdidos = sum(

        lesao.jogos_lesionado or 0

        for lesao in lesoes
    )

    # =====================
    # STATUS
    # =====================

    status_atual = "ativo"

    if lesoes:

        ultima = lesoes[0]

        status_atual = (
            ultima.status
            or "ativo"
        )

    # =====================
    # RISCO
    # =====================

    if total_lesoes == 0:

        risco = "baixo"
        risco_cor = "success"
        risco_percentual = 15

    elif total_lesoes <= 2:

        risco = "medio"
        risco_cor = "warning"
        risco_percentual = 50

    else:

        risco = "alto"
        risco_cor = "danger"
        risco_percentual = 85

    # =====================
    # DISPONIBILIDADE
    # =====================

    jogos_temporada = (
        jogador.jogos_temporada
        or 82
    )

    disponibilidade = max(

        0,

        round(

            (
                (
                    jogos_temporada
                    -
                    total_jogos_perdidos
                )

                /
                jogos_temporada
            ) * 100
        )
    )

    percentual_jogos_perdidos = round(

        (
            total_jogos_perdidos
            /
            jogos_temporada
        ) * 100,

        1
    )

    # =====================
    # IA
    # =====================

    cbr_resultado = None
    ml_previsao = None
    estimativa_final = None
    explicacao_ml = []
    lesao_normalizada = None
    aviso_ml = None

    if lesoes:

        ultima_lesao = lesoes[0]

        # =====================
        # NORMALIZAÇÃO
        # =====================

        lesao_normalizada = normalize_injury(

            ultima_lesao.tipo_lesao,

            ultima_lesao.local_lesao
        )

        body_region = get_body_region(
            lesao_normalizada
        )

        body_region_cbr = {

            "lower_body":
            "Perna",

            "upper_body":
            "Ombro",

            "general":
            "Geral"

        }.get(
            body_region,
            "Geral"
        )

        injury_family = get_injury_family(
            lesao_normalizada
        )

        # =====================
        # MAPA CBR
        # =====================

        tipo_cbr = {

            "Achilles Injury":
            "Achilles Injury",

            "Achilles Tear":
            "Achilles Tear",

            "Hamstring Strain":
            "Hamstring Strain",

            "Groin Strain":
            "Groin Strain",

            "Knee Injury":
            "Knee Injury",

            "Ankle Injury":
            "Ankle Injury",

            "Shoulder Injury":
            "Shoulder Injury",

            "Hip Injury":
            "Hip Injury",

            "Back Injury":
            "Back Injury"

        }.get(

            lesao_normalizada,

            lesao_normalizada
        )

        query_case = {

            "idade":
            jogador.idade or 25,

            "altura":
            jogador.altura or 1.90,

            "peso":
            jogador.peso or 90,

            "time":
            (
                jogador.time or ""
            ).replace(
                "Indiana ",
                ""
            ),

            "tipo_lesao":
            tipo_cbr,

            "local_lesao":
            body_region_cbr,

            "status":
            "out",

            "jogos_lesionado":
            max(
                ultima_lesao.jogos_lesionado or 0,
                7
            ),

            "historico_lesoes":
            total_lesoes,

            "temporada":
            2025,

            "recorrencia":

            "sim"
            if total_lesoes > 1
            else "nao",

            "resultado_final":
            "retornou_bem"
        }

        # =====================
        # CBR
        # =====================

        try:

            df_cbr = pd.read_csv(
                "data/cbr_nba_cases_real.csv"
            )

            retrieved = retrieve_cases(

                query_case,

                df_cbr,

                k=3
            )

            print("\n📊 QUERY CBR")
            print(query_case)

            print("\n📊 RETRIEVED")
            print(retrieved)

            if retrieved:

                cbr_resultado = adapt(

                    retrieved,

                    query_case
                )

                print("\n🧠 RESULTADO CBR")
                print(cbr_resultado)

        except Exception as e:

            print(
                "Erro CBR:",
                e
            )

        # =====================
        # MACHINE LEARNING
        # =====================

        try:

            ml_previsao = prever_recuperacao_ml(

                jogador,

                lesao_normalizada,

                gravidade="moderada",

                recorrencia=

                "sim"
                if total_lesoes > 1
                else "nao"
            )

            print(
                f"🧠 ML previsão:"
                f" {ml_previsao} dias"
            )

        except Exception as e:

            print(
                "Erro ML:",
                e
            )

        # =====================
        # MÉDIA FINAL
        # =====================

        try:

            cbr_dias = None

            if cbr_resultado:

                cbr_dias = cbr_resultado.get(
                    "dias_estimados"
                )

            if (
                cbr_dias
                and
                ml_previsao
            ):

                tipo_lower = str(
                    lesao_normalizada
                ).lower()

                lesoes_graves = [

                    "achilles tear",
                    "acl tear",
                    "rupture",
                    "fracture",
                    "torn acl",
                    "torn meniscus"

                ]

                if any(

                    x in tipo_lower

                    for x in
                    lesoes_graves
                ):

                    estimativa_final = round(

                        (
                            float(cbr_dias)
                            * 0.95
                        )

                        +

                        (
                            float(ml_previsao)
                            * 0.05
                        ),

                        1
                    )

                else:

                    estimativa_final = round(

                        (
                            float(cbr_dias)
                            * 0.60
                        )

                        +

                        (
                            float(ml_previsao)
                            * 0.40
                        ),

                        1
                    )

                # ==========================
                # CONFIANÇA ML
                # ==========================

                if (

                    ml_previsao
                    <
                    (
                        cbr_dias * 0.30
                    )

                ):

                    aviso_ml = (
                        "baixa_confianca"
                    )

            elif ml_previsao:

                estimativa_final = round(
                    float(ml_previsao),
                    1
                )

            elif cbr_dias:

                estimativa_final = round(
                    float(cbr_dias),
                    1
                )

            print(
                f"🧠 ESTIMATIVA FINAL:"
                f" {estimativa_final}"
            )

        except Exception as e:

            print(
                "Erro estimativa:",
                e
            )

    return render_template(

        "jogador.html",

        jogador=jogador,
        lesoes=lesoes,

        total_lesoes=
        total_lesoes,

        total_jogos_perdidos=
        total_jogos_perdidos,

        status_atual=
        status_atual,

        risco=
        risco,

        risco_cor=
        risco_cor,

        risco_percentual=
        risco_percentual,

        disponibilidade=
        disponibilidade,

        percentual_jogos_perdidos=
        percentual_jogos_perdidos,

        cbr_resultado=
        cbr_resultado,

        ml_previsao=
        ml_previsao,

        estimativa_final=
        estimativa_final,

        explicacao_ml=
        explicacao_ml,

        lesao_normalizada=
        lesao_normalizada,

        aviso_ml=
        aviso_ml,

        casos_similares=(
            cbr_resultado.get(
                "casos_similares",
                []
            )

            if cbr_resultado

            else []
        ),
    )

# =========================
# UPLOAD CSV
# =========================
@app.route(
    "/upload",
    methods=["GET", "POST"]
)
def upload():

    from flask import (
        request,
        redirect
    )

    if request.method == "POST":

        arquivo = request.files.get(
            "arquivo"
        )

        if arquivo:

            caminho = os.path.join(

                "data",

                arquivo.filename
            )

            arquivo.save(caminho)

            df = pd.read_csv(
                caminho
            )

            # ======================
            # LIMPA BANCO ANTIGO
            # ======================

            Lesao.query.delete()

            bd.session.commit()

            # ======================
            # IMPORTA CSV NOVO
            # ======================

            for _, row in df.iterrows():

                nova_lesao = Lesao(

                    jogador=row.get(
                        "jogador"
                    ),

                    tipo_lesao=row.get(
                        "tipo_lesao"
                    ),

                    local_lesao=row.get(
                        "grupo_corporal"
                    ),

                    status="out",

                    jogos_lesionado=row.get(
                        "jogos_perdidos",
                        row.get(
                            "dias_fora",
                            0
                        )
                    ),

                    data_lesao=row.get(
                        "data_lesao"
                    ),

                    retorno_previsto=row.get(
                        "data_retorno"
                    ),

                    observacoes=(
                        f"CID: "
                        f"{row.get('CID', 'N/A')} | "
                        f"Cirurgia: "
                        f"{'Sim' if row.get('precisou_de_cirurgia') else 'Não'}"
                    )
                )

                bd.session.add(
                    nova_lesao
                )

            bd.session.commit()

            print(
                f"✅ {len(df)} lesões sincronizadas"
            )

            return redirect(
                "/lesoes"
            )

    return render_template(
        "upload.html"
    )

# =========================
# LISTAR LESÕES
# =========================
@app.route("/lesoes")
def lesoes():

    from flask import request

    busca = request.args.get(
        "busca",
        ""
    ).strip()

    time = request.args.get(
        "time",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()

    gravidade = request.args.get(
        "gravidade",
        ""
    ).strip()

    cirurgia = request.args.get(
        "cirurgia",
        ""
    ).strip()

    query = Lesao.query

    # ======================
    # BUSCA INTELIGENTE
    # ======================

    if busca:

        query = query.filter(

            (
                Lesao.jogador.ilike(
                    f"%{busca}%"
                )
            )

            |

            (
                Lesao.tipo_lesao.ilike(
                    f"%{busca}%"
                )
            )

            |

            (
                Lesao.observacoes.ilike(
                    f"%{busca}%"
                )
            )
        )

    # ======================
    # FILTRO TIME
    # ======================

    if time:

        query = query.filter(

            Lesao.jogador.in_(

                bd.session.query(
                    Jogador.jogador
                ).filter_by(
                    time=time
                )
            )
        )

    # ======================
    # STATUS
    # ======================

    if status:

        query = query.filter_by(
            status=status
        )

    # ======================
    # GRAVIDADE
    # ======================

    if gravidade:

        query = query.filter(

            Lesao.observacoes.ilike(
                f"%{gravidade}%"
            )
        )

    # ======================
    # CIRURGIA
    # ======================

    if cirurgia == "sim":

        query = query.filter(

            Lesao.observacoes.ilike(
                "%Cirurgia: Sim%"
            )
        )

    elif cirurgia == "nao":

        query = query.filter(

            Lesao.observacoes.ilike(
                "%Cirurgia: Não%"
            )
        )

    lista_lesoes = query.order_by(
        Lesao.id.desc()
    ).all()

    # ======================
    # TIMES
    # ======================

    times = sorted([

        x[0]

        for x in

        bd.session.query(
            Jogador.time
        ).distinct().all()

        if x[0]
    ])

    return render_template(

        "lesoes.html",

        lesoes=
        lista_lesoes,

        busca=
        busca,

        time=
        time,

        status=
        status,

        gravidade=
        gravidade,

        cirurgia=
        cirurgia,

        times=
        times,

        Jogador=
        Jogador
    )

# =========================
# DELETAR LESÃO
# =========================
@app.route("/deletar/<int:id>")
def deletar(id):

    from flask import redirect

    lesao = Lesao.query.get_or_404(id)

    bd.session.delete(lesao)

    bd.session.commit()

    return redirect("/lesoes")

# =========================
# JOGADORES
# =========================
@app.route("/jogadores")
def jogadores():

    from flask import request

    busca = request.args.get(
        "busca",
        ""
    ).strip()

    time_filtro = request.args.get(
        "time",
        ""
    ).strip()

    query = Jogador.query

    # =====================
    # BUSCA POR NOME
    # =====================

    if busca:

        query = query.filter(

            Jogador.jogador.ilike(
                f"%{busca}%"
            )
        )

    # =====================
    # FILTRO POR TIME
    # =====================

    if time_filtro:

        query = query.filter(
            Jogador.time ==
            time_filtro
        )

    lista_jogadores = query.all()

    # lista única de times
    times = sorted(

        list(

            set(

                jogador.time
                for jogador
                in Jogador.query.all()

                if jogador.time
            )
        )
    )

    return render_template(

        "jogadores.html",

        jogadores=
        lista_jogadores,

        busca=
        busca,

        time_filtro=
        time_filtro,

        times=
        times
    )

# =========================
# UPLOAD JOGADORES
# =========================
@app.route(
    "/upload-jogadores",
    methods=["GET", "POST"]
)
def upload_jogadores():

    from flask import (
        request,
        redirect,
        render_template
    )

    from nba_roster_scraper import (
        scrape_team
    )

    if request.method == "POST":

        tipo = request.form.get(
            "tipo"
        )

        adicionados = 0
        atualizados = 0
        ignorados = 0

        df = None

        # =========================
        # CSV
        # =========================

        if tipo == "csv":

            arquivo = request.files.get(
                "arquivo"
            )

            if arquivo and arquivo.filename:

                caminho = os.path.join(
                    "data",
                    arquivo.filename
                )

                arquivo.save(
                    caminho
                )

                df = pd.read_csv(
                    caminho
                )

        # =========================
        # NBA ROSTER
        # =========================

        elif tipo == "nba":

            entrada = str(

                request.form.get(
                    "time_nba",
                    ""
                )

            ).strip()

            try:

                # agora aceita URL direta
                df = scrape_team(
                    entrada
                )

            except Exception as e:

                print(
                    "\n❌ Erro NBA:",
                    e,
                    "\n"
                )

                return redirect(
                    "/upload-jogadores"
                )

        else:

            return redirect(
                "/upload-jogadores"
            )

        # segurança
        if df is None or df.empty:

            print(
                "\n⚠️ Nenhum jogador encontrado\n"
            )

            return redirect(
                "/upload-jogadores"
            )

        # =========================
        # SALVAR / ATUALIZAR
        # =========================

        for _, row in df.iterrows():

            nome_jogador = str(

                row.get(
                    "jogador",
                    ""
                )

            ).strip()

            jogador_existente = (

                Jogador.query
                .filter(

                    bd.func.lower(
                        Jogador.jogador
                    )

                    ==

                    nome_jogador.lower()
                )
                .first()
            )

            # =====================
            # UPDATE
            # =====================

            if jogador_existente:

                time_antigo = (
                    jogador_existente.time
                )

                jogador_existente.time = (
                    row.get("time")
                )

                jogador_existente.idade = (
                    row.get("idade")
                )

                jogador_existente.altura = (
                    row.get("altura")
                )

                jogador_existente.peso = (
                    row.get("peso")
                )

                jogador_existente.temporada = (
                    row.get(
                        "temporada"
                    )
                )

                jogador_existente.jogos_temporada = (
                    row.get(
                        "jogos_temporada"
                    )
                )

                jogador_existente.foto = (
                    row.get("foto")
                )

                jogador_existente.logo_time = (
                    row.get(
                        "logo_time"
                    )
                )

                atualizados += 1

                if (

                    time_antigo
                    !=
                    row.get("time")

                ):

                    print(

                        f"🔄 "
                        f"{nome_jogador}"

                        f" mudou de "

                        f"{time_antigo}"

                        f" → "

                        f"{row.get('time')}"
                    )

                continue

            # =====================
            # NOVO JOGADOR
            # =====================

            novo_jogador = Jogador(

                jogador=
                nome_jogador,

                time=
                row.get("time"),

                idade=
                row.get("idade"),

                altura=
                row.get("altura"),

                peso=
                row.get("peso"),

                temporada=
                row.get(
                    "temporada"
                ),

                jogos_temporada=
                row.get(
                    "jogos_temporada"
                ),

                foto=
                row.get("foto"),

                logo_time=
                row.get(
                    "logo_time"
                )
            )

            bd.session.add(
                novo_jogador
            )

            adicionados += 1

        bd.session.commit()

        print(
            f"\n✅ {adicionados} adicionados"
        )

        print(
            f"🔄 {atualizados} atualizados"
        )

        print(
            f"⚠️ {ignorados} ignorados\n"
        )

        return redirect(
            "/jogadores"
        )

    # GET
    return render_template(
        "upload_jogadores.html"
    )

# =========================
# ESTATÍSTICAS
# =========================
@app.route("/estatisticas")
def estatisticas():

    from sqlalchemy import func

    # top lesionados bruto
    top_lesionados_bruto = (

        bd.session.query(

            Lesao.jogador,

            func.count(
                Lesao.id
            )
        )

        .group_by(
            Lesao.jogador
        )

        .all()
    )

    # ordenar no Python (garantia de ordenação decrescente)
    top_lesionados = sorted(

        top_lesionados_bruto,

        key=lambda x: x[1],

        reverse=True
    )

    # lesões por time bruto
    lesoes_time_bruto = (

        bd.session.query(

            Jogador.time,

            func.count(
                Lesao.id
            )
        )

        .join(
            Lesao,
            Jogador.jogador
            ==
            Lesao.jogador
        )

        .group_by(
            Jogador.time
        )

        .all()
    )

    # ordenar no Python
    lesoes_time = sorted(

        lesoes_time_bruto,

        key=lambda x: x[1],

        reverse=True
    )

    # tipos lesão bruto
    tipos_lesao_bruto = (

        bd.session.query(

            Lesao.tipo_lesao,

            func.count(
                Lesao.id
            )
        )

        .group_by(
            Lesao.tipo_lesao
        )

        .all()
    )

    # ordenar no Python
    tipos_lesao = sorted(

        tipos_lesao_bruto,

        key=lambda x: x[1],

        reverse=True
    )

    return render_template(
        "estatisticas.html",

        top_labels=
        [x[0] for x in top_lesionados],

        top_values=
        [x[1] for x in top_lesionados],

        time_labels=
        [x[0] for x in lesoes_time],

        time_values=
        [x[1] for x in lesoes_time],

        tipo_labels=
        [x[0] for x in tipos_lesao],

        tipo_values=
        [x[1] for x in tipos_lesao]
    )

# =========================
# DETALHES DA LESÃO
# =========================
@app.route(
    "/api/lesao/<tipo>"
)
def api_lesao(tipo):

    from sqlalchemy import func

    lesoes = Lesao.query.filter(
        Lesao.tipo_lesao == tipo
    ).all()

    if not lesoes:

        return jsonify({
            "erro":
            "Lesão não encontrada"
        })

    total = len(
        lesoes
    )

    jogos_perdidos = [

        x.jogos_lesionado
        for x in lesoes
        if x.jogos_lesionado
    ]

    media_recuperacao = round(

        sum(
            jogos_perdidos
        ) / len(
            jogos_perdidos
        ),

        1
    ) if jogos_perdidos else 0

    recorrentes = sum(

        1
        for x in lesoes

        if x.observacoes
        and "recorr" in
        x.observacoes.lower()
    )

    top_jogadores = {}

    for lesao in lesoes:

        nome = (
            lesao.jogador
        )

        top_jogadores[
            nome
        ] = (

            top_jogadores.get(
                nome,
                0
            ) + 1
        )

    top_jogadores = sorted(

        top_jogadores.items(),

        key=lambda x: x[1],

        reverse=True
    )[:8]

    tratamentos = {

        "Hamstring Strain": {
            "tratamento": [
                "Fisioterapia",
                "Fortalecimento muscular",
                "Controle de carga",
                "Retorno gradual"
            ],
            "risco":
            "alto"
        },

        "Achilles Tear": {
            "tratamento": [
                "Cirurgia",
                "Reabilitação intensiva",
                "Fortalecimento gradual",
                "Treino progressivo"
            ],
            "risco":
            "muito alto"
        },

        "Achilles Injury": {
            "tratamento": [
                "Repouso",
                "Fisioterapia",
                "Controle de impacto"
            ],
            "risco":
            "moderado"
        },

        "Ankle Injury": {
            "tratamento": [
                "Gelo",
                "Fisioterapia",
                "Estabilidade"
            ],
            "risco":
            "moderado"
        },

        "Knee Injury": {
            "tratamento": [
                "Fortalecimento",
                "Controle biomecânico",
                "Reabilitação"
            ],
            "risco":
            "alto"
        }
    }

    # fallback
    tratamento = tratamentos.get(
        tipo,
        {
            "tratamento": [
                "Monitoramento médico",
                "Fisioterapia"
            ],
            "risco":
            "moderado"
        }
    )

    return jsonify({

        "tipo":
        tipo,

        "total_casos":
        total,

        "media_recuperacao":
        media_recuperacao,

        "recorrencia":
        round(
            (
                recorrentes
                / total
            ) * 100,
            1
        ),

        "risco":
        tratamento[
            "risco"
        ],

        "tratamento":
        tratamento[
            "tratamento"
        ],

        "jogadores":
        top_jogadores
    })

# =========================
# EDITAR LESÃO
# =========================
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    from flask import request, redirect

    lesao = Lesao.query.get_or_404(id)

    if request.method == "POST":

        lesao.jogador = request.form["jogador"]

        lesao.tipo_lesao = request.form["tipo_lesao"]

        lesao.local_lesao = request.form["local_lesao"]

        lesao.status = request.form["status"]

        lesao.jogos_lesionado = request.form["jogos_lesionado"]

        lesao.data_lesao = request.form["data_lesao"]

        lesao.retorno_previsto = request.form["retorno_previsto"]

        lesao.observacoes = request.form["observacoes"]

        bd.session.commit()

        return redirect("/lesoes")

    return render_template(
        "editar.html",
        lesao=lesao
    )

# =========================
# DELETAR JOGADOR
# =========================

@app.route("/deletar-jogador/<nome>")
def deletar_jogador(nome):

    from flask import redirect

    jogador = Jogador.query.filter_by(
        jogador=nome
    ).first_or_404()

    # apagar lesões relacionadas
    Lesao.query.filter_by(
        jogador=nome
    ).delete()

    bd.session.delete(jogador)

    bd.session.commit()

    return redirect("/jogadores")

# =========================
# DELETAR VÁRIOS JOGADORES
# =========================
@app.route(
    "/deletar-jogadores",
    methods=["POST"]
)
def deletar_jogadores():

    from flask import (
        request,
        redirect
    )

    jogadores = request.form.getlist(
        "jogadores"
    )

    for nome in jogadores:

        jogador = (
            Jogador.query
            .filter_by(
                jogador=nome
            )
            .first()
        )

        if jogador:

            Lesao.query.filter_by(
                jogador=nome
            ).delete()

            bd.session.delete(
                jogador
            )

    bd.session.commit()

    return redirect(
        "/jogadores"
    )

# =========================
# ADICIONAR JOGADOR
# =========================
@app.route("/adicionar-jogador", methods=["GET", "POST"])
def adicionar_jogador():

    from flask import request, redirect

    if request.method == "POST":

        novo_jogador = Jogador(

            jogador=request.form["jogador"],

            time=request.form["time"],

            idade=request.form["idade"],

            altura=request.form["altura"],

            peso=request.form["peso"],

            temporada=request.form["temporada"],

            jogos_temporada=request.form[
                "jogos_temporada"
            ],

            foto=request.form["foto"],

            logo_time=request.form[
                "logo_time"
            ]
        )

        bd.session.add(novo_jogador)

        bd.session.commit()

        return redirect("/jogadores")

    return render_template(
        "adicionar_jogador.html"
    )

# =========================
# ADICIONAR LESÃO JOGADOR
# =========================
@app.route(
    "/adicionar-lesao/<nome>",
    methods=["GET", "POST"]
)
def adicionar_lesao_jogador(nome):

    from flask import request, redirect
    from datetime import date

    jogador = Jogador.query.filter_by(
        jogador=nome
    ).first_or_404()

    if request.method == "POST":

        nova_lesao = Lesao(

            jogador=jogador.jogador,

            tipo_lesao=request.form[
                "tipo_lesao"
            ],

            local_lesao=request.form[
                "local_lesao"
            ],

            status=request.form[
                "status"
            ],

            jogos_lesionado=request.form[
                "jogos_lesionado"
            ],

            data_lesao=request.form[
                "data_lesao"
            ],

            retorno_previsto=request.form[
                "retorno_previsto"
            ],

            observacoes=request.form[
                "observacoes"
            ]
        )

        bd.session.add(nova_lesao)

        bd.session.commit()

        return redirect(
            f"/jogador/{nome}"
        )

    return render_template(
        "adicionar_lesao_jogador.html",

        jogador=jogador,

        hoje=date.today()
    )

# =========================
# PERFIL TIME
# =========================
@app.route("/time/<nome>")
def perfil_time(nome):

    jogadores = Jogador.query.filter_by(
        time=nome
    ).all()

    total_jogadores = len(jogadores)

    lesionados = Lesao.query.filter(
        Lesao.jogador.in_(
            [j.jogador for j in jogadores]
        )
    ).all()

    total_lesoes = len(lesionados)

    jogadores_out = len([
        l for l in lesionados
        if l.status == "out"
    ])

    logo = None

    if jogadores:
        logo = jogadores[0].logo_time

    return render_template(
        "time.html",

        nome=nome,
        jogadores=jogadores,

        logo=logo,

        total_jogadores=total_jogadores,
        total_lesoes=total_lesoes,
        jogadores_out=jogadores_out
    )

with app.app_context():

    for jogador in Jogador.query.all():

        if jogador.time in TEAM_LOGOS:

            jogador.logo_time = TEAM_LOGOS[
                jogador.time
            ]

    bd.session.commit()

    print(
        "✅ Logos atualizadas"
    )

# =========================
# PESQUISAR LESÃO
# =========================
@app.route(
    "/pesquisar-lesao",
    methods=["GET"]
)
def pesquisar_lesao():

    termo = request.args.get(
        "lesao",
        ""
    ).strip()

    # =========================
    # TRADUÇÃO INTELIGENTE PT → NBA
    # =========================

    termos_dicio = {

        "entorse": "Sprain",

        "torção": "Sprain",

        "torcao": "Sprain",

        "distensão": "Strain",

        "distensao": "Strain",

        "estiramento": "Strain",

        "ruptura": "Tear",

        "fratura": "Fracture",

        "dor": "Soreness",

        "soreness": "Soreness",

        "luxação": "Dislocation",

        "luxacao": "Dislocation",

        "inflamação": "Inflammation",

        "inflamacao": "Inflammation",

        "contusão": "Contusion",

        "contusao": "Contusion",

        "espasmo": "Spasm",

        "espasmos": "Spasms",

        "lesão": "Injury",

        "lesao": "Injury",

        "tendinite": "Tendinitis",

        "tendinopatia": "Tendinopathy",

        "tornozelo": "Ankle",

        "joelho": "Knee",

        "menisco": "Meniscus",

        "ligamento": "ACL",

        "coxa": "Hamstring",

        "posterior": "Hamstring",

        "panturrilha": "Calf",

        "quadriceps": "Quadriceps",

        "quadríceps": "Quadriceps",

        "virilha": "Groin",

        "adutor": "Adductor",

        "costas": "Back",

        "ombro": "Shoulder",

        "pé": "Foot",

        "pe": "Foot",

        "dedo": "Toe",

        "aquiles": "Achilles",

        "quadril": "Hip",

        "punho": "Wrist",

        "pulso": "Wrist",

        "mão": "Hand",

        "mao": "Hand",

        "dedos": "Fingers"
    }

    # Separar palavras e traduzir individualmente
    palavras = termo.lower().split()

    termos_ingles = []

    for p in palavras:

        if p in ["de", "do", "da", "no", "na", "em", "para", "com"]:

            continue

        if p in termos_dicio:

            termos_ingles.append(
                termos_dicio[p]
            )

        else:

            termos_ingles.append(
                p.capitalize()
            )

    if termos_ingles:

        termo_busca = " ".join(
            termos_ingles
        )

    else:

        termo_busca = termo

    # =========================
    # TRATAMENTO COMUM
    # =========================

    tratamentos = {

        "Ankle Sprain": [

            "Repouso relativo",
            "Gelo e compressão",
            "Fisioterapia",
            "Fortalecimento do tornozelo",
            "Retorno gradual"
        ],

        "High Ankle Sprain": [

            "Imobilização parcial",
            "Controle de carga",
            "Fisioterapia",
            "Treino de estabilidade",
            "Retorno progressivo"
        ],

        "Hamstring Strain": [

            "Fisioterapia muscular",
            "Fortalecimento posterior",
            "Controle de sprint",
            "Alongamento",
            "Retorno progressivo"
        ],

        "Calf Strain": [

            "Fortalecimento panturrilha",
            "Controle de impacto",
            "Fisioterapia",
            "Mobilidade",
            "Retorno gradual"
        ],

        "Quadriceps Injury": [

            "Fortalecimento quadríceps",
            "Controle de carga",
            "Gelo",
            "Fisioterapia",
            "Treino progressivo"
        ],

        "Adductor Strain": [

            "Fortalecimento adutor",
            "Controle movimento lateral",
            "Fisioterapia",
            "Mobilidade",
            "Retorno gradual"
        ],

        "Knee Soreness": [

            "Controle de carga",
            "Fortalecimento joelho",
            "Mobilidade",
            "Fisioterapia",
            "Restrição de minutos"
        ],

        "Meniscus Injury": [

            "Fisioterapia",
            "Fortalecimento",
            "Controle de impacto",
            "Reabilitação funcional",
            "Retorno gradual"
        ],

        "ACL Injury": [

            "Cirurgia (quando necessário)",
            "Fisioterapia intensa",
            "Fortalecimento muscular",
            "Treino functional",
            "Retorno prolongado"
        ],

        "Back Spasms": [

            "Controle de carga",
            "Mobilidade",
            "Fortalecimento core",
            "Fisioterapia",
            "Redução impacto"
        ],

        "Shoulder Injury": [

            "Fortalecimento ombro",
            "Mobilidade",
            "Fisioterapia",
            "Controle de contato",
            "Retorno progressivo"
        ],

        "Achilles Tendinopathy": [

            "Controle de carga",
            "Fortalecimento excêntrico",
            "Fisioterapia",
            "Controle de impacto",
            "Retorno gradual"
        ],

        "Hip Tightness": [

            "Mobilidade quadril",
            "Alongamento",
            "Fisioterapia",
            "Controle de carga",
            "Retorno progressivo"
        ],

        "Foot Sprain": [

            "Imobilização parcial",
            "Fisioterapia",
            "Controle de impacto",
            "Fortalecimento",
            "Retorno gradual"
        ],

        "Sprain": [

            "Repouso relativo",
            "Gelo e compressão",
            "Fisioterapia",
            "Fortalecimento",
            "Retorno gradual"
        ],

        "Strain": [

            "Alongamento leve",
            "Fisioterapia muscular",
            "Fortalecimento gradual",
            "Controle de carga",
            "Retorno progressivo"
        ],

        "Tear": [

            "Avaliação médica especializada",
            "Fisioterapia intensa",
            "Fortalecimento muscular progressivo",
            "Retorno muito gradual"
        ],

        "Fracture": [

            "Imobilização médica",
            "Consolidação óssea monitorada",
            "Fisioterapia pós-gesso",
            "Recuperação de mobilidade",
            "Retorno gradual"
        ],

        "Soreness": [

            "Controle de minutos e carga",
            "Fisioterapia regenerativa",
            "Alongamento muscular",
            "Gelo pós-treino"
        ],

        "Injury": [

            "Monitoramento médico",
            "Fisioterapia regenerativa",
            "Treino adaptado"
        ]
    }

    # Tenta obter o tratamento exato
    tratamento = tratamentos.get(
        termo_busca
    )

    # Fallback por palavra-chave se não achar
    if not tratamento:

        for t in termos_ingles:

            if t in tratamentos:

                tratamento = tratamentos[t]

                break

    casos = []
    estatisticas = None
    cbr_resultado = None
    ml_previsao = None
    casos_similares = []

    if termo:

        # =========================
        # DATASET
        # =========================

        df = pd.read_csv(
            "data/cbr_nba_cases.csv"
        )

        # =========================
        # FILTRAR LESÃO (AND LOGICAL)
        # =========================

        casos_df = df

        for t in termos_ingles:

            casos_df = casos_df[

                casos_df["tipo_lesao"]
                .str.contains(

                    t,

                    case=False,

                    na=False
                )
            ]

        # =========================
        # ESTATÍSTICAS
        # =========================

        if not casos_df.empty:

            estatisticas = {

                "casos":

                len(casos_df),

                "media_retorno":

                round(

                    casos_df[
                        "dias_retorno_real"
                    ].mean(),

                    1
                ),

                "media_jogos":

                round(

                    casos_df[
                        "jogos_lesionado"
                    ].mean(),

                    1
                ),

                "recorrencia":

                round(

                    (
                        casos_df[
                            "recorrencia"
                        ]
                        ==
                        "sim"
                    ).mean()

                    * 100,

                    1
                )
            }

            # =========================
            # CBR PREVISÃO
            # =========================

            try:

                query_case = {

                    "idade":
                    28,

                    "altura":
                    1.98,

                    "peso":
                    98,

                    "time":
                    "",

                    "tipo_lesao":
                    termo_busca,

                    "local_lesao":
                    "lower_body",

                    "status":
                    "out",

                    "jogos_lesionado":
                    0,

                    "historico_lesoes":
                    1,

                    "temporada":
                    2025,

                    "recorrencia":
                    "nao",

                    "resultado_final":
                    "retornou_bem"
                }

                retrieved = retrieve_cases(

                    query_case,

                    casos_df,

                    k=min(3, len(casos_df))
                )

                cbr_resultado = adapt(

                    retrieved,

                    query_case
                )

                casos_similares = retrieved.to_dict(
                    "records"
                )

            except Exception as e:

                print(
                    "\n❌ Erro CBR:",
                    e,
                    "\n"
                )

            # =========================
            # PREVISÃO ML
            # =========================

            try:

                class DummyJogador:

                    def __init__(self):

                        self.idade = 28

                        self.altura = 1.98

                        self.peso = 98

                        self.jogos_temporada = 82

                dummy_jogador = DummyJogador()

                ml_previsao = prever_recuperacao_ml(

                    dummy_jogador,

                    termo_busca,

                    gravidade="moderada",

                    recorrencia="nao"
                )

            except Exception as e:

                print(
                    "\n❌ Erro ML:",
                    e,
                    "\n"
                )

            casos = casos_df.to_dict(
                "records"
            )

    return render_template(

        "pesquisar_lesao.html",

        termo=
        termo,

        casos=
        casos,

        estatisticas=
        estatisticas,

        cbr_resultado=
        cbr_resultado,

        casos_similares=
        casos_similares,

        tratamento=
        tratamento,

        ml_previsao=
        ml_previsao
    )


# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(debug=True)
