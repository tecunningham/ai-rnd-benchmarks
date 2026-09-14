"""Locate every row of data/ai_rd_benchmarks.csv in its downloaded source document.

Fills two columns: `page` (1-based page of the PDF where the benchmark and the score appear
together; blank for web pages and for rows that could not be located) and, for rows without a
numeric score, a candidate `quote` (the card's own sentence). Writes a review table to stdout so
the candidates can be checked by eye before they are accepted into the CSV.

    python scripts/annotate_sources.py --write   # update page/quote in the CSV (keeps hand-edited quotes)
    python scripts/annotate_sources.py           # dry run, print the review table
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ai_rd_benchmarks.csv"
INDEX = ROOT / "cards" / "index.csv"

# Search terms per benchmark (regex, case-insensitive). Subtask names are added automatically.
ALIASES = {
    "AI R&D threshold determination": [r"AI R&D-\d", r"AI R&D threshold", r"automated AI R&D", r"AI R&D capabilit"],
    "Internal AI R&D acceleration measure": [r"acceleration", r"Capabilities Index", r"ECI"],
    "Internal AI R&D productivity survey": [r"productivity", r"survey"],
    "Internal AI Research Evaluation Suite 1": [r"Internal AI research evaluation suite 1", r"Suite 1", r"AI research evaluation"],
    "Internal AI Research Evaluation Suite 2": [r"Internal AI research evaluation suite 2", r"Suite 2"],
    "Internal agentic coding evaluation": [r"agentic coding"],
    "Internal survey: drop-in replacement for an entry-level (L4) researcher": [r"drop-in", r"entry-level", r"L4"],
    "METR data deduplication (RSP checkpoint)": [r"deduplication", r"de-duplication"],
    "METR external evaluation": [r"METR"],
    "METR general autonomy time horizon": [r"time horizon", r"METR"],
    "RE-Bench (METR)": [r"RE-?Bench"],
    "SWE-Bench Pro": [r"SWE-?Bench Pro"],
    "SWE-bench Verified": [r"SWE-?bench Verified", r"SWE-?bench"],
    "Terminal-Bench": [r"Terminal-?Bench"],
    "Terminal-Bench-Science": [r"Terminal-?Bench-?Science"],
    "FrontierBench v0.1 (Terminal-Bench successor)": [r"FrontierBench"],
    "DeepSWE v1.1": [r"DeepSWE"],
    "FrontierCode 1.1 Main": [r"FrontierCode"],
    "GRB (GDM internal research engineering benchmark)": [r"\bGRB\b", r"research engineering benchmark"],
    "ML R&D CCL determination": [r"Machine Learning R&D", r"ML R&D", r"ML R&amp;D"],
    "MLE-Bench": [r"MLE-?Bench"],
    "MLE-bench": [r"MLE-?Bench"],
    "AI self-improvement (earlier: model autonomy) classification": [r"AI Self-improvement", r"Model Autonomy", r"self-improvement"],
    "Agentic tasks (autonomy suite)": [r"Agentic Tasks", r"autonomy"],
    "Internal Research Debugging Eval": [r"research debugging", r"Research Debugging"],
    "KernelGen 1P": [r"KernelGen"],
    "Monorepo-Bench": [r"Monorepo-?Bench"],
    "NanoGPT": [r"NanoGPT"],
    "OpenAI PRs": [r"OpenAI PRs", r"pull request"],
    "OpenAI Research Engineer interviews": [r"Research Engineer interview", r"interview"],
    "OpenAI-Proof Q&A": [r"OpenAI-?Proof"],
    "PaperBench": [r"PaperBench"],
    "PostTrainBench Lite": [r"PostTrainBench"],
    "SWE-Lancer IC SWE Diamond": [r"SWE-?Lancer"],
}


def load_doc(path: Path) -> list[str]:
    """Pages of the extracted text (a web page is one 'page')."""
    txt = path.with_suffix(".txt")
    if not txt.exists():
        return []
    t = txt.read_text()
    if "=== PAGE " in t:
        parts = re.split(r"\n=== PAGE (\d+) ===\n", t)
        pages = {}
        for i in range(1, len(parts), 2):
            pages[int(parts[i])] = parts[i + 1]
        return [pages.get(i + 1, "") for i in range(max(pages))]
    return [t]


LIGATURES = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl"}


def norm(s: str) -> str:
    for k, v in LIGATURES.items():
        s = s.replace(k, v)
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
                  .replace("\xad", "").replace("-\n", "")).strip()


def score_patterns(r) -> list[re.Pattern]:
    pats = []
    for s in {r["score"], r["score_text"]}:
        s = s.strip()
        if not s:
            continue
        m = re.match(r"^-?\d+(\.\d+)?", s)
        if m:
            num = m.group(0)
            pats.append(re.compile(r"(?<![\d.])" + re.escape(num) + r"(?!\d)"))
            if "." in num and num.endswith("0"):
                pats.append(re.compile(r"(?<![\d.])" + re.escape(num.rstrip("0").rstrip(".")) + r"(?!\d)"))
    return pats


def sentences(text: str) -> list[str]:
    t = norm(text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(])", t) if len(s.strip()) > 20]


QUOTE_RE = re.compile(r"(?<![A-Za-z])'(.{20,}?)'(?![A-Za-z])")

# Pages of documents whose benchmark tables are images (no extractable text): file -> page.
PAGE_OVERRIDES = {
    "cards/gdm/gemini-3-pro-model-card.pdf": 5,
    "cards/gdm/gemini-3-1-pro-model-card.pdf": 4, "cards/gdm/gemini-3-flash-model-card.pdf": 4,
    "cards/gdm/gemini-3-5-flash-model-card.pdf": 4, "cards/gdm/gemini-3-6-flash-model-card.pdf": 4,
    "cards/gdm/gemini-3-7-flash-model-card.pdf": 4, "cards/gdm/gemini-3-8-flash-model-card.pdf": 4,
}


def is_toc(pn: str, index: int) -> bool:
    """A table of contents: dotted leaders, or (near the front) a run of section numbers."""
    return len(re.findall(r"(?:\. ){4,}|\.{5,}", pn)) >= 5 or (index < 8 and len(re.findall(r" \d{1,3}(?= \d+(?:\.\d+)* [A-Z]| [A-Z])", pn)) >= 25)


def squash(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def notes_quotes(r) -> list[str]:
    """Verbatim card fragments recorded in single quotes in the notes (and score_text) during
    verification; these are the card's own words and become the `quote` column."""
    out = []
    for q in QUOTE_RE.findall(r["notes"] + " " + r["score_text"]):
        q = norm(q).strip(" .,;:")
        if q and q not in out and not re.match(r"^(was|removed|note|see) ", q):
            out.append(q)
    return out


