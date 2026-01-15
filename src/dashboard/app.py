from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import streamlit as st
import plotly.express as px


PRED_PATH = Path("data/processed/predictions.parquet")
CLEAN_PATH = Path("data/processed/clean.parquet")
FEEDBACK_PATH = Path("data/processed/feedback.csv")
REPORT_PATH = Path("data/processed/classification_report.txt")
CM_PATH = Path("data/processed/confusion_matrix.csv")

LABELS = ["negative", "neutral", "positive"]


@st.cache_data(show_spinner=False)
def load_predictions() -> pd.DataFrame:
    if PRED_PATH.exists():
        return pd.read_parquet(PRED_PATH)
    if CLEAN_PATH.exists():
        df = pd.read_parquet(CLEAN_PATH)
        if "model_label" not in df.columns:
            df["model_label"] = None
        return df
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_feedback() -> pd.DataFrame:
    if FEEDBACK_PATH.exists():
        try:
            return pd.read_csv(FEEDBACK_PATH)
        except Exception:
            return pd.DataFrame(columns=["review_id", "text_clean", "model_label", "user_label", "timestamp_utc"])
    return pd.DataFrame(columns=["review_id", "text_clean", "model_label", "user_label", "timestamp_utc"])


def ensure_feedback_file():
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not FEEDBACK_PATH.exists():
        pd.DataFrame(
            columns=["review_id", "text_clean", "model_label", "user_label", "timestamp_utc"]
        ).to_csv(FEEDBACK_PATH, index=False)


