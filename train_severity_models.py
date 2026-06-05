import pandas as pd
import joblib
import os

from sklearn.model_selection import (
    train_test_split
)

from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor
)

from sklearn.metrics import (

    accuracy_score,
    classification_report,
    mean_absolute_error,
    r2_score
)

from sklearn.compose import (
    ColumnTransformer
)

from sklearn.pipeline import (
    Pipeline
)

from sklearn.preprocessing import (
    OneHotEncoder
)


# ==========================
# CONFIG
# ==========================

INPUT_FILE = (
    "data/injury_history/"
    "dataset_ml.csv"
)

MODEL_FOLDER = (
    "modelos"
)

os.makedirs(

    MODEL_FOLDER,

    exist_ok=True
)


# ==========================
# DATASET
# ==========================

df = pd.read_csv(
    INPUT_FILE
)

df["temporada"] = (

    df["temporada"]

    .astype(str)

    .str.extract(
        r"(\d{4})"
    )[0]
)

df["temporada"] = pd.to_numeric(

    df["temporada"],

    errors="coerce"
)

df = df.dropna(

    subset=["dias_fora"]
)

df = df[
    df["dias_fora"]
    <= 365
]


# ==========================
# GRAVIDADE REAL
# ==========================

def faixa_gravidade(dias):

    if dias <= 14:
        return "leve"

    elif dias <= 60:
        return "moderada"

    return "grave"


df[
    "gravidade_real"
] = df[
    "dias_fora"
].apply(
    faixa_gravidade
)


print(
    "\n📊 Distribuição:"
)

print(
    df[
        "gravidade_real"
    ].value_counts()
)


# ==========================
# FEATURES
# ==========================

features = [

    "tipo_lesao",
    "grupo_corporal",
    "gravidade",

    "gravidade_score",
    "recorrencia_score",
    "risco_score",

    "idade",
    "altura",
    "peso",

    "temporada",
    "jogos_temporada",

    "historico_lesoes",
    "dias_totais_lesionado"
]

X = df[
    features
]

y_class = df[
    "gravidade_real"
]


categorical_features = [

    "tipo_lesao",
    "grupo_corporal",
    "gravidade"
]


preprocessor = ColumnTransformer(

    transformers=[

        (

            "cat",

            OneHotEncoder(
                handle_unknown="ignore"
            ),

            categorical_features
        )
    ],

    remainder="passthrough"
)


# ==========================
# CLASSIFICADOR
# ==========================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y_class,

    test_size=0.2,

    random_state=42
)

classifier = Pipeline([

    (
        "preprocessor",
        preprocessor
    ),

    (
        "model",

        RandomForestClassifier(

            n_estimators=400,

            max_depth=12,

            random_state=42,

            n_jobs=-1
        )
    )
])

print(
    "\n🧠 Treinando classificador..."
)

classifier.fit(

    X_train,
    y_train
)

pred_class = classifier.predict(
    X_test
)

acc = accuracy_score(

    y_test,

    pred_class
)

print(
    f"\n🎯 Accuracy:"
    f" {acc:.3f}"
)

print(
    "\n📋 Classification report:\n"
)

print(

    classification_report(

        y_test,

        pred_class
    )
)

joblib.dump(

    classifier,

    f"{MODEL_FOLDER}/"
    "severity_classifier.pkl"
)

print(
    "\n✅ Classificador salvo"
)


# ==========================
# MODELOS POR FAIXA
# ==========================

for gravidade in [

    "leve",
    "moderada",
    "grave"
]:

    print(
        f"\n{'='*50}"
    )

    print(
        f"🩺 Modelo:"
        f" {gravidade}"
    )

    subset = df[

        df[
            "gravidade_real"
        ]
        ==
        gravidade
    ]

    if len(subset) < 50:

        print(
            "⚠️ poucos casos"
        )

        continue

    X_sub = subset[
        features
    ]

    y_sub = subset[
        "dias_fora"
    ]

    X_train, X_test, y_train, y_test = train_test_split(

        X_sub,
        y_sub,

        test_size=0.2,

        random_state=42
    )

    regressor = Pipeline([

        (
            "preprocessor",
            preprocessor
        ),

        (
            "model",

            RandomForestRegressor(

                n_estimators=400,

                max_depth=12,

                random_state=42,

                n_jobs=-1
            )
        )
    ])

    regressor.fit(

        X_train,
        y_train
    )

    preds = regressor.predict(
        X_test
    )

    mae = mean_absolute_error(

        y_test,

        preds
    )

    r2 = r2_score(

        y_test,

        preds
    )

    print(
        f"📉 MAE:"
        f" {mae:.2f}"
    )

    print(
        f"📈 R²:"
        f" {r2:.3f}"
    )

    joblib.dump(

        regressor,

        f"{MODEL_FOLDER}/"
        f"{gravidade}_model.pkl"
    )

    print(
        "✅ Modelo salvo"
    )


print(
    "\n🚀 Tudo pronto!"
)