def find(r, pages: list[str], is_pdf: bool):
    """(page, quote). Page: where a quoted fragment from the notes appears; else where the
    benchmark alias and the score appear together; else the first alias hit; else a per-file
    override for image-only tables. Quote: the notes' verbatim fragments joined with ' … '."""
    aliases = ALIASES.get(r["benchmark"], [re.escape(r["benchmark"])])
    if r["subtask"]:
        aliases = [re.escape(w) for w in re.findall(r"[A-Za-z][A-Za-z-]{3,}", r["subtask"])[:3]] + aliases
    alias_re = re.compile("|".join(aliases), re.I)
    spats = score_patterns(r)
    quotes = notes_quotes(r)
    keys = [squash(q)[:45] for q in quotes if len(squash(q)) >= 18]
    sq_pages = [squash(norm(p)) for p in pages]
    key_pages, alias_num, alias_only = [], [], []
    for i, p in enumerate(pages):
        pn = norm(p)
        has_alias = bool(alias_re.search(pn))
        if any(k in sq_pages[i] for k in keys):
            key_pages.append((i + 1, has_alias))
        if has_alias and not is_toc(pn, i):
            (alias_num if any(sp.search(pn) for sp in spats) else alias_only).append(i + 1)
    # A quoted fragment on a page that also names the benchmark is the surest anchor; a fragment
    # alone can be a generic phrase ('performs on par with ...') that recurs elsewhere in the card.
    keyed = [pg for pg, has_alias in key_pages if has_alias]
    page = (keyed or alias_num or [pg for pg, _ in key_pages] or alias_only or [""])[0]
    if not is_pdf:
        page = ""
    quote = " … ".join(quotes) if not r["score"] else ""
    return page, quote[:600]


