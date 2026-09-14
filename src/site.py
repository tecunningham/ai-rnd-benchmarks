"""Helpers shared by the site's pages, so each .qmd stays short."""
from __future__ import annotations

import matplotlib.pyplot as plt
from IPython.display import Markdown, display

from src import benchmarks

# Quarto's `fig-format: svg` is applied through IPython.display.set_matplotlib_formats, which
# IPython 8 removed, so Quarto silently falls back to 96-dpi PNG. Set the inline format directly.
try:
    from matplotlib_inline.backend_inline import set_matplotlib_formats
    set_matplotlib_formats("svg")
except Exception:  # pragma: no cover - older stacks still honour Quarto's own setup cell
    pass


def show_table(lab, caption=""):
    df = benchmarks.load_frontier(lab)
    if df.empty:
        display(Markdown("_No rows recorded._")); return
    t = benchmarks.wide(df)
    display(Markdown(benchmarks.to_markdown(t) + (f"\n\n: {caption}" if caption else "")))


def show_series(lab):
    benchmarks.timeseries(benchmarks.load_frontier(lab), lab=lab); plt.show()


def show_overview(lab):
    benchmarks.overview(benchmarks.load_frontier(lab), lab); plt.show()


def show_unbounded(lab):
    benchmarks.unbounded_overview(benchmarks.load_frontier(lab), lab); plt.show()


def show_cross_shared():
    benchmarks.cross_lab_shared(); plt.show()


def show_cross_research():
    benchmarks.cross_lab_research(); plt.show()


def show_cross_unbounded():
    benchmarks.cross_lab_unbounded(); plt.show()


def show_scaling():
    benchmarks.scaling_curves(); plt.show()


def show_cards(lab):
    t = benchmarks.cards(benchmarks.load_frontier(lab))
    t["card"] = t.apply(lambda r: f"[{r['card_title']}]({r['card_url']})" if r["card_url"] else r["card_title"], axis=1)
    t["local copy"] = t["local_copy"].map(lambda f: f"[{f.rsplit('/', 1)[-1]}]({f})" if f else "")
    display(Markdown(benchmarks.to_markdown(t[["model", "card_date", "card", "local copy"]].set_index("model").rename_axis("Model"))))
    om = benchmarks.omitted(lab)
    if len(om):
        items = "; ".join(f"{r.model} ({r.card_date:%b %Y}: better on {r.improved} of {r.shared} shared evaluations)" for r in om.itertuples())
        display(Markdown(f"_Cards left out as dominated, that is no better than an earlier card on all or almost all of the evaluations they share: {items}. Their rows stay in the CSV._"))
