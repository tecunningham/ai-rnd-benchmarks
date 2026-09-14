# Data

Hand-curated. Every row carries a `source_url` and a `confidence` flag.

| file | one row per | key columns |
|---|---|---|
| `ai_rd_benchmarks.csv` | AI R&D benchmark score in a closed-lab model or system card (Google DeepMind, OpenAI, Anthropic) | `frontier` yes/no marks smaller siblings released alongside a frontier model; `confidence` in reported (card or the METR report it cites) / announcement (launch post) / snippet (search-result excerpt) / memory; `family` groups benchmarks; `conditions` holds scaffold, subset and budget; `score` is the plain number, `score_text` the cell as printed; `source_file` is the local copy of the source under `cards/`, `page` the 1-based PDF page the number or statement is on, and `quote` (rows without a number) the card's own words |
| `ai_rd_benchmark_series.csv` | benchmark series in the figures (lab x benchmark, with version and scale splits) | `ceiling` (blank = unbounded), `direction` higher/lower, `human_ref` and `threshold` with labels (red dotted and grey dashed lines), `category`, `overview` yes/no for the shared 0 to 100 percent panel, `deprecated_date` and `deprecated_note` for the card at which the lab stopped reporting the series (black cross), `human_time` for the human effort the reference point represents |

Collection and verification notes, card by card: `notes/ai-rd-benchmarks.md`.

The documents themselves are in `cards/<lab>/` (see `cards/index.csv`), fetched by `scripts/fetch_cards.py`; `scripts/annotate_sources.py` fills `source_file`, `page` and `quote`.
