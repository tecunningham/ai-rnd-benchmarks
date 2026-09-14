# AI R&D benchmarks in closed-lab model cards

The AI R&D evaluation scores that OpenAI, Anthropic and Google DeepMind report in their model and
system cards, collected in one long-form CSV with a source and a confidence flag on every row, and
rendered as a Quarto site with a sidebar: two cross-lab figures, then per lab, a saturation overview of every bounded evaluation on one 0 to
100 percent axis, a log-axis overview of the unbounded ones as multiples of the card's human
reference, one small panel per evaluation over time, and a benchmark-by-model table.

Rendered site: https://tecunningham.github.io/ai-rnd-benchmarks/

## Layout

| path | what |
|---|---|
| `index.qmd` | across the labs: shared-benchmark panels, every lab's research evaluations on one axis, every lab's unbounded evaluations on one log axis |
| `openai.qmd`, `anthropic.qmd`, `gdm.qmd` | one page per lab: bounded overview, unbounded overview, small multiples, table, cards |
| `method.qmd` | provenance, how to read the figures, the frontier rule |
| `src/site.py` | the `show_*` helpers the pages call |
| `data/ai_rd_benchmarks.csv` | one row per score (lab, model, card, benchmark, conditions, score, source, confidence) |
| `data/ai_rd_benchmark_series.csv` | per-series metadata: ceiling, direction, human reference, threshold, category, retirement |
| `data/notes/ai-rd-benchmarks.md` | collection and verification notes, card by card |
| `src/benchmarks.py` | loading, the frontier rule, tables and every figure |
| `cards/<lab>/` | every cited card, report and post, as fetched (PDF or HTML) plus its extracted text; `cards/index.csv` maps URLs to files |
| `scripts/fetch_cards.py` | downloads the documents cited in the data CSV into `cards/` and extracts their text |
| `scripts/annotate_sources.py` | locates each row in its document (page) and fills the `quote` column for qualitative rows |
| `scripts/digitize_curves.py` | reads the score-against-budget charts in the OpenAI cards into `data/ai_rd_scaling_curves.csv` |
| `src/plots.py` | shared matplotlib style |

## Render

```
pip install -r requirements.txt
quarto render
```

`freeze: auto` caches executed cells under `_freeze/`; delete that directory (or edit the page)
to force re-execution after a data change. The GitHub Actions workflow in `.github/workflows/`
renders on every push to `main` and deploys to GitHub Pages (repository Settings, Pages, Source =
GitHub Actions).

## Conventions

- Scores are as the lab reports them and are not comparable across labs.
- Every table cell links to its source, opened at the right page of the local copy of the card; qualitative cells quote the card's own words.
- Cells carry provenance marks: none = read from the card, `*` = launch post, `†` = search-result
  excerpt, `‡` = memory, `≈` = read off a chart (highest point on the model's curve); chart-read points are hollow in the figures.
- Only cards on the evaluation frontier are shown: a card that improves on at most a quarter of the
  evaluations it shares with earlier cards is left out of the figures and tables (its rows stay in the CSV).
- A black cross sits on a series' last reported value when later cards stop reporting it.

This began as an appendix of [open-labs](https://github.com/tecunningham/open-labs).
