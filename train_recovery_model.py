import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import (
    train_test_split
)

from sklearn.ensemble import (
    RandomForestRegressor
)

from sklearn.metrics import (

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
    "dataset_ml_enhanced.csv"
)

MODEL_PATH = (
    "modelos/"
    "recovery_model_v3.pkl"
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

print(
    f"\n📊 Casos usados:"
    f" {len(df)}"
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
    "dias_totais_lesionado",

    # features médicas
    "teve_cirurgia",
    "teve_ruptura",
    "teve_fratura",
    "teve_torn",
    "teve_strain",
    "teve_sprain",
    "out_for_season",
    "out_indefinitely",
    "dtd",
    "questionable",
    "probable",
    "soreness",

    "medical_risk_score"
]

target = "dias_fora_log"

X = df[
    features
]

y = df[
    target
]


# ==========================
# SPLIT
# ==========================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.2,

    random_state=42
)


# ==========================
# FEATURES
# ==========================

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
# MODELO
# ==========================

model = RandomForestRegressor(

    n_estimators=700,

    max_depth=18,

    min_samples_split=4,

    min_samples_leaf=2,

    random_state=42,

    n_jobs=-1
)

pipeline = Pipeline([

    (
        "preprocessor",
        preprocessor
    ),

    (
        "model",
        model
    )
])


# ==========================
# TREINO
# ==========================

print(
    "\n🧠 Treinando modelo..."
)

pipeline.fit(

    X_train,
    y_train
)

print(
    "✅ Modelo treinado"
)


# ==========================
# PREVISÃO
# ==========================

pred_log = pipeline.predict(
    X_test
)

# voltar do log
preds = np.expm1(
    pred_log
)

real = np.expm1(
    y_test
)

mae = mean_absolute_error(

    real,

    preds
)

r2 = r2_score(

    real,

    preds
)

print(
    f"\n📉 Erro médio:"
    f" {mae:.2f} dias"
)

print(
    f"📈 R²:"
    f" {r2:.3f}"
)


# ==========================
# IMPORTÂNCIA
# ==========================

ohe = pipeline.named_steps[
    "preprocessor"
].named_transformers_[
    "cat"
]

feature_names = list(

    ohe.get_feature_names_out(
        categorical_features
    )
)

feature_names += [

    col
    for col in features
    if col not in categorical_features
]

importances = pipeline.named_steps[
    "model"
].feature_importances_

importance_df = pd.DataFrame({

    "feature":
    feature_names,

    "importance":
    importances
})

importance_df = importance_df.sort_values(

    "importance",

    ascending=False
)

print(
    "\n🔥 TOP FEATURES:"
)

print(
    importance_df.head(20)
)


# ==========================
# SALVAR
# ==========================

joblib.dump(

    pipeline,

    MODEL_PATH
)

print(
    f"\n✅ Modelo salvo:"
    f" {MODEL_PATH}"
)