def append_feedback(review_id: str, text_clean: str, model_label: str, user_label: str):
    ensure_feedback_file()
    row = {
        "review_id": review_id,
        "text_clean": text_clean,
        "model_label": model_label,
        "user_label": user_label,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    pd.DataFrame([row]).to_csv(FEEDBACK_PATH, mode="a", header=False, index=False)


def load_confusion_matrix() -> pd.DataFrame | None:
    if CM_PATH.exists():
        try:
            cm = pd.read_csv(CM_PATH, index_col=0)
            return cm
        except Exception:
            return None
    return None


def load_report_text() -> str | None:
    if REPORT_PATH.exists():
        try:
            return REPORT_PATH.read_text(encoding="utf-8")
        except Exception:
            return None
    return None


st.set_page_config(page_title="Restaurant Sentiment (LLM + MLOps)", layout="wide")

st.title("Restaurant Sentiment (LLM + MLOps)")
st.caption("Pipeline batch + predicciones + evaluación + feedback loop (correcciones).")

df = load_predictions()
fb = load_feedback()
ensure_feedback_file()

if df.empty:
    st.error("No encuentro datos. Ejecuta el pipeline primero para generar data/processed/clean.parquet y predictions.parquet.")
    st.stop()

expected_cols = {"review_id", "restaurant_name", "city", "stars", "text_clean"}
missing = expected_cols - set(df.columns)
if missing:
    st.warning(f"Faltan columnas esperadas en el dataset: {missing}. El dashboard mostrará lo disponible.")


st.sidebar.header("Filtros")

cities = sorted([c for c in df.get("city", pd.Series(dtype=str)).dropna().unique().tolist()])
restaurants = sorted([r for r in df.get("restaurant_name", pd.Series(dtype=str)).dropna().unique().tolist()])
stars_unique = sorted([int(s) for s in df.get("stars", pd.Series(dtype=int)).dropna().unique().tolist()])

sel_city = st.sidebar.selectbox("Ciudad", options=["(Todas)"] + cities, index=0)
sel_rest = st.sidebar.selectbox("Restaurante", options=["(Todos)"] + restaurants, index=0)
sel_stars = st.sidebar.multiselect("Estrellas", options=stars_unique, default=stars_unique)

fdf = df.copy()
if sel_city != "(Todas)" and "city" in fdf.columns:
    fdf = fdf[fdf["city"] == sel_city]
if sel_rest != "(Todos)" and "restaurant_name" in fdf.columns:
    fdf = fdf[fdf["restaurant_name"] == sel_rest]
if "stars" in fdf.columns and sel_stars:
    fdf = fdf[fdf["stars"].astype(int).isin(sel_stars)]


col1, col2, col3, col4 = st.columns(4)

col1.metric("Reseñas (filtradas)", f"{len(fdf):,}")
col2.metric("Reseñas (totales)", f"{len(df):,}")
col3.metric("Feedback total", f"{len(fb):,}")
col4.metric("Feedback (últimas 24h)", f"{(fb['timestamp_utc'].fillna('').str[:10] == datetime.now(timezone.utc).date().isoformat()).sum() if 'timestamp_utc' in fb.columns else 0:,}")


left, right = st.columns([1, 1])

with left:
    st.subheader("Distribución de sentimiento (modelo)")
    if "model_label" in fdf.columns:
        counts = fdf["model_label"].fillna("unknown").value_counts().reset_index()
        counts.columns = ["sentiment", "count"]
        fig = px.bar(counts, x="sentiment", y="count", title="Conteo por sentimiento")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No existe la columna model_label en los datos filtrados.")

with right:
    st.subheader("Proporción de sentimiento (modelo)")
    if "model_label" in fdf.columns:
        counts = fdf["model_label"].fillna("unknown").value_counts().reset_index()
        counts.columns = ["sentiment", "count"]
        fig = px.pie(counts, names="sentiment", values="count", title="Proporción por sentimiento")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No existe la columna model_label en los datos filtrados.")


st.subheader("Reseñas y predicción (con feedback loop)")

display_cols = [c for c in ["review_id", "restaurant_name", "city", "stars", "text_clean", "label_proxy", "model_label"] if c in fdf.columns]
preview = fdf[display_cols].copy() if display_cols else fdf.copy()
preview = preview.reset_index(drop=True)

st.dataframe(preview, use_container_width=True, height=280)

st.markdown("### Corregir sentimiento (feedback)")

if "review_id" not in preview.columns or "text_clean" not in preview.columns or "model_label" not in preview.columns:
    st.info("Para activar feedback necesitas columnas: review_id, text_clean, model_label.")
else:
    idx = st.number_input("Índice de la reseña a corregir (según la tabla)", min_value=0, max_value=max(0, len(preview)-1), value=0, step=1)
    row = preview.iloc[int(idx)]

    st.write("**Texto:**", row["text_clean"])
    st.write("**Predicción del modelo:**", row["model_label"])

    user_label = st.radio("Etiqueta corregida", LABELS, horizontal=True)

    if st.button("Guardar corrección"):
        append_feedback(
            review_id=str(row["review_id"]),
            text_clean=str(row["text_clean"]),
            model_label=str(row["model_label"]),
            user_label=str(user_label),
        )
        st.success("✅ Feedback guardado en data/processed/feedback.csv")
        st.cache_data.clear()


st.subheader("Evaluación (artefactos)")

cm = load_confusion_matrix()
rep = load_report_text()

a, b = st.columns([1, 1])

with a:
    st.markdown("**Classification report**")
    if rep:
        st.code(rep)
    else:
        st.info("No encuentro classification_report.txt. Ejecuta: python src/evaluation/metrics.py")

with b:
    st.markdown("**Confusion matrix**")
    if cm is not None:
        cm_plot = cm.copy()
        cm_plot.index.name = "true"
        cm_plot = cm_plot.reset_index().melt(id_vars="true", var_name="pred", value_name="count")
        fig = px.density_heatmap(cm_plot, x="pred", y="true", z="count", histfunc="sum", title="Matriz de confusión")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(cm, use_container_width=True)
    else:
        st.info("No encuentro confusion_matrix.csv. Ejecuta: python src/evaluation/metrics.py")

st.caption("Tip: si aumentas el tamaño del batch (limit=500) tendrás mejores métricas y gráficos más interesantes.")
