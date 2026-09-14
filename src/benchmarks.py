"""AI R&D benchmark scores reported in closed-lab model and system cards.

`data/ai_rd_benchmarks.csv` is long-form: one row per (lab, model, benchmark, subtask, condition).
`wide()` pivots one lab into the table the page shows: rows are benchmarks, columns are
successive frontier models in card-date order, cells are the reported score text with a
provenance mark.
"""
from __future__ import annotations

import re

import pandas as pd

from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"

LABS = {"gdm": "Google DeepMind", "openai": "OpenAI", "anthropic": "Anthropic"}

# How the number reached this table. `reported` = read from the card itself (or the METR report the
# card cites); `announcement` = read from the lab's launch post, not the card; `snippet` = read from
# a search-result excerpt of the card or of a write-up quoting it; `memory` = recalled without a
# source check. Marks are appended to the cell.
CONFIDENCE_MARK = {"reported": "", "announcement": "*", "snippet": "†", "memory": "‡", "chart": "≈"}

# Row order in the wide tables: AI R&D suites, then research-replication and competition suites,
# then agentic-coding benchmarks, then the lab's own threshold determination.
FAMILY_ORDER = ["re_bench", "ai_rd_suite1", "ai_rd_suite2", "ml_rd_internal", "internal_research_debugging",
                "openai_proof_qa", "mle_bench", "paperbench", "openai_prs", "swe_lancer", "re_interviews",
                "agentic_tasks", "ai_rd_uplift", "metr_external", "swe_bench_verified", "swe_bench_pro",
                "terminal_bench", "agentic_coding_internal", "other", "ml_rd_determination"]


def _hours(text: str):
    """'1h30m' -> 1.5, '6.6h' -> 6.6, '0h30m' -> 0.5; None when the text is not a duration."""
    m = re.fullmatch(r"\s*(\d+)h(\d+)m\s*", text)
    if m:
        return int(m.group(1)) + int(m.group(2)) / 60
    m = re.fullmatch(r"\s*([\d.]+)h\s*", text)
    return float(m.group(1)) if m else None


def load(lab: str | None = None, frontier_only: bool = False) -> pd.DataFrame:
    """`frontier_only` keeps the cards flagged `frontier == yes`: the lab's most capable released
    model at the card date, or a card that moved the lab's frontier. Smaller siblings (Sonnet 4,
    Haiku 4.5, Codex addenda, Gemini Flash-Lite) stay in the CSV. Durations such as '2h17m' (METR
    time horizons) are parsed into hours."""
    df = pd.read_csv(DATA / "ai_rd_benchmarks.csv", dtype=str, keep_default_na=False)
    df["score_num"] = pd.to_numeric(df["score"], errors="coerce")
    hours = df["score"].map(_hours)
    df.loc[df["score_num"].isna() & hours.notna(), "score_num"] = hours
    df["card_date"] = pd.to_datetime(df["card_date"], errors="coerce")
    if lab:
        df = df[df["lab"] == lab]
    if frontier_only:
        df = df[df["frontier"] == "yes"]
    return df.reset_index(drop=True)


QUOTE_CHARS = 180  # a qualitative cell shows this much of the card's wording; the full quote is in the tooltip


def _href(r) -> str:
    """Link target for one row: the local copy of the source (PDF opened at the page the number is
    on) when the document was downloaded into cards/, else the original URL."""
    f = r.get("source_file", "")
    if f:
        return f + (f"#page={r['page']}" if r.get("page", "") and f.endswith(".pdf") else "")
    return r["source_url"]


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def _clip(s: str, n: int = QUOTE_CHARS) -> str:
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:.…") + " …"


def _cell(rows: pd.DataFrame) -> str:
    """One table cell: every row for this benchmark and model, each linked to its source. A numeric
    score is shown as printed; a qualitative result shows the card's own words (the `quote`
    column), clipped, with the full quote and the source page in the tooltip."""
    parts = []
    for _, r in rows.sort_values("conditions").iterrows():
        href = _href(r)
        where = ("p. " + r["page"] + " of " if r.get("page", "") else "") + (r["card_title"] or r["source_url"])
        if r["score"] or not r.get("quote", ""):
            s = r["score_text"] or r["score"]
            if not s:
                continue
            title = where
            text = _esc(s)
        else:
            q = r["quote"]
            title = q + " — " + where
            text = "“" + _esc(_clip(q)) + "”"
        s = f'<a href="{_esc(href)}" title="{_esc(title)}">{text}</a>' if href else text
        if r["conditions"]:
            s = f"{s} ({_esc(r['conditions'])})"
        parts.append(s + CONFIDENCE_MARK.get(r["confidence"], ""))
    return "<br>".join(parts)


def models(df: pd.DataFrame) -> list[str]:
    """Models in card-date order, then by the order they first appear in the file."""
    order = (df.assign(_i=range(len(df)))
               .groupby("model", sort=False)
               .agg(d=("card_date", "min"), i=("_i", "min"))
               .sort_values(["d", "i"]))
    return list(order.index)


def wide(df: pd.DataFrame, families: list[str] | None = None) -> pd.DataFrame:
    """Rows: benchmark (and subtask); columns: models in card order; cells: reported scores."""
    if families:
        df = df[df["family"].isin(families)]
    df = df.copy()
    df["row"] = df.apply(lambda r: f"{r['benchmark']}: {r['subtask']}" if r["subtask"] else r["benchmark"], axis=1)
    # Rows grouped by family (AI R&D suites first, coding benchmarks after, the lab's threshold
    # determination last), then by first appearance in the file (the CSV is written in card order).
    rank = {f: i for i, f in enumerate(FAMILY_ORDER)}
    df["_fam"] = df["family"].map(lambda f: rank.get(f, len(FAMILY_ORDER) - 1))
    df["_pos"] = range(len(df))
    row_order = list(df.sort_values(["_fam", "_pos"]).drop_duplicates("row")["row"])
    cols = models(df)
    out = pd.DataFrame("", index=row_order, columns=cols)
    for (row, model), g in df.groupby(["row", "model"], sort=False):
        out.loc[row, model] = _cell(g)
    out.index.name = "Benchmark"
    return out


def cards(df: pd.DataFrame) -> pd.DataFrame:
    """One line per model: card date, title, URL."""
    files = dict(zip(df["source_url"], df.get("source_file", pd.Series("", index=df.index))))
    t = (df.groupby("model", sort=False)
           .agg(card_date=("card_date", "min"), card_title=("card_title", "first"), card_url=("card_url", "first"))
           .reset_index())
    t["local_copy"] = t["card_url"].map(lambda u: files.get(u, "") or "")
    t = t.sort_values("card_date")
    t["card_date"] = t["card_date"].dt.strftime("%Y-%m")
    return t.reset_index(drop=True)


