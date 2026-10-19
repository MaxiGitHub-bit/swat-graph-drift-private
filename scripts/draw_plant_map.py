"""
This draws the engineering plant map from docs/plant_map/ to docs/plant_map/plant_map.png.
  python scripts/draw_plant_map.py
Solid lines: documented links. Dashed: inferred (to verify). Grey nodes: backup or unused.

"""
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from swatlab import graph  # noqa: E402

nodes = graph.load_nodes()
links = [r for r in graph.load_links() if r["evidence"]
         in ("documented", "inferred")]
by_stage = defaultdict(list)
for n in nodes:
    by_stage[int(n["stage"])].append(n)
pos = {}
for s, ns in by_stage.items():
    sens = [n for n in ns if n["kind"] == "sensor"]
    acts = [n for n in ns if n["kind"] == "actuator"]
    for k, n in enumerate(sens):
        pos[n["tag"]] = (s * 3.0 - 0.6, -k * 1.0)
    for k, n in enumerate(acts):
        pos[n["tag"]] = (s * 3.0 + 0.6, -k * 1.0 - 0.5)

fig, ax = plt.subplots(figsize=(16, 9))
style = {"flow": "#1f77b4", "control": "#d62728", "shared_role": "#7f7f7f"}
for r in links:
    (x1, y1), (x2, y2) = pos[r["node_a"]], pos[r["node_b"]]
    rad = 0.35 if abs(x1 - x2) < 0.01 else 0.0
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), zorder=1,
                arrowprops=dict(arrowstyle="-", color=style[r["type"]], lw=1.2, alpha=0.75,
                                ls="-" if r["evidence"] == "documented" else "--",
                                connectionstyle=f"arc3,rad={rad}", shrinkA=9, shrinkB=9)
                )
for n in nodes:
    x, y = pos[n["tag"]]
    quiet = n["status"] != "active"
    ax.scatter(x, y, s=420, zorder=2, color="#dddddd" if quiet else
               ("#ffffff" if n["kind"] == "sensor" else "#fff2cc"), edgecolors="black", linewidths=0.8)
    ax.text(x, y, n["tag"], ha="center", va="center", fontsize=6.5, zorder=3)
for s in sorted(by_stage):
    ax.text(s * 3.0, 1.3, f"Stage {s}",
            ha="center", fontsize=11, weight="bold")
for t, c in style.items():
    ax.plot([], [], color=c, label=t.replace("_", " "))
ax.plot([], [], color="black", ls="--", label="inferred (to verify)")
ax.legend(loc="lower right", frameon=False)
ax.set_title(
    "SWaT engineering plant map (a draft), from Goh et al. (2017) Fig. 2 and Table 2")
ax.axis("off")
out = REPO / "docs" / "plant_map" / "plant_map.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print("saved", out.relative_to(REPO))