MANUAL_QUOTES: dict = {  # (model, benchmark, subtask) -> (verbatim card text, PDF page); rows whose notes carry no quotable fragment
    ("GPT-6 Astra", "PostTrainBench Lite", ""): ("PostTrainBench Lite evaluates an agent's ability to improve an open-source base model on a target benchmark. … The evaluation covers 12 combinations from the full PostTrainBench suite", ""),
    ("Claude Sonnet 4", "AI R&D threshold determination", ""): ("Claude Sonnet 4 does not require ASL-4 protections despite showing improvements over Claude Sonnet 3.7 on several AI research tasks. Claude Sonnet 4 crossed the METR data deduplication threshold (with 27.6% of trials above threshold) and showed improved performance on the SWE-bench Verified hard subset (15.4/42 problems solved), while remaining below threshold. Overall, whereas Claude Sonnet 4 shows capability improvements in select areas, its performance remains well below the thresholds that would warrant ASL-4 protections.", 107),
    ("Claude Opus 4.1", "Internal AI Research Evaluation Suite 2", ""): ("We did not run Internal AI Research Evaluation Suite 2 or the internal model use survey for this incremental release.", 22),
    ("Claude Opus 4.1", "Internal AI R&D productivity survey", ""): ("We did not run Internal AI Research Evaluation Suite 2 or the internal model use survey for this incremental release.", 22),
    ("Claude Opus 4.1", "AI R&D threshold determination", ""): ("Claude Opus 4.1 demonstrates incremental improvements compared to Claude Opus 4, consistent with a model that does not cross the \"notably more capable\" threshold from our RSP. … As stated in Section 3.1 of our RSP: \"If a new or existing model is below the 'notably more capable' standard, no further testing is necessary.\" New RSP evaluations were therefore not required.", 18),
    ("Claude Sonnet 4.5", "Internal AI R&D productivity survey", ""): ("0/7 researchers believed that the model could completely automate the work of a junior ML researcher. … One participant estimated an overall productivity boost of ~100%, and indicated that their workflow was now mainly focused on managing multiple agents. … most of the productivity boost was attributable to Claude Code, and not to the capabilities delta between Claude Opus 4.1 and (early) Claude Sonnet 4.5.", 148),
    ("Claude Haiku 4.5", "AI R&D threshold determination", ""): ("Our evaluations determined that Claude Haiku 4.5 met the ASL-3 rule-out threshold. Our evaluation results showed that Claude Haiku 4.5 remained well below ASL-3 thresholds across all domains of concern.", 7),
    ("Claude Sonnet 4.6", "Internal AI Research Evaluation Suite 2", ""): ("[Table 6.3.1.1.B] AI R&D-4 evaluations: Internal AI Research Evaluation Suite 1 — Can models optimize machine learning code and train smaller models to solve machine learning problems? (Suite 2 is not listed.)", 112),
    ("Claude Sonnet 4.6", "AI R&D threshold determination", ""): ("It performed below or equal to Claude Opus 4.6 on Internal AI Research Evaluation Suite 1, confirming that its capabilities are not higher than Claude Opus 4.6's. … While we do not believe Sonnet 4.6 meets the threshold for AI R&D-4, we find ourselves in a gray zone where clean rule-out is difficult and the margin to the threshold is unclear.", 112),
    ("Claude Mythos Preview", "Internal AI Research Evaluation Suite 1", ""): ("Claude Mythos Preview clears the 4h and 8h thresholds on all tasks, and the 40h threshold on 2/3 of the tasks. … We take the suite's saturation as the expected outcome for a model at this capability level.", 36),
    ("Claude Mythos Preview", "Internal AI R&D acceleration measure", ""): ("On the current pipeline, the slope ratio lands between 1.86× and 4.3× depending on the choice of breakpoint. … The slope measurement tells us that Anthropic's capability trajectory bent upward in the period leading to Claude Mythos Preview. … Our best estimates of the elasticity of progress to researcher output, combined with the observed uplift, yield an overall progress multiplier below 2×.", 44),
    ("Claude Mythos Preview", "METR external evaluation", "External AI R&D testing (METR, Epoch AI and other partners)"): ("Claude Mythos Preview rediscovered 4 of 5 key insights, while Claude Opus 4.6 discovered just 2 of 5 key insights. There was no direct baseline for discovering these insights.", 45),
    ("Claude Opus 4.7", "Internal AI Research Evaluation Suite 2", ""): ("Internal suite 2: Did not run [Table 2.3.4.A] Summary table of AI R&D rule-out automated evals.", 28),
    ("Claude Opus 4.7", "Internal AI R&D productivity survey", ""): ("Because of weaker general capabilities for Claude Opus 4.7 compared to Claude Mythos Preview, we did not run a separate internal survey on this model. … [Mythos Preview Slack poll:] The distribution was wide and the geometric mean was on the order of 4×.", 29),
    ("Claude Opus 4.7", "AI R&D threshold determination", ""): ("The model's capabilities fall between those of Claude Opus 4.6 and Claude Mythos Preview, and it does not advance our capability frontier. … The main reason we have determined that Claude Opus 4.7 does not cross the threshold in question is that 1) We do not see a sustained, 2× speedup, in capabilities over time; and 2) It does not seem close to being able to fully substitute for Research Scientists and Research Engineers", 26),
    ("Claude Opus 4.8", "Internal AI R&D productivity survey", ""): ("We did not run a new internal survey on this model. … All of these shortcomings came from manually flagged issues over a sample of ~5600 sessions using the final Claude Opus 4.8.", 31),
    ("Claude Opus 4.8", "Internal AI R&D acceleration measure", ""): ("Claude Opus 4.8 sits between Claude Opus 4.7 and Claude Mythos Preview based on capabilities measured by the Anthropic ECI (§2.3.4) and does not advance the capability frontier, so both conclusions carry over directly.", 31),
    ("Claude Fable 5 / Mythos 5", "Internal AI R&D productivity survey", ""): ("These are drawn from a sample of 886 day-to-day uses of a nearly-final version of the model. … Cluster: states an unverified guess as fact (41/886) … Cluster: Claude reported work as done or verified when it wasn't (16/886)", 37),
    ("Claude Sonnet 5", "Internal AI R&D productivity survey", ""): ("We did not run a new internal survey on this model. Similarly, we did not compile AECI for Sonnet 5, since it does not advance the frontier.", 25),
    ("Claude Sonnet 5", "AI R&D threshold determination", ""): ("Claude Sonnet 5 does not advance our capability frontier as it performs below Opus 4.7 on all evaluations except for Novel Compiler where it scores higher than Opus 4.7 but well below Claude Mythos 5. … We assess that Claude Sonnet 5 does not cross the automated AI R&D capability threshold.", 26),
    ("Claude Opus 5", "Internal AI R&D productivity survey", ""): ("If Claude Opus 5 represented a practical jump in AI R&D capability larger than its small margin over Mythos 5, we would expect to observe more signs of internal adoption (in our internal use metrics) than we've seen to date.", 32),
    ("Claude Fable 5.1 / Mythos 5.1", "SWE-bench Verified", ""): ("8.2 SWE-bench Pro, Multilingual, and Multimodal … We report three variants, where each score is an average over five trials: SWE-bench Pro … SWE-bench Multilingual … SWE-bench Multimodal", 168),
    ("Claude Fable 5.1 / Mythos 5.1", "Internal AI R&D productivity survey", ""): ("[METR:] For instance, we expect that [Mythos 5.1] likely provides a higher productivity uplift than Mythos Preview.", 41),
    ("Claude Fable 5.1 / Mythos 5.1", "METR external evaluation", "Sunlight and LMCA"): ("However, we still observed [Mythos 5.1] achieving subexpert performance in Sunlight and LMCA.", 40),
    ("Claude Fable 5.1 / Mythos 5.1", "Internal AI Research Evaluation Suite 1", ""): ("Recent models have crossed the highest human baselines for many of the automated task-based AI R&D evaluations described in Section 8.3 of the Claude Opus 4.6 System Card, and results on such tasks are no longer a significant component of our RSP and FCF capability-threshold determinations.", 35),
}


