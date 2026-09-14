"""Download every document cited in data/ai_rd_benchmarks.csv into cards/<lab>/ and extract its text.

    python scripts/fetch_cards.py            # fetch what is missing, extract text, rewrite cards/index.csv
    python scripts/fetch_cards.py --refetch  # re-download everything

PDFs are saved as-is and their text goes next to them as <slug>.txt with `=== PAGE n ===` markers, so a
row's `page` in the data CSV can be checked with grep. Web pages are saved as .html plus a plain-text
rendering. cards/index.csv maps each URL to its local file."""
from __future__ import annotations

import csv
import hashlib
import html
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlparse

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "cards"
DATA = ROOT / "data" / "ai_rd_benchmarks.csv"


def slug_for(url: str) -> str:
    u = urlparse(url)
    path = unquote(u.path).rstrip("/")
    name = path.rsplit("/", 1)[-1] or u.netloc
    is_pdf = name.lower().endswith(".pdf")
    stem = re.sub(r"\.pdf$", "", name, flags=re.I)
    if u.netloc == "x.com":
        stem = "x-" + "-".join(p for p in path.split("/") if p)
    elif u.netloc.endswith("arxiv.org"):
        stem = "arxiv-" + stem
    elif not is_pdf and u.netloc not in ("cdn.openai.com", "storage.googleapis.com", "deploymentsafety.openai.com"):
        stem = u.netloc.replace("www.", "").split(".")[0] + "-" + stem
    stem = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
    return stem + (".pdf" if is_pdf else ".html")


def fetch(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["curl", "-sSL", "--retry", "3", "--max-time", "300", "-A",
                        "Mozilla/5.0 (X11; Linux x86_64) ai-rnd-benchmarks/1.0", "-o", str(dest), url],
                       capture_output=True, text=True)
    if r.returncode != 0 or not dest.exists() or dest.stat().st_size == 0:
        print(f"  FAILED {url}: {r.stderr.strip()[:200]}", file=sys.stderr)
        dest.unlink(missing_ok=True)
        return False
    head = dest.read_bytes()[:5]
    if dest.suffix == ".pdf" and head != b"%PDF-":
        # A URL we expected to be a PDF answered with HTML (a landing page or an error page).
        alt = dest.with_suffix(".html")
        dest.rename(alt)
        print(f"  note: {url} is not a PDF; saved as {alt.name}", file=sys.stderr)
    return True


def pdf_text(path: Path) -> tuple[str, int]:
    import pypdf
    reader = pypdf.PdfReader(str(path))
    parts = []
    for i, page in enumerate(reader.pages):
        try:
            t = page.extract_text() or ""
        except Exception as e:  # noqa: BLE001
            t = f"[extraction failed: {e}]"
        parts.append(f"\n=== PAGE {i + 1} ===\n{t}")
    return "".join(parts), len(reader.pages)


def html_text(path: Path) -> tuple[str, int]:
    raw = path.read_text(errors="replace")
    raw = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h\d|tr|section|article)>", "\n", raw)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
    return text, 0


def main(refetch: bool = False):
    d = pd.read_csv(DATA, dtype=str, keep_default_na=False)
    urls = pd.concat([d[["lab", "card_url"]].rename(columns={"card_url": "url"}),
                      d[["lab", "source_url"]].rename(columns={"source_url": "url"})]).drop_duplicates()
    urls = urls[urls["url"] != ""].sort_values(["lab", "url"])
    rows = []
    for lab, url in urls.itertuples(index=False):
        slug = slug_for(url)
        dest = CARDS / lab / slug
        alt = dest.with_suffix(".html")
        existing = dest if dest.exists() else (alt if alt.exists() else None)
        if refetch or existing is None:
            print(f"{lab}: fetching {url}")
            if not fetch(url, dest):
                rows.append({"lab": lab, "url": url, "file": "", "pages": "", "bytes": "", "sha256": "", "fetched": date.today().isoformat(), "status": "failed"})
                continue
            existing = dest if dest.exists() else alt
        text, pages = pdf_text(existing) if existing.suffix == ".pdf" else html_text(existing)
        if existing.suffix == ".html" and len(text) < 1500:
            # A bot wall or a JavaScript shell (openai.com, x.com, neowin): keep the link, not the stub.
            print(f"  blocked: {url} returned no readable text; not kept", file=sys.stderr)
            existing.unlink(); existing.with_suffix(".txt").unlink(missing_ok=True)
            rows.append({"lab": lab, "url": url, "file": "", "pages": "", "bytes": "", "sha256": "", "fetched": date.today().isoformat(), "status": "blocked"})
            continue
        existing.with_suffix(".txt").write_text(text)
        rows.append({"lab": lab, "url": url, "file": str(existing.relative_to(ROOT)), "pages": pages or "",
                     "bytes": existing.stat().st_size, "sha256": hashlib.sha256(existing.read_bytes()).hexdigest()[:16],
                     "fetched": date.today().isoformat(), "status": "ok"})
    with open(CARDS / "index.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    ok = sum(r["status"] == "ok" for r in rows)
    print(f"{ok}/{len(rows)} documents; index at cards/index.csv")


if __name__ == "__main__":
    main(refetch="--refetch" in sys.argv)
