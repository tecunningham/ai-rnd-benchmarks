"""Read the Anthropic ECI (AECI) of every Claude model off the 'Anthropic ECI over time' figure in
the Claude Fable 5.1 / Mythos 5.1 system card (Figure 2.3.5.A, p39), and join the public Epoch ECI.

The figure prints values for the three newest models and anchors Claude 3.5 Sonnet (June 2024) at
130; every other dot is read from the chart. Output: data/ai_rd_aeci.csv."""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "cards/anthropic/claude-fable-5-1-claude-mythos-5-1-system-card.pdf"
PAGE = 39
# dots left to right on the figure, in release order (the figure labels each dot)
MODELS = ["Claude 3 Opus", "Claude 3.5 Sonnet", "Claude 3.5 Sonnet (Oct 2024)", "Claude 3.7 Sonnet", "Claude Opus 4", "Claude Sonnet 4.5",
          "Claude Opus 4.5", "Claude Opus 4.6", "Claude Mythos Preview", "Claude Fable 5 / Mythos 5", "Claude Opus 5", "Claude Fable 5.1 / Mythos 5.1"]
PRINTED = {"Claude 3.5 Sonnet": 130.0, "Claude Fable 5 / Mythos 5": 159.46, "Claude Opus 5": 160.73, "Claude Fable 5.1 / Mythos 5.1": 161.98}
EPOCH_NAME = {"Claude 3.5 Sonnet (Oct 2024)": "Claude 3.5 Sonnet (October 2024)", "Claude Fable 5 / Mythos 5": "Claude Fable 5",
              "Claude Fable 5.1 / Mythos 5.1": "Claude Fable 5.1"}


def dots():
    page = pymupdf.open(CARD)[PAGE - 1]; r = page.rect
    clip = pymupdf.Rect(r.x0 + r.width * 0.1, r.y0 + r.height * 0.08, r.x0 + r.width * 0.9, r.y0 + r.height * 0.48)
    pix = page.get_pixmap(dpi=300, clip=clip)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3].astype(int)
    mx, mn = a.max(-1), a.min(-1)
    grey = (mx < 170) & (mx - mn < 25) & (mn > 60)
    colour = (mx - mn > 60) & (mx < 250)
    pts = []
    for m in (grey, colour):
        er = ndimage.binary_erosion(m, structure=np.ones((7, 7)))          # drops error bars, the dashed trend and text
        lbl, _ = ndimage.label(er)
        for i, sl in enumerate(ndimage.find_objects(lbl)):
            h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
            if 4 <= w <= 40 and 4 <= h <= 40:
                cy, cx = ndimage.center_of_mass(lbl[sl] == i + 1)
                pts.append((sl[1].start + cx, sl[0].start + cy))
    x_axis = int(((mx < 120) & (mx - mn < 20)).sum(1).argmax())
    pts = [p for p in pts if p[1] < x_axis - 20 and p[1] > 0.22 * pix.height]   # inside the plot, below the legend
    return sorted(pts)


def main():
    pts = dots()
    if len(pts) != len(MODELS):
        raise SystemExit(f"found {len(pts)} dots for {len(MODELS)} models: {pts}")
    ys = {m: y for m, (x, y) in zip(MODELS, pts)}
    # calibrate on the two extreme printed values
    (m0, v0), (m1, v1) = ("Claude 3.5 Sonnet", 130.0), ("Claude Fable 5.1 / Mythos 5.1", 161.98)
    k = (ys[m0] - ys[m1]) / (v1 - v0)
    epoch = pd.read_csv(ROOT / "data/external/epoch_eci_scores.csv").set_index("Model")
    rows = []
    for m in MODELS:
        read = v0 + (ys[m0] - ys[m]) / k
        printed = PRINTED.get(m)
        en = EPOCH_NAME.get(m, m)
        rows.append(dict(model=m, aeci=round(printed if printed is not None else read, 2), aeci_read_from_chart=round(read, 2),
                         aeci_source="printed in the card" if printed is not None else "read off Figure 2.3.5.A",
                         eci_public=epoch["eci"].get(en, ""), eci_public_ci_low=epoch["eci_ci_low"].get(en, ""), eci_public_ci_high=epoch["eci_ci_high"].get(en, ""),
                         source_file="cards/anthropic/claude-fable-5-1-claude-mythos-5-1-system-card.pdf", page=PAGE))
    with open(ROOT / "data/ai_rd_aeci.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(f"{r['model']:32s} AECI {r['aeci']:7.2f} ({r['aeci_read_from_chart']:6.2f} read)   public ECI {r['eci_public']}")


if __name__ == "__main__":
    main()
