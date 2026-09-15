"""Download the external datasets used for the capability-versus-uplift page into data/external/.

    python scripts/fetch_external.py

Epoch AI, Epoch Capabilities Index model scores (CC-BY): https://epoch.ai/data/eci_scores.csv
Epoch AI, Notable AI models (CC-BY): https://epoch.ai/data/notable_ai_models.csv"""
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {"epoch_eci_scores.csv": "https://epoch.ai/data/eci_scores.csv",
         "epoch_notable_ai_models.csv": "https://epoch.ai/data/notable_ai_models.csv"}
out = ROOT / "data" / "external"; out.mkdir(exist_ok=True)
for name, url in FILES.items():
    subprocess.run(["curl", "-sSL", "--retry", "3", "-A", "Mozilla/5.0 ai-rnd-benchmarks/1.0", "-o", str(out / name), url], check=True)
    print(name, (out / name).stat().st_size, "bytes")
(out / "FETCHED").write_text(date.today().isoformat() + "\n")