def to_markdown(t: pd.DataFrame) -> str:
    """GitHub-style table without the `tabulate` dependency; header cells wrap the model names."""
    cols = [t.index.name or ""] + list(t.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for idx, row in t.iterrows():
        cells = [str(idx)] + [str(v) for v in row.tolist()]
        lines.append("| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |")
    return "\n".join(lines)


# ----------------------------------------------------------------------------- time series
import textwrap

import matplotlib.pyplot as plt
import numpy as np

from src import plots


def numeric_series(df: pd.DataFrame) -> pd.DataFrame:
    """Rows with a numeric score, one series key per benchmark (+ subtask)."""
    d = df[df["score_num"].notna() & df["card_date"].notna()].copy()

    def key(r):
        s = f"{r['benchmark']}: {r['subtask']}" if r["subtask"] else r["benchmark"]
        # Terminal-Bench changed version several times; each version is its own series.
        m = re.search(r"\bv\d(?:\.\d)?", r["conditions"]) if r["family"] == "terminal_bench" else None
        if m:
            s += f" {m.group(0)}"
        return s
    d["series"] = d.apply(key, axis=1)
    # An internal task rescaled between cards is split at the known break (see SCALE_BREAKS).
    for series, (cut, lo_label, hi_label) in SCALE_BREAKS.items():
        m = d["series"] == series
        d.loc[m, "series"] = d.loc[m, "score_num"].map(lambda v: f"{series} ({hi_label if v >= cut else lo_label})")
    # A benchmark reported in two different units (percent uplift vs a multiple) is two series.
    d["_unit"] = d["metric"].map(_unit)
    d["series"] = d["series"] + d.groupby("series")["_unit"].transform(
        lambda u: u.map(lambda v: "" if u.nunique() == 1 else f" [{v}]"))
    return d


# Series whose scores are not comparable across a card boundary: (cutoff, label below, label at or above).
# Anthropic's quadruped task was re-normalised between Sonnet 4.5 (threshold 1.0) and Opus 4.5 (threshold 12).
SCALE_BREAKS = {
    "Internal AI Research Evaluation Suite 1: Quadruped RL": (5, "threshold 1 scale", "threshold 12 scale"),
}


def _unit(metric: str) -> str:
    m = metric.lower()
    if "%" in m or "percent" in m:
        return "percent"
    if "0 to 1" in m:
        return "fraction"
    if "speedup" in m or "multiple" in m or "acceleration" in m or m.endswith(" x"):
        return "multiple"
    return "score"


def _short(model: str) -> str:
    for p in ("Claude ", "Gemini ", "OpenAI "):
        model = model.replace(p, "")
    return model.replace(" (Oct 2024)", " Oct24").replace(" Thinking", "")


def timeseries(df: pd.DataFrame, title: str | None = None, ncols: int = 3, min_points: int = 2, lab: str | None = None):
    """Small multiples: one panel per benchmark series with >= min_points numeric scores.

    Within a panel the lowest score per model (the base setting, e.g. no parallel compute) is
    joined by a line; other conditions for the same model are hollow markers. Points from
    rows not yet checked against the card (snippet or memory) are drawn with a lighter fill.
    Speedup-style series spanning more than 20x use a log y-axis."""
    plots.style()
    d = numeric_series(df)
    lab = lab or (df["lab"].iloc[0] if len(df) else None)
    meta = series_meta()
    rank = {f: i for i, f in enumerate(FAMILY_ORDER)}
    keep = [s for s, g in d.groupby("series") if g["model"].nunique() >= min_points]
    order = (d[d["series"].isin(keep)].groupby("series")
               .agg(fam=("family", lambda x: rank.get(x.iloc[0], 99)), t=("card_date", "min"))
               .sort_values(["fam", "t"]).index.tolist())
    if not order:
        fig, ax = plt.subplots(figsize=(8, 2)); plots._empty(ax, "No series with two or more numeric scores"); return fig
    nrows = int(np.ceil(len(order) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.4 * ncols, 2.8 * nrows), squeeze=False, sharex=True)
    x0, x1 = d["card_date"].min(), d["card_date"].max()
    latest_card = df["card_date"].max()
    pad = pd.Timedelta(days=45)
    for ax, s in zip(axes.flat, order):
        g = d[d["series"] == s].sort_values("card_date")
        base = g.loc[g.groupby("model")["score_num"].idxmin()].sort_values("card_date")
        extra = g.drop(base.index)
        c = plots.RUN_COLORS["final"]
        m = meta_for(meta, lab, s)
        ax.plot(base["card_date"], base["score_num"], color=c, lw=1.5, zorder=2)
        verified = base["confidence"].isin(["reported", "announcement"])
        chart = base["confidence"] == "chart"
        ax.scatter(base["card_date"][verified], base["score_num"][verified], s=28, c=c, zorder=3,
                   edgecolors=plots.SURFACE, linewidths=1)
        ax.scatter(base["card_date"][~verified & ~chart], base["score_num"][~verified & ~chart], s=28, c="#a9c8ee", zorder=3,
                   edgecolors=c, linewidths=1)
        ax.scatter(base["card_date"][chart], base["score_num"][chart], s=30, facecolors=plots.SURFACE, zorder=3,
                   edgecolors=c, linewidths=1.3)
        if not extra.empty:
            ax.scatter(extra["card_date"], extra["score_num"], s=26, facecolors="none", edgecolors=c, linewidths=1.2, zorder=3)
        _retire_mark(ax, m, base["card_date"].iloc[-1], base["score_num"].iloc[-1], latest_card)
        for i, (_, r) in enumerate(base.iterrows()):
            up = i % 2 == 0
            ax.annotate(_short(r["model"]), (r["card_date"], r["score_num"]), xytext=(0, 6 if up else -6),
                        textcoords="offset points", ha="center", va="bottom" if up else "top",
                        fontsize=6.5, color=plots.INK2)
        ptitle = re.sub(r" \[.*\]$", "", s)
        ax.set_title("\n".join(textwrap.wrap(ptitle, 40)[:2]), fontsize=8.5)
        metric = g["metric"].iloc[0]
        ax.set_ylabel(textwrap.fill(metric, 22), fontsize=7)
        lo, hi = base["score_num"].min(), base["score_num"].max()
        refs = [v for v in ([m["human_ref"], m["threshold"]] if m is not None else []) if pd.notna(v)]
        if m is not None and pd.notna(m["ceiling"]):
            # Bounded metric: show the whole range so saturation is visible.
            ax.set_ylim(0, m["ceiling"] * 1.06)
            ax.axhline(m["ceiling"], color=plots.INK2, lw=0.8, zorder=1)
        elif lo > 0 and hi / lo > 20:
            ax.set_yscale("log")
            if refs:
                ax.set_ylim(min(lo, *refs) / 1.6, max(hi, *refs) * 1.9)
        else:
            top = max([hi] + refs) * 1.3
            ax.set_ylim(0 if lo >= 0 else None, top)
        ax.set_xlim(x0 - pad, x1 + pad)
        _ref_lines(ax, m, x0, x1)
        ax.tick_params(labelsize=7.5)
    for ax in axes.flat[len(order):]:
        ax.axis("off")
    for ax in axes[-1]:
        ax.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(bymonth=[1, 7]))
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b\n%Y"))
    if title:
        fig.suptitle(title, x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------------- ceilings and overview
CATEGORY_COLORS = {"research": "#2a78d6", "swe": "#eb6834", "terminal": "#1baf7a", "knowledge": "#eda100", "external": "#4a3aa7"}
CATEGORY_LABELS = {"research": "AI research tasks", "swe": "Software engineering", "terminal": "Terminal and agentic",
                   "knowledge": "Knowledge", "external": "External (METR)"}
HUMAN_REF_COLOR = "#c8322b"
_SHORT = [("Internal AI R&D acceleration measure: CoBench (internal root-cause diagnosis on historical Anthropic infrastructure)", "CoBench"),
          ("Internal AI Research Evaluation Suite 1: ", "Suite 1 "), ("Internal AI Research Evaluation Suite 2", "Suite 2"),
          ("OpenAI Research Engineer interviews: ", "RE interview "), ("MLE-bench: ", ""), ("PaperBench: ", ""),
          ("SWE-bench Verified: ", "SWE-V "), ("SWE-bench Verified", "SWE-bench Verified"), (" (RSP checkpoint)", ""),
          ("GRB (GDM internal research engineering benchmark)", "GRB (internal)"), ("SWE-Lancer IC SWE Diamond", "SWE-Lancer Diamond"),
          ("Agentic tasks (autonomy suite)", "Agentic tasks"), ("Internal agentic coding evaluation", "Internal agentic coding"),
          ("FrontierBench v0.1 (Terminal-Bench successor)", "FrontierBench v0.1"), ("Internal Research Debugging Eval", "Research debugging"),
          (" (75 competitions, AIDE)", " full (pass@10)"), ("MLE-Bench Revised", "MLE-bench revised"),
          ("RE-Bench (METR): 4-task modified subset run by Anthropic", "RE-Bench 4-task subset (Anthropic run)"),
          ("METR external evaluation: 50% time horizon", "METR 50% time horizon"),
          ("Internal AI R&D productivity survey", "Staff productivity survey"),
          ("METR data deduplication (RSP checkpoint)", "METR data dedup"),
          ("METR general autonomy time horizon", "METR autonomy time horizon")]


def series_meta() -> pd.DataFrame:
    m = pd.read_csv(DATA / "ai_rd_benchmark_series.csv", dtype=str, keep_default_na=False)
    for c in ["ceiling", "human_ref", "threshold"]:
        m[c] = pd.to_numeric(m[c], errors="coerce")
    m["deprecated_date"] = pd.to_datetime(m["deprecated_date"], errors="coerce")
    return m.set_index(["lab", "series"])


def _retire_mark(ax, m, last_x, last_y, latest_card):
    """Black cross on the last reported value when later cards stop reporting the series: either the
    series metadata records a retirement, or the last value predates the lab's newest card."""
    # A documented retirement counts only if it comes at or after the last value: a version split
    # (Terminal-Bench v4.0) inherits the base series' metadata, whose retirement date is the
    # earlier version's.
    dep = m.get("deprecated_date", pd.NaT) if m is not None else pd.NaT
    documented = pd.notna(dep) and pd.Timestamp(dep) >= pd.Timestamp(last_x)
    if not documented and not (latest_card is not None and last_x < latest_card):
        return False
    ax.scatter([last_x], [last_y], marker="x", s=46, c=plots.INK, linewidths=1.5, zorder=5)
    return True


def meta_for(meta: pd.DataFrame, lab: str, series: str):
    """Exact series match, else the series without its version / scale / unit suffix."""
    for key in (series, re.sub(r" (v\d(?:\.\d)?|\[.*\]|\(.*scale\))$", "", series).strip(),
                re.sub(r" (v\d(?:\.\d)?|\[.*\])$", "", re.sub(r" \(.*scale\)", "", series)).strip()):
        if (lab, key) in meta.index:
            return meta.loc[(lab, key)]
    return None


def short_name(series: str) -> str:
    for a, b in _SHORT:
        series = series.replace(a, b)
    return re.sub(r" \[.*\]$", "", series)


def _ref_lines(ax, m, x0, x1):
    """Human reference (red dotted) and rule-out threshold (grey dashed) with right-hand labels."""
    if m is None:
        return
    if pd.notna(m["human_ref"]):
        ax.axhline(m["human_ref"], color=HUMAN_REF_COLOR, ls=(0, (1.5, 2.5)), lw=1.2, zorder=1)
        ax.annotate(m["human_ref_label"], (0.01, m["human_ref"]), xycoords=("axes fraction", "data"), xytext=(0, -2),
                    textcoords="offset points", ha="left", va="top", fontsize=6.3, color=HUMAN_REF_COLOR)
    if pd.notna(m["threshold"]):
        ax.axhline(m["threshold"], color=plots.MUTED, ls=(0, (4, 3)), lw=1, zorder=1)
        ax.annotate(m["threshold_label"], (0.01, m["threshold"]), xycoords=("axes fraction", "data"), xytext=(0, -2),
                    textcoords="offset points", ha="left", va="top", fontsize=6.3, color=plots.INK2)


def _card_labels(ax, df, x0, x1):
    """Model names above the ceiling at their card dates, pushed apart so they stay legible."""
    cards = (df[df["card_date"].notna()].groupby("model")["card_date"].min().sort_values())
    names = [_short(m) for m in cards.index]
    xs = [pd.Timestamp(v).value for v in cards.values]
    lo, hi = pd.Timestamp(x0).value, pd.Timestamp(x1).value
    gap = (hi - lo) * 0.021
    pos = list(xs)
    for i in range(1, len(pos)):
        if pos[i] - pos[i - 1] < gap:
            pos[i] = pos[i - 1] + gap
    for xd, xp, name in zip(xs, pos, names):
        xd, xp = pd.Timestamp(xd), pd.Timestamp(xp)
        ax.axvline(xd, color=plots.GRID, lw=0.8, zorder=0)
        ax.plot([xd, xp], [100, 104], color=plots.AXIS, lw=0.5, zorder=1, clip_on=False)
        ax.annotate(name, (xp, 104), xytext=(0, 2), textcoords="offset points", rotation=90, ha="center",
                    va="bottom", fontsize=6.3, color=plots.INK2, annotation_clip=False)


def _chart_marks(ax, b: pd.DataFrame, ycol: str, colour: str) -> int:
    """Redraw the points read off a chart (confidence `chart`) as hollow markers; returns how many."""
    ch = b["confidence"] == "chart"
    if ch.any():
        ax.scatter(b["card_date"][ch], b[ycol][ch], s=24, facecolors=plots.SURFACE, edgecolors=colour, linewidths=1.3, zorder=4)
    return int(ch.sum())


CHART_LEGEND = "hollow: read off a chart in the card (no printed value)"


def overview(df: pd.DataFrame, lab: str, title: str | None = None, min_points: int = 2):
    """Every bounded series of one lab on a single 0 to 100 percent axis, as percent of its ceiling.

    Colour is the benchmark category (fixed slots); identity is the label at each line's last
    point. The ceiling is the top of the axis. Lower-is-better and unbounded series are excluded
    (see `overview` in data/ai_rd_benchmark_series.csv)."""
    plots.style()
    meta = series_meta()
    d = numeric_series(df)
    rows = []
    for s, g in d.groupby("series"):
        m = meta_for(meta, lab, s)
        if m is None or m["overview"] != "yes" or pd.isna(m["ceiling"]) or m["direction"] != "higher":
            continue
        base = g.loc[g.groupby("model")["score_num"].idxmin()].sort_values("card_date")
        if base["model"].nunique() < min_points:
            continue
        base = base.assign(pct=base["score_num"] / m["ceiling"] * 100, category=m["category"], series=s)
        rows.append((base, m))
    fig, ax = plt.subplots(figsize=(10, 6.6))
    if not rows:
        plots._empty(ax, "No bounded series with two or more points"); return fig
    allb = pd.concat([b for b, _ in rows])
    x0, x1 = allb["card_date"].min(), allb["card_date"].max()
    latest_card = df["card_date"].max()
    retired = charted = 0
    span = (x1 - x0).days or 1
    ax.axhline(100, color=plots.INK2, lw=1, zorder=1)
    ax.annotate("ceiling", (x0, 100), xytext=(2, -9), textcoords="offset points", fontsize=7, color=plots.INK2)
    ends = []
    for b, m in sorted(rows, key=lambda bm: bm[0]["card_date"].min()):
        c = CATEGORY_COLORS[b["category"].iloc[0]]
        ax.plot(b["card_date"], b["pct"], color=c, lw=1.6, alpha=0.9, zorder=2)
        ax.scatter(b["card_date"], b["pct"], s=16, c=c, edgecolors=plots.SURFACE, linewidths=0.8, zorder=3)
        charted += _chart_marks(ax, b, "pct", c)
        last = b.iloc[-1]
        if _retire_mark(ax, m, last["card_date"], last["pct"], latest_card):
            retired += 1
        ends.append((last["card_date"], last["pct"], short_name(b["series"].iloc[0]), c))
    # Right-hand labels, nudged apart so they do not overlap.
    ends.sort(key=lambda e: e[1])
    ys = [e[1] for e in ends]
    gap = 3.6
    for i in range(1, len(ys)):
        if ys[i] - ys[i - 1] < gap:
            ys[i] = ys[i - 1] + gap
    over = ys[-1] - 104 if ys and ys[-1] > 104 else 0
    ys = [y - over for y in ys]
    xend = x1 + pd.Timedelta(days=45)
    xlab = x1 + pd.Timedelta(days=int(span * 0.07))
    for (xd, y, name, c), yl in zip(ends, ys):
        ax.plot([xd, xlab], [y, yl], color=c, lw=0.6, alpha=0.6, zorder=1, clip_on=False)
        ax.annotate(name, (xlab, yl), xytext=(3, 0), textcoords="offset points", va="center", fontsize=6.8,
                    color=plots.INK2, annotation_clip=False)
    ax.set_ylim(0, 108)
    ax.set_xlim(x0 - pd.Timedelta(days=30), xend)
    ax.set_ylabel("Score as percent of the benchmark ceiling")
    ax.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %Y"))
    handles = [plt.Line2D([], [], color=CATEGORY_COLORS[k], lw=2, label=CATEGORY_LABELS[k])
               for k in CATEGORY_COLORS if k in set(allb["category"])]
    if retired:
        handles.append(plt.Line2D([], [], color=plots.INK, marker="x", ls="none", markersize=7, markeredgewidth=1.4,
                                  label="last reported value; later cards drop it"))
    if charted:
        handles.append(plt.Line2D([], [], color=plots.INK2, marker="o", ls="none", markersize=6, markerfacecolor=plots.SURFACE,
                                  markeredgewidth=1.3, label=CHART_LEGEND))
    _card_labels(ax, df, x0, x1)
    ax.legend(handles=handles, loc="lower left", fontsize=8, title=None)
    ax.set_title(title or f"{LABS.get(lab, lab)}: every bounded AI R&D evaluation, as percent of its ceiling", pad=84)
    fig.subplots_adjust(left=0.07, right=0.66, top=0.8, bottom=0.08)
    return fig


# ----------------------------------------------------------------------------- unbounded metrics, per lab
def _multiple(y, _pos=None):
    return f"{y:g}\u00d7"


def _unbounded_rows(d: pd.DataFrame, lab: str, meta: pd.DataFrame) -> list:
    """(series, points with a `ratio` column, meta, what 1x means, indexed?) for every unbounded
    series of one lab in `d` (the output of `numeric_series`). A series with a card-stated human
    reference is divided by it (reference divided by score when lower is better); one without is
    indexed to its first reported value."""
    rows = []
    for s, g in d[d["lab"] == lab].groupby("series"):
        m = meta_for(meta, lab, s)
        if m is None or pd.notna(m["ceiling"]):
            continue
        lower = m["direction"] == "lower"
        pick = "idxmax" if lower else "idxmin"
        base = g.loc[getattr(g.groupby("model")["score_num"], pick)()].sort_values("card_date")
        if pd.notna(m["human_ref"]):
            ratio = (m["human_ref"] / base["score_num"]) if lower else (base["score_num"] / m["human_ref"])
            what = f"1\u00d7 = {m['human_ref']:g}" + (f", {m['human_time']}" if m["human_time"] else "")
            indexed = False
        else:
            first = base["score_num"].iloc[0]
            if first <= 0:
                continue
            ratio = (first / base["score_num"]) if lower else (base["score_num"] / first)
            what = f"indexed to {_short(base['model'].iloc[0])} = {first:g}"
            indexed = True
        rows.append((s, base.assign(ratio=ratio.values), m, what, indexed))
    return rows


def _end_labels_log(ax, ends, lo, hi, x0, x1, gap_frac: float = 0.036):
    """Right-hand labels for a log axis: (x, y, text, colour) per line end, nudged apart in log space."""
    ends = sorted(ends, key=lambda e: e[1])
    ys = [np.log10(e[1]) for e in ends]
    gap = (np.log10(hi) - np.log10(lo)) * gap_frac
    for i in range(1, len(ys)):
        if ys[i] - ys[i - 1] < gap:
            ys[i] = ys[i - 1] + gap
    top = np.log10(hi) - gap
    over = ys[-1] - top if ys and ys[-1] > top else 0
    ys = [y - over for y in ys]
    span = (x1 - x0).days or 1
    xlab = x1 + pd.Timedelta(days=int(span * 0.07))
    for (xd, y, name, c), yl in zip(ends, ys):
        ax.plot([xd, xlab], [y, 10 ** yl], color=c, lw=0.6, alpha=0.6, zorder=1, clip_on=False)
        ax.annotate(name, (xlab, 10 ** yl), xytext=(3, 0), textcoords="offset points", va="center", fontsize=6.8,
                    color=plots.INK2, annotation_clip=False)


def unbounded_overview(df: pd.DataFrame, lab: str, title: str | None = None):
    """One lab's unbounded metrics (no ceiling) on a log axis of multiples, in the bounded
    overview's style. A series with a card-stated human reference is divided by it (reference
    divided by score when lower is better), so 1x is the reference reached; a series without one is
    indexed to its first reported value and drawn dashed. Colour is the benchmark category; the
    label at each line's end names the series and what 1x means for it."""
    plots.style()
    meta = series_meta()
    d = numeric_series(df)
    latest_card = df["card_date"].max()
    rows = _unbounded_rows(d, lab, meta)
    fig, ax = plt.subplots(figsize=(10, 6.6))
    if not rows:
        plots._empty(ax, "No unbounded series recorded"); return fig
    ax.axhline(1, color=HUMAN_REF_COLOR, ls=(0, (1.5, 2.5)), lw=1.4, zorder=1)
    ends = []
    retired = 0
    for s, b, m, what, indexed in sorted(rows, key=lambda r: r[1]["card_date"].min()):
        c = CATEGORY_COLORS.get(m["category"], plots.MUTED)
        ax.plot(b["card_date"], b["ratio"], color=c, lw=1.6, ls=(0, (3, 2)) if indexed else "-", zorder=2)
        ax.scatter(b["card_date"], b["ratio"], s=16, c=c, edgecolors=plots.SURFACE, linewidths=0.8, zorder=3)
        last = b.iloc[-1]
        if _retire_mark(ax, m, last["card_date"], last["ratio"], latest_card):
            retired += 1
        ends.append((last["card_date"], float(last["ratio"]), f"{short_name(s)} ({what})", c))
    allr = pd.concat([b["ratio"] for _, b, _, _, _ in rows])
    x0, x1 = d["card_date"].min(), d["card_date"].max()
    lo, hi = min(allr.min() / 1.8, 0.5), max(allr.max() * 2.5, 2)
    ax.set_yscale("log"); ax.set_ylim(lo, hi)
    ax.yaxis.set_major_formatter(plt.matplotlib.ticker.FuncFormatter(_multiple))
    ax.yaxis.set_minor_formatter(plt.matplotlib.ticker.NullFormatter())
    ax.annotate("human reference reached (1\u00d7)", (x0, 1), xytext=(2, -9), textcoords="offset points", fontsize=7,
                color=HUMAN_REF_COLOR)
    _end_labels_log(ax, ends, lo, hi, x0, x1)
    ax.set_xlim(x0 - pd.Timedelta(days=30), x1 + pd.Timedelta(days=45))
    ax.set_ylabel("Score as a multiple (log)")
    ax.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %Y"))
    present = {m["category"] for _, _, m, _, _ in rows}
    handles = [plt.Line2D([], [], color=CATEGORY_COLORS[k], lw=2, label=CATEGORY_LABELS[k])
               for k in CATEGORY_COLORS if k in present]
    handles.append(plt.Line2D([], [], color=plots.INK2, lw=1.6, label="solid: 1\u00d7 = card's human reference"))
    handles.append(plt.Line2D([], [], color=plots.INK2, lw=1.6, ls=(0, (3, 2)), label="dashed: no human reference; 1\u00d7 = first card"))
    if retired:
        handles.append(plt.Line2D([], [], color=plots.INK, marker="x", ls="none", markersize=7, markeredgewidth=1.4,
                                  label="last reported value; later cards drop it"))
    ax.legend(handles=handles, loc="lower left", fontsize=7.5)
    # Card names above the plot, as in the bounded overview (anchored just above the top of the axis).
    _card_labels_log(ax, df, x0, x1, hi)
    ax.set_title(title or f"{LABS.get(lab, lab)}: every unbounded AI R&D evaluation, as a multiple", pad=84)
    fig.subplots_adjust(left=0.07, right=0.66, top=0.8, bottom=0.08)
    return fig


def _card_labels_log(ax, df, x0, x1, ytop):
    cards = (df[df["card_date"].notna()].groupby("model")["card_date"].min().sort_values())
    names = [_short(m) for m in cards.index]
    xs = [pd.Timestamp(v).value for v in cards.values]
    lo, hi = pd.Timestamp(x0).value, pd.Timestamp(x1).value
    gap = (hi - lo) * 0.021
    pos = list(xs)
    for i in range(1, len(pos)):
        if pos[i] - pos[i - 1] < gap:
            pos[i] = pos[i - 1] + gap
    for xd, xp, name in zip(xs, pos, names):
        xd, xp = pd.Timestamp(xd), pd.Timestamp(xp)
        ax.axvline(xd, color=plots.GRID, lw=0.8, zorder=0)
        ax.plot([xd, xp], [ytop, ytop * 1.15], color=plots.AXIS, lw=0.5, zorder=1, clip_on=False)
        ax.annotate(name, (xp, ytop * 1.15), xytext=(0, 2), textcoords="offset points", rotation=90, ha="center",
                    va="bottom", fontsize=6.3, color=plots.INK2, annotation_clip=False)


# ----------------------------------------------------------------------------- evaluation frontier
DOMINATED_MIN_SHARED = 3      # need this many shared evaluations to judge a card
DOMINATED_MAX_IMPROVED = 0.25  # improving on at most this share of them = dominated


def dominance(df: pd.DataFrame, lab: str) -> pd.DataFrame:
    """For each card in date order: how many evaluations it shares with earlier cards, how many of
    those it improves on (base condition, direction-aware), and whether it counts as dominated.
    A card that is worse or equal on all but a quarter of the evaluations it shares with earlier
    cards adds no frontier information and is left out of the figures and tables."""
    meta = series_meta()
    d = numeric_series(df)
    if d.empty:
        return pd.DataFrame(columns=["model", "card_date", "shared", "improved", "new", "dominated"])
    d["dir"] = d["series"].map(lambda s: (lambda m: m["direction"] if m is not None else "higher")(meta_for(meta, lab, s)))
    base = (d.groupby(["model", "series", "dir"])["score_num"].min().reset_index()
              .merge(d.groupby("model")["card_date"].min().rename("card_date"), on="model"))
    best: dict[str, float] = {}
    out = []
    for model in base.sort_values("card_date").drop_duplicates("model")["model"]:
        rows = base[base["model"] == model]
        shared = improved = new = 0
        upd = []
        for _, r in rows.iterrows():
            v = r["score_num"] if r["dir"] == "higher" else -r["score_num"]
            if r["series"] in best:
                shared += 1
                improved += int(v > best[r["series"]])
            else:
                new += 1
            upd.append((r["series"], v))
        for s, v in upd:
            best[s] = max(best.get(s, -np.inf), v)
        dominated = shared >= DOMINATED_MIN_SHARED and improved / shared <= DOMINATED_MAX_IMPROVED
        out.append(dict(model=model, card_date=rows["card_date"].iloc[0], shared=shared, improved=improved,
                        new=new, dominated=dominated))
    return pd.DataFrame(out)


def frontier(df: pd.DataFrame, lab: str) -> pd.DataFrame:
    """Rows of the cards that are not dominated (see `dominance`)."""
    dom = dominance(df, lab)
    drop = set(dom.loc[dom["dominated"], "model"])
    return df[~df["model"].isin(drop)].reset_index(drop=True)


def load_frontier(lab: str | None = None) -> pd.DataFrame:
    """Frontier-flagged cards minus the dominated ones, for one lab or all labs."""
    if lab:
        return frontier(load(lab, frontier_only=True), lab)
    return pd.concat([frontier(load(l, frontier_only=True), l) for l in LABS], ignore_index=True)


def omitted(lab: str) -> pd.DataFrame:
    dom = dominance(load(lab, frontier_only=True), lab)
    return dom[dom["dominated"]].reset_index(drop=True)


# ----------------------------------------------------------------------------- across the three labs
LAB_COLORS = {"openai": "#2a78d6", "anthropic": "#eb6834", "gdm": "#1baf7a"}
LAB_ORDER = ["openai", "anthropic", "gdm"]

# Benchmarks more than one lab reports, as (panel title, {lab: regex on the series name}, ceiling or None,
# note). Versions and subsets are drawn as separate segments in the lab's colour.
SHARED_PANELS = [
    ("SWE-bench Verified", {l: r"^SWE-bench Verified$" for l in LAB_ORDER}, 100, "477-problem subset at OpenAI"),
    ("SWE-Bench Pro", {l: r"^SWE-Bench Pro$" for l in LAB_ORDER}, 100, ""),
    ("Terminal-Bench, every version", {l: r"^Terminal-Bench(?: v\d(?:\.\d)?)?$" for l in LAB_ORDER}, 100,
     "a segment per version; OpenAI values are launch-post figures"),
    ("MLE-bench, different subsets", {"openai": r"^MLE-bench: ", "gdm": r"^MLE-Bench$"}, 100,
     "OpenAI: 75 competitions pass@10, then 30 pass@1, then 72 revised; GDM: medal rate"),
    ("RE-Bench (METR), human-normalized", {"gdm": r"^RE-Bench \(METR\): human-normalized average$",
                                          "anthropic": r"^RE-Bench \(METR\): 4-task"}, None,
     "GDM: 5 of 7 tasks, 32 h budget; Anthropic: 4 modified tasks. 1.0 = best human 8-hour attempt"),
]


_SEGMENT_TAGS = {"MLE-bench: MLE-bench (75 competitions, AIDE)": "75 comp., pass@10",
                 "MLE-bench: MLE-bench-30": "30 subset", "MLE-bench: MLE-Bench Revised": "revised (72)"}


def load_all_frontier() -> pd.DataFrame:
    return pd.concat([load_frontier(lab) for lab in LAB_ORDER], ignore_index=True)


def _series_by_lab(df: pd.DataFrame) -> pd.DataFrame:
    d = numeric_series(df)
    return d.loc[d.groupby(["lab", "series", "model"])["score_num"].idxmin()].sort_values("card_date")


def cross_lab_shared(df: pd.DataFrame | None = None, ncols: int = 3):
    """Benchmarks reported by more than one lab, one panel each, lines coloured by lab. Bounded
    panels show the full 0 to 100 range; the RE-Bench panel has the human baseline as a red dotted
    line. Conditions differ between labs (subset, scaffold, budget), so read within a panel as
    'who reports what, and where it sits against the ceiling', not as a ranking."""
    plots.style()
    df = load_all_frontier() if df is None else df
    d = _series_by_lab(df)
    nrows = int(np.ceil(len(SHARED_PANELS) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.6 * ncols, 3.1 * nrows), squeeze=False)
    x0, x1 = d["card_date"].min(), d["card_date"].max()
    pad = pd.Timedelta(days=45)
    used = set()
    for ax, (title, pats, ceiling, note) in zip(axes.flat, SHARED_PANELS):
        ymax = 0
        for lab in LAB_ORDER:
            if lab not in pats:
                continue
            g = d[(d["lab"] == lab) & d["series"].str.contains(pats[lab], regex=True)]
            if g.empty:
                continue
            used.add(lab)
            c = LAB_COLORS[lab]
            for s, seg in g.groupby("series", sort=False):
                seg = seg.sort_values("card_date")
                ax.plot(seg["card_date"], seg["score_num"], color=c, lw=1.6, alpha=0.9, zorder=2)
                ax.scatter(seg["card_date"], seg["score_num"], s=16, c=c, edgecolors=plots.SURFACE, linewidths=0.8, zorder=3)
                ymax = max(ymax, seg["score_num"].max())
                if g["series"].nunique() > 1:
                    tag = _SEGMENT_TAGS.get(s) or re.sub(r"^Terminal-Bench ?", "", s) or "v1"
                    ax.annotate(tag, (seg["card_date"].iloc[0], seg["score_num"].iloc[0]), xytext=(3, 4),
                                textcoords="offset points", fontsize=5.8, color=c, ha="left")
        if ceiling:
            ax.axhline(ceiling, color=plots.INK2, lw=0.8, zorder=1)
            ax.set_ylim(0, ceiling * 1.06)
        else:
            ax.axhline(1, color=HUMAN_REF_COLOR, ls=(0, (1.5, 2.5)), lw=1.2, zorder=1)
            ax.annotate("human baseline (1.0)", (0.02, 1), xycoords=("axes fraction", "data"), xytext=(0, -2),
                        textcoords="offset points", va="top", fontsize=6.3, color=HUMAN_REF_COLOR)
            ax.set_ylim(0, max(1.2, ymax * 1.15))
        ax.set_xlim(x0 - pad, x1 + pad)
        ax.set_title(title, fontsize=9)
        if note:  # every panel's lines start low and left, so the top-left corner is free
            ax.text(0.02, 0.93 if ceiling else 0.97, "\n".join(textwrap.wrap(note, 46)), transform=ax.transAxes,
                    fontsize=5.8, color=plots.MUTED, va="top")
        ax.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(bymonth=[1, 7]))
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %y"))
        ax.tick_params(labelsize=7.5)
    for ax in axes.flat[len(SHARED_PANELS):]:
        ax.axis("off")
    handles = [plt.Line2D([], [], color=LAB_COLORS[l], lw=2, label=LABS[l]) for l in LAB_ORDER if l in used]
    spare = axes.flat[len(SHARED_PANELS)] if len(SHARED_PANELS) < axes.size else axes.flat[0]
    spare.legend(handles=handles, loc="center" if spare.axison is False else "lower right", fontsize=8.5,
                 title="Score as the lab reports it", title_fontsize=8)
    fig.suptitle("Benchmarks reported by more than one lab", x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    return fig


def cross_lab_research(df: pd.DataFrame | None = None, min_points: int = 2):
    """Every lab's bounded AI-research evaluations (the `research` category: internal task suites,
    MLE-bench, PaperBench, research Q&A, GRB) on one 0 to 100 percent axis, coloured by lab, with
    the lab's retirement crosses. The picture the three labs share: each internal research
    evaluation climbs toward its ceiling within one to two years and is then replaced."""
    plots.style()
    df = load_all_frontier() if df is None else df
    meta = series_meta()
    d = numeric_series(df)
    rows = []
    for (lab, s), g in d.groupby(["lab", "series"]):
        m = meta_for(meta, lab, s)
        if m is None or m["overview"] != "yes" or m["category"] != "research" or pd.isna(m["ceiling"]) or m["direction"] != "higher":
            continue
        base = g.loc[g.groupby("model")["score_num"].idxmin()].sort_values("card_date")
        if base["model"].nunique() < min_points:
            continue
        rows.append((base.assign(pct=base["score_num"] / m["ceiling"] * 100, lab=lab, series=s), m))
    fig, ax = plt.subplots(figsize=(10, 6.2))
    if not rows:
        plots._empty(ax, "No bounded research series"); return fig
    allb = pd.concat([b for b, _ in rows])
    x0, x1 = allb["card_date"].min(), allb["card_date"].max()
    latest = df.groupby("lab")["card_date"].max()
    span = (x1 - x0).days or 1
    ax.axhline(100, color=plots.INK2, lw=1, zorder=1)
    ax.annotate("ceiling", (x0, 100), xytext=(2, -9), textcoords="offset points", fontsize=7, color=plots.INK2)
    ends, retired, charted = [], 0, 0
    for b, m in sorted(rows, key=lambda bm: bm[0]["card_date"].min()):
        lab = b["lab"].iloc[0]; c = LAB_COLORS[lab]
        ax.plot(b["card_date"], b["pct"], color=c, lw=1.6, alpha=0.9, zorder=2)
        ax.scatter(b["card_date"], b["pct"], s=16, c=c, edgecolors=plots.SURFACE, linewidths=0.8, zorder=3)
        charted += _chart_marks(ax, b, "pct", c)
        last = b.iloc[-1]
        if _retire_mark(ax, m, last["card_date"], last["pct"], latest[lab]):
            retired += 1
        ends.append((last["card_date"], last["pct"], f"{LABS[lab]}: {short_name(b['series'].iloc[0])}", c))
    ends.sort(key=lambda e: e[1])
    ys = [e[1] for e in ends]
    gap = 3.8
    for i in range(1, len(ys)):
        if ys[i] - ys[i - 1] < gap:
            ys[i] = ys[i - 1] + gap
    over = ys[-1] - 104 if ys and ys[-1] > 104 else 0
    ys = [y - over for y in ys]
    xlab = x1 + pd.Timedelta(days=int(span * 0.07))
    for (xd, y, name, c), yl in zip(ends, ys):
        ax.plot([xd, xlab], [y, yl], color=c, lw=0.6, alpha=0.6, zorder=1, clip_on=False)
        ax.annotate(name, (xlab, yl), xytext=(3, 0), textcoords="offset points", va="center", fontsize=6.8,
                    color=plots.INK2, annotation_clip=False)
    ax.set_ylim(0, 108)
    ax.set_xlim(x0 - pd.Timedelta(days=30), x1 + pd.Timedelta(days=45))
    ax.set_ylabel("Score as percent of the benchmark ceiling")
    ax.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %Y"))
    handles = [plt.Line2D([], [], color=LAB_COLORS[l], lw=2, label=LABS[l]) for l in LAB_ORDER if l in set(allb["lab"])]
    if retired:
        handles.append(plt.Line2D([], [], color=plots.INK, marker="x", ls="none", markersize=7, markeredgewidth=1.4,
                                  label="last reported value; the lab's later cards drop it"))
    if charted:
        handles.append(plt.Line2D([], [], color=plots.INK2, marker="o", ls="none", markersize=6, markerfacecolor=plots.SURFACE,
                                  markeredgewidth=1.3, label=CHART_LEGEND))
    ax.legend(handles=handles, loc="lower left", fontsize=8)
    ax.set_title("All three labs: bounded AI-research evaluations, as percent of their ceilings", pad=10)
    fig.subplots_adjust(left=0.07, right=0.66, top=0.92, bottom=0.08)
    return fig


def cross_lab_unbounded(df: pd.DataFrame | None = None):
    """Every lab's unbounded evaluations on one log axis of multiples, coloured by lab. Same
    normalisation as the per-lab figure: solid lines are divided by the card's human reference, so
    1x is the reference reached; dashed lines have no reference and are indexed to their first card.
    Multiples are only comparable within a series, so read this as 'how far past its own human
    reference each lab has pushed', not as a ranking."""
    plots.style()
    df = load_all_frontier() if df is None else df
    meta = series_meta()
    d = numeric_series(df)
    latest = df.groupby("lab")["card_date"].max()
    rows = [(lab, *r) for lab in LAB_ORDER for r in _unbounded_rows(d, lab, meta)]
    fig, ax = plt.subplots(figsize=(10, 6.6))
    if not rows:
        plots._empty(ax, "No unbounded series recorded"); return fig
    ax.axhline(1, color=HUMAN_REF_COLOR, ls=(0, (1.5, 2.5)), lw=1.4, zorder=1)
    ends, retired = [], 0
    for lab, s, b, m, what, indexed in sorted(rows, key=lambda r: r[2]["card_date"].min()):
        c = LAB_COLORS[lab]
        ax.plot(b["card_date"], b["ratio"], color=c, lw=1.6, ls=(0, (3, 2)) if indexed else "-", zorder=2)
        ax.scatter(b["card_date"], b["ratio"], s=16, c=c, edgecolors=plots.SURFACE, linewidths=0.8, zorder=3)
        last = b.iloc[-1]
        if _retire_mark(ax, m, last["card_date"], last["ratio"], latest[lab]):
            retired += 1
        ends.append((last["card_date"], float(last["ratio"]), f"{LABS[lab]}: {short_name(s)} ({what})", c))
    allr = pd.concat([b["ratio"] for _, _, b, _, _, _ in rows])
    x0, x1 = d["card_date"].min(), d["card_date"].max()
    lo, hi = min(allr.min() / 1.8, 0.5), max(allr.max() * 2.5, 2)
    ax.set_yscale("log"); ax.set_ylim(lo, hi)
    ax.yaxis.set_major_formatter(plt.matplotlib.ticker.FuncFormatter(_multiple))
    ax.yaxis.set_minor_formatter(plt.matplotlib.ticker.NullFormatter())
    ax.annotate("human reference reached (1\u00d7)", (x0, 1), xytext=(2, -9), textcoords="offset points", fontsize=7,
                color=HUMAN_REF_COLOR)
    _end_labels_log(ax, ends, lo, hi, x0, x1, gap_frac=0.034)
    ax.set_xlim(x0 - pd.Timedelta(days=30), x1 + pd.Timedelta(days=45))
    ax.set_ylabel("Score as a multiple (log)")
    ax.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %Y"))
    present = {lab for lab, *_ in rows}
    handles = [plt.Line2D([], [], color=LAB_COLORS[l], lw=2, label=LABS[l]) for l in LAB_ORDER if l in present]
    handles.append(plt.Line2D([], [], color=plots.INK2, lw=1.6, label="solid: 1\u00d7 = card's human reference"))
    handles.append(plt.Line2D([], [], color=plots.INK2, lw=1.6, ls=(0, (3, 2)), label="dashed: no human reference; 1\u00d7 = first card"))
    if retired:
        handles.append(plt.Line2D([], [], color=plots.INK, marker="x", ls="none", markersize=7, markeredgewidth=1.4,
                                  label="last reported value; the lab's later cards drop it"))
    ax.legend(handles=handles, loc="lower left", fontsize=7.5)
    ax.set_title("All three labs: unbounded AI R&D evaluations, as multiples of their references", pad=10)
    fig.subplots_adjust(left=0.07, right=0.62, top=0.92, bottom=0.08)
    return fig


# ----------------------------------------------------------------------------- score against budget (OpenAI)
MODEL_COLORS = {"GPT-5.4 Thinking": "#eda100", "GPT-5.5": "#eb6834", "GPT-5.6 Luna": "#a9c8ee", "GPT-5.6 Terra": "#6fa0e0",
                "GPT-5.6 Sol": "#2a78d6", "GPT-6 Astra": "#4a3aa7"}
BUDGET_KINDS = [("API cost", "API cost (USD)"), ("simulated latency", "simulated latency (minutes)"), ("output tokens", "output tokens")]
CURVE_BENCHMARKS = ["Internal Research Debugging Eval", "KernelGen 1P", "NanoGPT", "PostTrainBench Lite"]


def scaling_curves(path: Path | None = None):
    """OpenAI's AI-self-improvement evaluations as the cards draw them: score against the budget an
    agent was given, one line per model. One row per evaluation, one column per budget measure (the
    GPT-5.6 card plots API cost and simulated latency; the GPT-6 Astra card plots output tokens).
    Every point is read off the card's chart (data/ai_rd_scaling_curves.csv), so markers are hollow.
    Axes run to the ceiling so the distance left to 100 percent, and to NanoGPT's best human
    solution, is visible."""
    plots.style()
    meta = series_meta()
    c = pd.read_csv(path or DATA / "ai_rd_scaling_curves.csv")
    fig, axes = plt.subplots(len(CURVE_BENCHMARKS), len(BUDGET_KINDS), figsize=(10.5, 2.75 * len(CURVE_BENCHMARKS)), squeeze=False)
    present = set()
    for i, bench in enumerate(CURVE_BENCHMARKS):
        m = meta_for(meta, "openai", bench)
        for j, (kind, xlabel) in enumerate(BUDGET_KINDS):
            ax = axes[i, j]
            sub = c[(c["benchmark"] == bench) & (c["x_kind"] == kind)]
            if sub.empty:
                ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
                for sp in ax.spines.values():
                    sp.set_visible(False)
                ax.text(0.5, 0.5, "not drawn against\n" + kind + " in the cards", ha="center", va="center", fontsize=7.5, color=plots.MUTED,
                        transform=ax.transAxes)
                continue
            for model, col in MODEL_COLORS.items():
                g = sub[sub["model"] == model].sort_values("x")
                if g.empty:
                    continue
                present.add(model)
                ax.plot(g["x"], g["y"], color=col, lw=1.5, zorder=2)
                ax.scatter(g["x"], g["y"], s=22, facecolors=plots.SURFACE, edgecolors=col, linewidths=1.2, zorder=3)
            ax.axhline(100, color=plots.INK2, lw=0.8, zorder=1)
            if m is not None and pd.notna(m["human_ref"]):
                ax.axhline(m["human_ref"], color=HUMAN_REF_COLOR, ls=(0, (1.5, 2.5)), lw=1.2, zorder=1)
                ax.annotate(m["human_ref_label"], (0.98, m["human_ref"]), xycoords=("axes fraction", "data"), xytext=(0, 2),
                            textcoords="offset points", ha="right", va="bottom", fontsize=6.3, color=HUMAN_REF_COLOR)
            ax.set_ylim(0, 104)
            ax.set_xlim(left=0)
            if kind == "output tokens":
                ax.xaxis.set_major_formatter(plt.matplotlib.ticker.FuncFormatter(lambda v, _p: f"{v/1000:g}K"))
            elif kind == "API cost":
                ax.xaxis.set_major_formatter(plt.matplotlib.ticker.FuncFormatter(lambda v, _p: f"${v:g}"))
            ax.tick_params(labelsize=7.5)
            if i == len(CURVE_BENCHMARKS) - 1 or c[(c["benchmark"] == CURVE_BENCHMARKS[min(i + 1, len(CURVE_BENCHMARKS) - 1)]) & (c["x_kind"] == kind)].empty:
                ax.set_xlabel(xlabel, fontsize=8)
            if j == 0:
                ax.set_ylabel(sub["y_metric"].iloc[0], fontsize=8)
        axes[i, 0].annotate(short_name(bench), (0, 1), xycoords="axes fraction", xytext=(0, 4), textcoords="offset points",
                            fontsize=9.5, fontweight="bold", va="bottom", color=plots.INK)
    for j, (kind, xlabel) in enumerate(BUDGET_KINDS):
        card = "GPT-6 Astra card" if kind == "output tokens" else "GPT-5.6 card"
        axes[0, j].set_title(f"against {xlabel}\n({card})", fontsize=8.5, color=plots.INK2, pad=22, fontweight="normal")
    handles = [plt.Line2D([], [], color=MODEL_COLORS[k], lw=2, label=k) for k in MODEL_COLORS if k in present]
    handles.append(plt.Line2D([], [], color=plots.INK2, marker="o", ls="none", markersize=6, markerfacecolor=plots.SURFACE,
                              markeredgewidth=1.2, label="every point is read off the card's chart"))
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=8, bbox_to_anchor=(0.5, -0.005))
    fig.suptitle("OpenAI: AI self-improvement evaluations, score against budget, by model", x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0.04, 1, 0.965))
    return fig


