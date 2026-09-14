"""Digitise the score-versus-budget curves in the OpenAI GPT-5.6 and GPT-6 Astra system cards.

The cards give these evaluations only as line charts (score against API cost, simulated latency or
output tokens). This script finds the axes and tick marks of each chart image, finds the filled
circle markers by their legend colour (thin lines are removed by a morphological opening) and maps
marker centres to data values. Output: data/ai_rd_scaling_curves.csv, confidence `chart`.

Inputs: crops of the card pages (see FIGURES) rendered with PyMuPDF at 260 dpi into the folder
given on the command line; the Astra card's figures are the PNGs embedded in the web page."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "ai_rd_scaling_curves.csv"

GPT56 = dict(card="GPT-5.6 system card", card_date="2026-07", source_file="cards/openai/gpt-5-6.pdf")
ASTRA = dict(card="GPT-6 Astra system card", card_date="2026-09", source_file="cards/openai/gpt-6-astra.html")
# legend: model name -> legend-dot pixel x (y given per figure); tick values in axis order
FIGURES = [
    dict(file="fig37_debug_cost.png", benchmark="Internal Research Debugging Eval", x_kind="API cost", x_unit="USD", y_metric="rubric score %",
         xticks=[0, 2, 4, 6], yticks=[20, 40, 60], legend_y=172, page=59, figure="Figure 37", **GPT56),
    dict(file="fig38_debug_latency.png", benchmark="Internal Research Debugging Eval", x_kind="simulated latency", x_unit="minutes", y_metric="rubric score %",
         xticks=[0, 2, 4, 6], yticks=[20, 40, 60], legend_y=172, page=60, figure="Figure 38", **GPT56),
    dict(file="fig39_kernel_cost.png", benchmark="KernelGen 1P", x_kind="API cost", x_unit="USD", y_metric="rubric score %",
         xticks=[0, 50, 100], yticks=[0, 20, 40, 60], legend_y=177, page=61, figure="Figure 39", **GPT56),
    dict(file="fig40_kernel_latency.png", benchmark="KernelGen 1P", x_kind="simulated latency", x_unit="minutes", y_metric="rubric score %",
         xticks=[0, 100, 200], yticks=[0, 20, 40, 60], legend_y=164, page=61, figure="Figure 40", **GPT56),
    dict(file="fig43_nanogpt_cost.png", benchmark="NanoGPT", x_kind="API cost", x_unit="USD", y_metric="mean reward %",
         xticks=[0, 20, 40, 60], yticks=[0, 5, 10, 15], legend_y=177, page=64, figure="Figure 43", **GPT56),
    dict(file="fig44_nanogpt_latency.png", benchmark="NanoGPT", x_kind="simulated latency", x_unit="minutes", y_metric="mean reward %",
         xticks=[0, 200, 400], yticks=[0, 5, 10, 15], legend_y=164, page=64, figure="Figure 44", **GPT56),
    dict(file="fig45_posttrain_latency.png", benchmark="PostTrainBench Lite", x_kind="simulated latency", x_unit="minutes", y_metric="mean reward %",
         xticks=[100, 200], yticks=[0, 20, 40, 60], legend_y=225, page=65, figure="Figure 45", **GPT56),
    dict(file="astra_debug.png", benchmark="Internal Research Debugging Eval", x_kind="output tokens", x_unit="tokens", y_metric="rubric score %",
         xticks=[10_000, 20_000], yticks=[40, 60, 80], legend_y=164, xlog=True, page="", figure="Figure 52", **ASTRA),
    dict(file="astra_kernel.png", benchmark="KernelGen 1P", x_kind="output tokens", x_unit="tokens", y_metric="rubric score %",
         xticks=[0, 100_000, 200_000, 300_000], yticks=[0, 20, 40, 60], legend_y=164, page="", figure="Figure 53", **ASTRA),
    dict(file="astra_nanogpt.png", benchmark="NanoGPT", x_kind="output tokens", x_unit="tokens", y_metric="mean reward %",
         xticks=[0, 50_000, 100_000, 150_000], yticks=[0, 10, 20], legend_y=164, page="", figure="Figure 54", **ASTRA),
    dict(file="astra_posttrain.png", benchmark="PostTrainBench Lite", x_kind="output tokens", x_unit="tokens", y_metric="mean reward %",
         xticks=[0, 100_000, 200_000], yticks=[40, 60, 80], legend_y=164, page="", figure="Figure 55", **ASTRA),
]
LEGEND_56 = {"GPT-5.6 Sol": 276, "GPT-5.6 Terra": 498, "GPT-5.6 Luna": 748, "GPT-5.5": 985, "GPT-5.4 Thinking": 1151}
LEGEND_ASTRA = {"GPT-6 Astra": 599, "GPT-5.6 Sol": 835}


def dark(a):
    mx, mn = a.max(-1), a.min(-1)
    return (mx < 140) & (mx - mn < 30)


def axes_and_ticks(a):
    d = dark(a)
    rows = d.sum(1); cols = d.sum(0)
    ya = int(rows.argmax()); xa = int(cols.argmax())
    # x ticks: dark pixels in the band just below the x axis, grouped into runs
    band = d[ya + 3: ya + 14, :].any(0)
    xt = [int(np.mean(g)) for g in _runs(np.where(band)[0])]
    band = d[:, xa - 14: xa - 3].any(1)
    yt = [int(np.mean(g)) for g in _runs(np.where(band)[0])]
    return xa, ya, xt, yt


def _runs(idx):
    if len(idx) == 0:
        return []
    groups, cur = [], [idx[0]]
    for i in idx[1:]:
        if i - cur[-1] <= 2:
            cur.append(i)
        else:
            groups.append(cur); cur = [i]
    groups.append(cur)
    return [g for g in groups if len(g) <= 12]


def markers(a, colour, exclude_above):
    dist = np.sqrt(((a - np.array(colour)) ** 2).sum(-1))
    m = dist < 45
    m[:exclude_above] = False
    m = ndimage.binary_opening(m, structure=_disk(6))
    lbl, n = ndimage.label(m)
    pts = []
    for i, sl in enumerate(ndimage.find_objects(lbl)):
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        if 10 <= w <= 45 and 10 <= h <= 45:
            cy, cx = ndimage.center_of_mass(lbl[sl] == i + 1)
            pts.append((sl[1].start + cx, sl[0].start + cy))
    return sorted(pts)


def _disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return (x * x + y * y) <= r * r


def calib(ticks_px, values, log=False):
    v = np.log10(values) if log else np.array(values, float)
    px = np.array(ticks_px[:len(values)], float)
    if len(px) != len(v):
        raise ValueError(f"{len(px)} ticks found for {len(v)} values: {ticks_px}")
    slope, icpt = np.polyfit(px, v, 1)
    return (lambda p: 10 ** (slope * p + icpt)) if log else (lambda p: slope * p + icpt)


def main(folder: Path):
    rows = []
    for f in FIGURES:
        a = np.asarray(Image.open(folder / f["file"]).convert("RGB")).astype(int)
        xa, ya, xt, yt = axes_and_ticks(a)
        xt = [t for t in xt if t >= xa - 3]
        yt = [t for t in yt if t <= ya + 3]
        try:
            fx = calib(xt, f["xticks"], f.get("xlog", False)); fy = calib(sorted(yt, reverse=True), f["yticks"])
        except ValueError as e:
            print(f"{f['file']}: {e}  (axes at x={xa}, y={ya}; xticks={xt}, yticks={yt})", file=sys.stderr); continue
        legend = LEGEND_ASTRA if f["card"].startswith("GPT-6") else LEGEND_56
        for model, lx in legend.items():
            colour = a[f["legend_y"], lx]
            pts = markers(a, colour, exclude_above=f["legend_y"] + 25)
            for px, py in pts:
                if px < xa - 5 or py > ya + 5:
                    continue
                rows.append(dict(lab="openai", model=model, card=f["card"], card_date=f["card_date"], benchmark=f["benchmark"],
                                 x_kind=f["x_kind"], x_unit=f["x_unit"], x=round(float(fx(px)), 3 if f["x_unit"] == "USD" else 1),
                                 y=round(float(fy(py)), 1), y_metric=f["y_metric"], source_file=f["source_file"], page=f["page"],
                                 figure=f["figure"], confidence="chart"))
            print(f"{f['file']:28s} {model:16s} {len(pts)} points; max y {max([r['y'] for r in rows if r['model']==model and r['figure']==f['figure']], default='-')}")
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(len(rows), "points ->", OUT)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
