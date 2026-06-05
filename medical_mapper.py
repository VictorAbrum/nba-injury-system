# ==========================
# NORMALIZADOR MÉDICO NBA
# Compatível com:
# - dataset gold
# - ML
# - CBR
# ==========================

def normalize_injury(
    tipo_lesao,
    local_lesao=""
):

    tipo = str(
        tipo_lesao
    ).lower().strip()

    local = str(
        local_lesao
    ).lower().strip()

    texto = (
        f"{tipo} {local}"
    )

    # =====================
    # PROTOCOL / ILLNESS
    # =====================

    if any(x in texto for x in [

        "protocol",
        "health and safety",
        "covid"
    ]):

        return "Protocol"

    if any(x in texto for x in [

        "illness",
        "flu",
        "virus",
        "migraine",
        "fever",
        "cold",
        "dizziness",
        "sick"
    ]):

        return "Illness"

    if "concussion" in texto:

        return "Concussion"

    # =====================
    # LOWER BODY
    # =====================

    if any(x in texto for x in [

        "ankle",
        "tornozelo"
    ]):

        return "Ankle Injury"

    if any(x in texto for x in [

        "knee",
        "acl",
        "meniscus",
        "patella"
    ]):

        return "Knee Injury"

    if "hamstring" in texto:

        return "Hamstring Strain"

    if any(x in texto for x in [

        "groin",
        "adductor"
    ]):

        return "Groin Strain"

    if any(x in texto for x in [

        "quadriceps",
        "quad"
    ]):

        return "Quadriceps Injury"

    if "calf" in texto:

        return "Calf Strain"

    if "hip" in texto:

        return "Hip Injury"

    if "foot" in texto:

        return "Foot Injury"

    if "toe" in texto:

        return "Toe Injury"

    if "heel" in texto:

        return "Heel Injury"

    # ==========================
    # ACHILLES
    # ==========================

    if "achilles" in texto:

        grave_achilles = [

            "torn",
            "tear",
            "rupture",
            "ruptured",
            "surgery",
            "repair",
            "out for season"
        ]

        if any(

            termo in texto

            for termo in
            grave_achilles
        ):

            return (
                "Achilles Tear"
            )

        leve_achilles = [

            "sore",
            "strain",
            "strained",
            "tendinitis",
            "tendonitis",
            "tendinopathy",
            "injury",
            "dtd"
        ]

        if any(

            termo in texto

            for termo in
            leve_achilles
        ):

            return (
                "Achilles Injury"
            )

        return (
            "Achilles Injury"
        )

    # =====================
    # UPPER BODY
    # =====================

    if "shoulder" in texto:

        return "Shoulder Injury"

    if "wrist" in texto:

        return "Wrist Injury"

    if any(x in texto for x in [

        "hand",
        "thumb",
        "finger"
    ]):

        return "Hand Injury"

    if "elbow" in texto:

        return "Elbow Injury"

    if "neck" in texto:

        return "Neck Injury"

    if any(x in texto for x in [

        "back",
        "lumbar"
    ]):

        return "Back Injury"

    if "rib" in texto:

        return "Rib Injury"

    if "abdominal" in texto:

        return "Abdominal Injury"

    if any(x in texto for x in [

        "face",
        "jaw",
        "nose",
        "facial"
    ]):

        return "Facial Injury"

    if "pelvis" in texto:

        return "Pelvis Injury"

    # =====================
    # FALLBACK
    # =====================

    return "Other"


# =====================
# REGIÃO CORPORAL
# =====================

def get_body_region(
    lesao
):

    lesao = str(
        lesao
    ).lower()

    lower_body = [

        "ankle",
        "knee",
        "hamstring",
        "groin",
        "quadriceps",
        "calf",
        "hip",
        "foot",
        "toe",
        "heel",
        "achilles",
        "leg",
        "pelvis"
    ]

    upper_body = [

        "shoulder",
        "wrist",
        "hand",
        "elbow",
        "neck",
        "back",
        "rib",
        "abdominal",
        "facial"
    ]

    if any(
        x in lesao
        for x in lower_body
    ):

        return (
            "lower_body"
        )

    if any(
        x in lesao
        for x in upper_body
    ):

        return (
            "upper_body"
        )

    return (
        "general"
    )


# =====================
# FAMÍLIA DA LESÃO
# =====================

def get_injury_family(
    lesao
):

    lesao = str(
        lesao
    ).lower()

    if any(
        x in lesao
        for x in [

            "strain",
            "hamstring",
            "groin",
            "calf",
            "quadriceps"
        ]
    ):

        return (
            "muscular"
        )

    if any(
        x in lesao
        for x in [

            "ankle",
            "knee",
            "toe",
            "hip"
        ]
    ):

        return (
            "joint"
        )

    if any(
        x in lesao
        for x in [

            "achilles",
            "tendon"
        ]
    ):

        return (
            "tendon"
        )

    if any(
        x in lesao
        for x in [

            "fracture",
            "rib",
            "facial"
        ]
    ):

        return (
            "bone"
        )

    if any(
        x in lesao
        for x in [

            "concussion",
            "neurological"
        ]
    ):

        return (
            "neurological"
        )

    return (
        "general"
    )