# ----------------------------------------------------------------------------- RE-Bench by task (Google DeepMind)
REBENCH_RUNS = [("Gemini 2.5 Flash", "45 minutes"), ("Gemini 2.5 Flash", "2 hours"), ("Gemini 2.5 Pro", "45 minutes"), ("Gemini 2.5 Pro", "2 hours"),
                ("Gemini 2.5 Deep Think", "2 hours"), ("Gemini 3 Pro", "2 hours")]


def rebench_tasks(path: Path | None = None):
    """DeepMind's RE-Bench results task by task, as read off the bar charts in the Gemini 2.5 Pro,
    2.5 Deep Think and 3 Pro cards (data/ai_rd_rebench_tasks.csv). One panel per task; each Gemini
    run (model and time budget) is a hollow point in release order, the 8-hour human bar is the red
    dotted line and DeepMind's own 30-minute Claude 3.5 Sonnet run a grey point. Where a run appears
    in more than one card the latest card's reading is used; they agree to about 0.02."""
    plots.style()
    c = pd.read_csv(path or DATA / "ai_rd_rebench_tasks.csv")
    c = c.sort_values("card_date").drop_duplicates(["model", "time_budget", "task"], keep="last")
    tasks = [t for t in ["Optimize a Kernel", "Scaling Law Experiment", "Restricted Architecture MLM", "Optimize LLM Foundry", "Fix Embedding"]
             if t in set(c["task"])]
    fig, axes = plt.subplots(1, len(tasks), figsize=(2.3 * len(tasks), 3.9), sharey=True)
    xs = list(range(len(REBENCH_RUNS)))
    labels = [f"{_short(m)}\n{b.replace(' minutes', ' min').replace(' hours', ' h')}" for m, b in REBENCH_RUNS]
    for ax, task in zip(axes, tasks):
        sub = c[c["task"] == task].set_index(["model", "time_budget"])["normalized_score"]
        ys = [sub.get(run, np.nan) for run in REBENCH_RUNS]
        ok = [i for i, y in enumerate(ys) if pd.notna(y)]
        ax.plot([xs[i] for i in ok], [ys[i] for i in ok], color=LAB_COLORS["gdm"], lw=1.4, zorder=2)
        ax.scatter([xs[i] for i in ok], [ys[i] for i in ok], s=30, facecolors=plots.SURFACE, edgecolors=LAB_COLORS["gdm"], linewidths=1.3, zorder=3)
        human = sub.get(("Human", "8 hours"), np.nan)
        if pd.notna(human):
            ax.axhline(human, color=HUMAN_REF_COLOR, ls=(0, (1.5, 2.5)), lw=1.2, zorder=1)
            ax.annotate(f"human, 8 h ({human:.2f})", (0.02, human), xycoords=("axes fraction", "data"), xytext=(0, 2), textcoords="offset points",
                        va="bottom", fontsize=6.3, color=HUMAN_REF_COLOR)
        claude = sub.get(("Claude 3.5 Sonnet", "30 minutes"), np.nan)
        if pd.notna(claude):
            ax.scatter([-0.8], [claude], s=30, facecolors=plots.SURFACE, edgecolors=plots.MUTED, linewidths=1.3, zorder=3)
            ax.annotate("3.5 Sonnet\n30 min", (-0.8, claude), xytext=(0, 7), textcoords="offset points", ha="center", va="bottom", fontsize=5.8, color=plots.MUTED)
        ax.axhline(1.0, color=plots.AXIS, lw=0.8, zorder=1)
        ax.set_title("\n".join(textwrap.wrap(task, 16)), fontsize=8.5)
        ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=5.8, rotation=90)
        ax.set_xlim(-1.4, len(xs) - 0.5); ax.set_ylim(0, 2.05)
        ax.tick_params(axis="y", labelsize=7.5)
    axes[0].set_ylabel("normalised score (1.0 = human reference solution)", fontsize=7.5)
    handles = [plt.Line2D([], [], color=LAB_COLORS["gdm"], marker="o", markerfacecolor=plots.SURFACE, markeredgewidth=1.3, lw=1.4, markersize=6, label="Gemini run (model, time budget); hollow: read off the card's chart"),
               plt.Line2D([], [], color=HUMAN_REF_COLOR, ls=(0, (1.5, 2.5)), lw=1.2, label="best human 8-hour attempt, as drawn in the card"),
               plt.Line2D([], [], color=plots.MUTED, marker="o", markerfacecolor=plots.SURFACE, markeredgewidth=1.3, ls="none", markersize=6, label="Claude 3.5 Sonnet, 30 minutes, run by DeepMind")]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=7.5, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Google DeepMind: RE-Bench by task, from the bar charts in the Gemini 2.5 Pro, 2.5 Deep Think and 3 Pro cards", x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0.06, 1, 0.94))
    return fig
