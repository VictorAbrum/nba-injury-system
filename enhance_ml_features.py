import pandas as pd
import numpy as np


# ==========================
# CONFIG
# ==========================

INPUT_FILE = (
    "data/injury_history/"
    "dataset_ml.csv"
)

OUTPUT_FILE = (
    "data/injury_history/"
    "dataset_ml_enhanced.csv"
)


# ==========================
# DATASET
# ==========================

df = pd.read_csv(
    INPUT_FILE
)

texto = df[
    "tipo_lesao_original"
].fillna("").str.lower()


# ==========================
# FEATURES MÉDICAS
# ==========================

FEATURES = {

    "teve_cirurgia": [
        "surgery",
        "surgical"
    ],

    "teve_ruptura": [
        "rupture",
        "ruptured"
    ],

    "teve_fratura": [
        "fracture",
        "fractured",
        "broken"
    ],

    "teve_torn": [
        "tear",
        "torn"
    ],

    "teve_strain": [
        "strain"
    ],

    "teve_sprain": [
        "sprain"
    ],

    "out_for_season": [
        "out for season"
    ],

    "out_indefinitely": [
        "out indefinitely"
    ],

    "dtd": [
        "dtd",
        "day-to-day"
    ],

    "questionable": [
        "questionable"
    ],

    "probable": [
        "probable"
    ],

    "soreness": [
        "soreness",
        "tightness"
    ]
}


# ==========================
# EXTRAIR FEATURES
# ==========================

for coluna, termos in FEATURES.items():

    df[coluna] = texto.apply(

        lambda x:

        int(

            any(
                termo in x
                for termo in termos
            )
        )
    )


# ==========================
# TARGET LOG
# ==========================

df[
    "dias_fora_log"
] = np.log1p(

    df[
        "dias_fora"
    ]
)


# ==========================
# SCORE MÉDICO
# ==========================

medical_features = [

    "teve_cirurgia",
    "teve_ruptura",
    "teve_fratura",
    "teve_torn",
    "teve_strain",
    "teve_sprain",
    "out_for_season",
    "out_indefinitely"
]

df[
    "medical_risk_score"
] = df[
    medical_features
].sum(axis=1)


# ==========================
# SALVAR
# ==========================

df.to_csv(

    OUTPUT_FILE,

    index=False
)

print(
    "\n✅ DATASET ENHANCED SALVO"
)

print(
    f"\n📊 Registros:"
    f" {len(df)}"
)

print(
    "\n📌 Novas colunas:"
)

for col in FEATURES:

    print(
        col
    )

print(
    "\n📌 Score médico:"
)

print(

    df[
        "medical_risk_score"
    ].describe()
)