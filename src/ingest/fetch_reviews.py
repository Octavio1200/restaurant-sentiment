import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

API_URL = "http://127.0.0.1:8000/reviews"

def fetch_reviews(limit: int = 200, seed: int | None = 42) -> pd.DataFrame:
    params = {"limit": limit, "seed": seed}
    r = requests.get(API_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    return pd.DataFrame(data)

def save_raw(df: pd.DataFrame) -> Path:
    out_dir = Path("data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"reviews_{ts}.parquet"
    df.to_parquet(out_path, index=False)
    return out_path

def main():
    df = fetch_reviews(limit=300, seed=42)
    path = save_raw(df)
    print(f"Guardado: {path} | rows={len(df)}")

if __name__ == "__main__":
    main()
