import pandas as pd
import numpy as np


# ==========================
# CONFIG
# ==========================

INPUT_FILE = (
    "data/injury_history/"
    "historico_lesoes_tratado.csv"
)

OUTPUT_FILE = (
    "data/injury_history/"
    "historico_lesoes_gold.csv"
)


# ==========================
# NORMALIZAÇÃO AVANÇADA
# ==========================

PATTERNS = {

    "Ankle Injury": [
        "ankle",
        "rolled ankle"
    ],

    "Knee Injury": [
        "knee",
        "meniscus",
        "acl",
        "mcl",
        "patella"
    ],

    "Hamstring Strain": [
        "hamstring"
    ],

    "Calf Strain": [
        "calf"
    ],

    "Achilles Injury": [
        "achilles",
        "tendon"
    ],

    "Groin Strain": [
        "groin",
        "adductor"
    ],

    "Hip Injury": [
        "hip"
    ],

    "Foot Injury": [
        "foot"
    ],

    "Toe Injury": [
        "toe"
    ],

    "Back Injury": [
        "back",
        "spine"
    ],

    "Shoulder Injury": [
        "shoulder"
    ],

    "Hand Injury": [
        "hand",
        "thumb",
        "palm"
    ],

    "Wrist Injury": [
        "wrist"
    ],

    "Finger Injury": [
        "finger"
    ],

    "Elbow Injury": [
        "elbow"
    ],

    "Neck Injury": [
        "neck"
    ],

    "Quadriceps Injury": [
        "quad",
        "quadricep"
    ],

    "Concussion": [
        "concussion",
        "head"
    ],

    "Illness": [
        "illness",
        "flu",
        "virus",
        "covid",
        "sickness"
    ],

    "Lower Leg Injury": [
        "leg",
        "lower leg",
        "upper leg",
        "tibia",
        "shin",
        "fibula"
    ],

    "Heel Injury": [
        "heel"
    ],

    "Abdominal Injury": [
        "abdominal",
        "abdomen",
        "core"
    ],

    "Rib Injury": [
        "rib",
        "chest"
    ],

    "Facial Injury": [
        "nose",
        "jaw",
        "face",
        "mouth",
        "eye"
    ],

    "Pelvis Injury": [
        "pelvis",
        "pelvic"
    ],

    "Protocol": [
        "health and safety",
        "protocol"
    ],

    "Neurological": [
        "dizziness",
        "migraine",
        "vertigo"
    ]
}


# ==========================
# GRAVIDADE
# ==========================

def extrair_gravidade(texto):

    texto = str(texto).lower()

    grave = [

        "surgery",
        "rupture",
        "tear",
        "torn",
        "acl",
        "achilles",
        "out for season",
        "fracture",
        "out indefinitely"
    ]

    moderada = [

        "out",
        "strain",
        "sprain",
        "injury",
        "protocol"
    ]

    leve = [

        "dtd",
        "questionable",
        "probable",
        "soreness",
        "tightness"
    ]

    if any(x in texto for x in grave):
        return "grave"

    if any(x in texto for x in moderada):
        return "moderada"

    if any(x in texto for x in leve):
        return "leve"

    return "moderada"


# ==========================
# NORMALIZAR LESÃO
# ==========================

def normalizar(texto):

    texto = str(texto).lower()

    for lesao, termos in PATTERNS.items():

        for termo in termos:

            if termo in texto:

                return lesao

    return "Other"


# ==========================
# SCORE GRAVIDADE
# ==========================

GRAVIDADE_SCORE = {

    "leve": 1,
    "moderada": 2,
    "grave": 3
}


# ==========================
# GRUPO CORPORAL
# ==========================

GRUPO_MAP = {

    "Ankle Injury":
    "lower_body",

    "Knee Injury":
    "lower_body",

    "Hamstring Strain":
    "lower_body",

    "Calf Strain":
    "lower_body",

    "Achilles Injury":
    "lower_body",

    "Groin Strain":
    "lower_body",

    "Hip Injury":
    "lower_body",

    "Foot Injury":
    "lower_body",

    "Toe Injury":
    "lower_body",

    "Quadriceps Injury":
    "lower_body",

    "Lower Leg Injury":
    "lower_body",

    "Heel Injury":
    "lower_body",

    "Pelvis Injury":
    "lower_body",

    "Back Injury":
    "trunk",

    "Abdominal Injury":
    "trunk",

    "Rib Injury":
    "trunk",

    "Shoulder Injury":
    "upper_body",

    "Hand Injury":
    "upper_body",

    "Wrist Injury":
    "upper_body",

    "Finger Injury":
    "upper_body",

    "Elbow Injury":
    "upper_body",

    "Neck Injury":
    "upper_body",

    "Facial Injury":
    "head",

    "Concussion":
    "head",

    "Illness":
    "medical",

    "Protocol":
    "medical",

    "Neurological":
    "medical"
}


# ==========================
# DATASET
# ==========================

df = pd.read_csv(
    INPUT_FILE
)

# remover lixo
lixo = [

    "personal",
    "rest",
    "coach decision"
]

mask = ~df[
    "tipo_lesao_original"
].str.lower().str.contains(

    "|".join(lixo),

    na=False
)

df = df[mask].copy()

# normalização
df["tipo_lesao"] = df[
    "tipo_lesao_original"
].apply(normalizar)

# grupo corporal
df["grupo_corporal"] = df[
    "tipo_lesao"
].map(GRUPO_MAP)

# gravidade
df["gravidade"] = df[
    "tipo_lesao_original"
].apply(extrair_gravidade)

# score gravidade
df["gravidade_score"] = df[
    "gravidade"
].map(GRAVIDADE_SCORE)

# recorrência score
df["recorrencia_score"] = np.where(

    df["recorrencia"]
    == "sim",

    1,

    0
)

# dias fora limpo
df["dias_fora"] = pd.to_numeric(

    df["dias_fora"],

    errors="coerce"
)

df = df[

    (
        df["dias_fora"]
        >= 0
    )

    |

    (
        df["dias_fora"]
        .isna()
    )
]

df = df[

    (
        df["dias_fora"]
        <= 365
    )

    |

    (
        df["dias_fora"]
        .isna()
    )
]

# risco inicial
df["risco_score"] = (

    df["gravidade_score"]

    +

    df["recorrencia_score"]
)

# salvar
df.to_csv(

    OUTPUT_FILE,

    index=False
)

print(
    "\n✅ DATASET GOLD SALVO"
)

print(
    f"\n📊 Registros:"
    f" {len(df)}"
)

print(
    "\n📌 Lesões:"
)

print(
    df[
        "tipo_lesao"
    ].value_counts()
)