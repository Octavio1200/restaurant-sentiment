# Restaurant Sentiment (LLM + MLOps)

Proyecto de análisis de sentimiento para reseñas de restaurantes (estilo Yelp):
- API simulada con FastAPI
- Ingesta batch a `data/raw/`
- Inferencia con LLaMA (Transformers)
- Dashboard en Streamlit
- Evaluación + feedback loop
- Tracking con MLflow y versionado de datos con DVC (próximos pasos)

## Quickstart (Windows)
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pyarrow
uvicorn src.ingest.api_simulator:app --reload
python src\ingest\fetch_reviews.py
sql