def main(write: bool):
    d = pd.read_csv(DATA, dtype=str, keep_default_na=False)
    idx = pd.read_csv(INDEX, dtype=str, keep_default_na=False)
    files = dict(zip(idx["url"], idx["file"]))
    for c in ["page", "quote", "source_file"]:
        if c not in d.columns:
            d[c] = ""
    docs = {}
    review = []
    for i, r in d.iterrows():
        f = files.get(r["source_url"]) or ""
        d.at[i, "source_file"] = f
        if not f:
            continue
        if f not in docs:
            docs[f] = load_doc(ROOT / f)
        page, quote = find(r, docs[f], f.endswith(".pdf"))
        if not page and f in PAGE_OVERRIDES and r["score"]:
            page = PAGE_OVERRIDES[f]
        manual = MANUAL_QUOTES.get((r["model"], r["benchmark"], r["subtask"]))
        if manual:
            quote, page = manual[0], (manual[1] or page)
        d.at[i, "page"] = str(page) if page else ""
        if not r["score"] and not r["quote"]:      # keep quotes already checked by hand
            d.at[i, "quote_candidate"] = quote
        review.append((i, r["lab"], r["model"], (r["benchmark"] + (": " + r["subtask"] if r["subtask"] else ""))[:60],
                       r["score_text"][:70] or r["score"], page, (quote if not r["score"] else "")[:160]))
    rv = pd.DataFrame(review, columns=["i", "lab", "model", "benchmark", "score_text", "page", "quote_candidate"])
    if "--missing" in sys.argv:
        rv = rv[(rv["page"] == "") & d.loc[rv["i"], "source_file"].str.endswith(".pdf").values]
    if "--quotes" in sys.argv:
        rv = rv[d.loc[rv["i"], "score"].values == ""]
    pd.set_option("display.width", 320); pd.set_option("display.max_rows", 1000); pd.set_option("display.max_colwidth", 170)
    print(rv.to_string(index=False))
    noq = d[(d["score"] == "") & (d["quote"] == "") & (rv.set_index("i")["quote_candidate"].reindex(d.index).fillna("") == "")]
    print("\nqualitative rows with no quote:", len(noq))
    print("\nrows without a page (PDF sources):", ((d["page"] == "") & d["source_file"].str.endswith(".pdf")).sum(), "of", d["source_file"].str.endswith(".pdf").sum())
    if write:
        if "quote_candidate" in d.columns:
            mask = (d["quote"] == "") & (d["score"] == "")
            d.loc[mask, "quote"] = d.loc[mask, "quote_candidate"].fillna("")
            d = d.drop(columns=["quote_candidate"])
        d.to_csv(DATA, index=False)
        print("written")


if __name__ == "__main__":
    main("--write" in sys.argv)
