"""Digitise the RE-Bench per-task bar charts in Google DeepMind's cards.

Three cards draw normalised RE-Bench scores per task (Optimize a Kernel, Scaling Law Experiment,
Restricted Architecture MLM, Optimize LLM Foundry, Fix Embedding) as grouped bars with the human
8-hour bar, and never print the values. This script finds the horizontal gridlines (0.0 to 2.0 in
steps of 0.2), finds every bar as a solid rectangle, splits the bars into the five task groups by
the gaps between them and names each bar by its position in the group, which follows the legend
order. Output: data/ai_rd_rebench_tasks.csv, confidence `chart`."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "ai_rd_rebench_tasks.csv"
TASKS = ["Optimize a Kernel", "Scaling Law Experiment", "Restricted Architecture MLM", "Optimize LLM Foundry", "Fix Embedding"]

# (image, card, card_date, source_file, page, figure, bars in legend order as (model, budget))
FIGURES = [
    ("gemini-2-5-pro_p18_0.png", "Gemini 2.5 Pro model card", "2025-06", "cards/gdm/gemini-2-5-pro-model-card.pdf", 18, "Figure 4",
     [("Gemini 2.5 Flash", "45 minutes"), ("Gemini 2.5 Pro", "45 minutes"), ("Gemini 2.5 Pro", "2 hours"), ("Claude 3.5 Sonnet", "30 minutes"), ("Human", "8 hours")]),
    ("gemini-2-5-deep-think_p16_0.png", "Gemini 2.5 Deep Think model card", "2025-08", "cards/gdm/gemini-2-5-deep-think-model-card.pdf", 16, "Figure 4",
     [("Gemini 2.5 Flash", "45 minutes"), ("Gemini 2.5 Pro", "45 minutes"), ("Gemini 2.5 Pro", "2 hours"), ("Gemini 2.5 Deep Think", "2 hours"), ("Claude 3.5 Sonnet", "30 minutes"), ("Human", "8 hours")]),
    ("gemini-3-pro-fsf_p16_0.png", "Gemini 3 Pro Frontier Safety Framework report", "2025-11", "cards/gdm/gemini-3-pro-fsf-report.pdf", 16, "Figure 5",
     [("Gemini 2.5 Flash", "2 hours"), ("Gemini 2.5 Pro", "45 minutes"), ("Gemini 2.5 Deep Think", "2 hours"), ("Gemini 3 Pro", "2 hours"), ("Human", "8 hours")]),
]


def gridlines(a):
    """Pixel rows of the light-grey horizontal gridlines inside the plot (top to bottom). The top
    gridline is 2.0 and they are 0.2 apart; the 0.0 line can hide under the dark x axis, so the floor
    is extrapolated from the spacing rather than required to be found."""
    light = (a.min(-1) > 200) & (a.max(-1) < 245) & (a.max(-1) - a.min(-1) < 12)
    rows = np.where(light.mean(1) > 0.35)[0]
    groups, cur = [], [rows[0]]
    for r in rows[1:]:
        if r - cur[-1] <= 2:
            cur.append(r)
        else:
            groups.append(cur); cur = [r]
    groups.append(cur)
    ys = [float(np.mean(g)) for g in groups]
    step = float(np.median(np.diff(ys[:8])))
    ys = [y for y in ys if y <= ys[0] + 10.5 * step]          # drop legend-box edges below the plot
    return ys, step


def bars(a, floor):
    """(x_centre, y_top, width) of every bar. Thin error bars and the star markers are removed by a
    horizontal erosion before connected components are taken; a bar must reach the plot floor."""
    mx, mn = a.max(-1), a.min(-1)
    solid = (mx < 240) & ~((mx - mn < 12) & (mn > 205))            # coloured or grey, not the light gridlines
    ev, eh = 2, 4                                                  # erosion half-sizes: removes lines thinner than 5 x 9 px
    solid = ndimage.binary_erosion(solid, structure=np.ones((2 * ev + 1, 2 * eh + 1)))
    lbl, n = ndimage.label(solid)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lbl)):
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        fill = (lbl[sl] == i + 1).mean()
        if w >= 12 and h >= 2 and fill > 0.8 and abs(sl[0].stop + ev - floor) < 14 and w < 200:
            out.append(((sl[1].start + sl[1].stop) / 2, sl[0].start - ev, w + 2 * eh))
    return sorted(out)


def main(folder: Path):
    rows = []
    for img, card, date, src, page, figure, legend in FIGURES:
        a = np.asarray(Image.open(folder / img).convert("RGB")).astype(int)
        gl, step = gridlines(a)
        top = gl[0]; floor = top + 10 * step                 # 2.0 at the top gridline, 0.0 ten steps down
        slope, icpt = -0.2 / step, 2.0 + 0.2 * top / step
        b = bars(a, floor)
        # split into task groups by the largest gaps
        xs = np.array([x for x, _, _ in b])
        gaps = np.diff(xs)
        cuts = sorted(np.argsort(gaps)[-(len(TASKS) - 1):])
        groups, start = [], 0
        for c in cuts:
            groups.append(b[start:c + 1]); start = c + 1
        groups.append(b[start:])
        for task, g in zip(TASKS, groups):
            if len(g) != len(legend):
                print(f"{img} {task}: {len(g)} bars for {len(legend)} legend entries", file=sys.stderr)
            for (x, ytop, w), (model, budget) in zip(g, legend):
                rows.append(dict(lab="gdm", model=model, time_budget=budget, task=task, normalized_score=round(float(slope * ytop + icpt), 2),
                                 card=card, card_date=date, source_file=src, page=page, figure=figure, confidence="chart"))
        print(f"{img}: {len(b)} bars in {len(groups)} groups")
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(len(rows), "values ->", OUT)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
