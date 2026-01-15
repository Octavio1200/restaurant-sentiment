from pathlib import Path
import pandas as pd
import subprocess
import sys


def test_metrics_smoke(tmp_path: Path, monkeypatch):
    data_dir = tmp_path / "data" / "processed"
    data_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(
        {
            "label_proxy": ["negative", "neutral", "positive", "positive"],
            "model_label": ["negative", "neutral", "neutral", "positive"],
        }
    )
    pred_path = data_dir / "predictions.parquet"
    df.to_parquet(pred_path, index=False)

    monkeypatch.chdir(tmp_path)

    repo_root = Path(__file__).resolve().parents[1]
    env = dict(**__import__("os").environ)
    env["PYTHONPATH"] = str(repo_root)

    script = repo_root / "src" / "evaluation" / "metrics.py"
    result = subprocess.run([sys.executable, str(script)], env=env, capture_output=True, text=True)

    assert result.returncode == 0, f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    assert (data_dir / "classification_report.txt").exists()
    assert (data_dir / "confusion_matrix.csv").exists()
