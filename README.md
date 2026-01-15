# Restaurant Sentiment (LLM + MLOps)

Proyecto de análisis de sentimiento para reseñas de restaurantes (estilo Yelp):
- API simulada con FastAPI
- Ingesta batch a `data/raw/`
- Inferencia con LLaMA (Transformers)
- Dashboard en Streamlit
- Evaluación + feedback loop
- Tracking con MLflow y versionado de datos con DVC (próximos pasos)


## Estructura del repo

```bash
restaurant-sentiment/
├─ data/
│  ├─ raw/
│  └─ processed/
├─ src/
│  ├─ ingest/
│  ├─ preprocessing/
│  ├─ model/
│  ├─ evaluation/
│  └─ dashboard/
├─ tests/
└─ README.md
```

## Quickstart (Windows)
### 1) Crear entorno y dependencias
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pyarrow
```
### 2) Levantar API simulada (terminal 1)
```bash
uvicorn src.ingest.api_simulator:app --reload
```
### 3) Generar datos + correr pipeline (terminal 2)
```bash
python src\ingest\fetch_reviews.py
python src\preprocessing\clean.py
python src\model\infer_llama.py
python src\evaluation\metrics.py
```
### 4) Levantar dashboard
```bash
streamlit run src\dashboard\app.py
```