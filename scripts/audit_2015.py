"""
audit_2015.py is my W1 final step.

Checks the converted 2015 data before any modelling:
  1. where the time gap(s) in the attack file are
  2. how the attack labels line up with the official attack list
  3. the unexplained labelled period on 29 Dec 2015, 06:30 to 06:42
     (compared with attack 21 at 18:30 to 18:42 the same day), as a figure
  4. how much each sensor shifts between the training week and the
     normal-labelled part of the attack week (early drift evidence)
  5. the proposed train / validation split boundaries

"""
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from _common import find_file, get_paths  # noqa: E402

# ~6 h after recording began (Goh et al., 2017)
SETTLE_UNTIL = pd.Timestamp("2015-12-22 22:00:00")
TRAIN_FRACTION = 0.8
WINDOW_SENSORS = ["LIT101", "FIT101", "MV101", "P101"]


def load(work, name):
    return pd.read_parquet(work / "parquet" / f"swat2015_{name}.parquet")


def segments(df):
    f = df["attack"].to_numpy()
    e = np.flatnonzero(np.diff(np.r_[0, f, 0]))
    return pd.DataFrame({"seg_start": df["timestamp"].iloc[e[::2]].to_numpy(),
                         "seg_end": df["timestamp"].iloc[e[1::2] - 1].to_numpy()
                         })


def attack_list(root):
    raw = pd.read_excel(
        find_file(root, "List_of_attacks_Final.xlsx"), dtype=str)
    raw = raw[pd.to_numeric(raw["Attack #"], errors="coerce").notna()].copy()
    raw["attack_no"] = raw["Attack #"].astype(float).astype(int)
    start = pd.to_datetime(raw["Start Time"], errors="coerce")
    start = start.where(start >= "2015-12-01", start +
                        pd.DateOffset(years=1))  # 2015 typo for Jan 2016
    end_t = raw["End Time"].str.extract(r"(\d{1,2}:\d{2}:\d{2})")[0]
    end = pd.to_datetime(start.dt.strftime("%Y-%m-%d") +
                         " " + end_t, errors="coerce")
    out = pd.DataFrame({"attack_no": raw["attack_no"], "list_start": start, "list_end": end,
                        "attack_point": raw["Attack Point"]
                        })
    return out.sort_values("list_start").reset_index(drop=True)


def match(lst, seg):
    rows, used = [], set()
    for _, a in lst.iterrows():
        if pd.isna(a["list_end"]):
            rows.append(
                {**a, "status": "no end time in list"})
            continue
        hit = seg[(seg["seg_start"] <= a["list_end"]) &
                  (seg["seg_end"] >= a["list_start"])]
        if hit.empty:
            rows.append({**a, "status": "NOT labelled in data"})
            continue
        s = hit.iloc[0]
        used.update(hit.index)
        rows.append({**a, "seg_start": s["seg_start"], "seg_end": s["seg_end"],
                     "start_offset_s": (s["seg_start"] - a["list_start"]).total_seconds(),
                     "end_offset_s": (s["seg_end"] - a["list_end"]).total_seconds(),
                     "status": "shares segment with another attack" if len(hit) and
                     ((hit.iloc[0]["seg_end"] - hit.iloc[0]["seg_start"]).total_seconds() >
                      (a["list_end"] - a["list_start"]).total_seconds() + 120) else "matched"})
    extra = seg.drop(index=list(used))
    for _, s in extra.iterrows():
        rows.append({"attack_no": None, "seg_start": s["seg_start"], "seg_end": s["seg_end"],
                     "status": "labelled in data but NOT in list"})
    return pd.DataFrame(rows)


def window_plot(att, out):
    wins = [("2015-12-29 06:00", "2015-12-29 07:15", "06:30-06:42 (not in list)"),
            ("2015-12-29 18:00", "2015-12-29 19:15", "18:30-18:42 (attack 21)")]
    fig, axes = plt.subplots(len(WINDOW_SENSORS), 2,
                             figsize=(12, 9), sharex="col")
    for j, (a, b, title) in enumerate(wins):
        w = att[(att["timestamp"] >= a) & (att["timestamp"] <= b)]
        for i, s in enumerate(WINDOW_SENSORS):
            ax = axes[i, j]
            ax.plot(w["timestamp"], w[s], lw=0.8)
            lab = w["attack"].to_numpy() == 1
            if lab.any():
                ax.fill_between(w["timestamp"], w[s].min(),
                                w[s].max(), where=lab, alpha=0.2, color="red")
            ax.set_ylabel(s)
            if i == 0:
                ax.set_title(title)
    fig.suptitle("29 Dec 2015: labelled periods (red) and plant readings")
    fig.autofmt_xdate()
    fig.savefig(out, dpi=110, bbox_inches="tight")


def main():
    root, work = get_paths(__doc__)
    rep = work / "reports"
    rep.mkdir(exist_ok=True)
    lines = []
    att, nor = load(work, "attack_v0"), load(work, "normal_v1")
    sensors = [c for c in nor.columns if c not in (
        "timestamp", "label_raw", "attack")]

    # 1. gaps
    d = att["timestamp"].diff().dt.total_seconds()
    for i in np.flatnonzero(d.to_numpy() > 1):
        lines.append(f"GAP in attack file: {att['timestamp'].iloc[i - 1]} -> {att['timestamp'].iloc[i]} "
                     f"({int(d.iloc[i])} s); labels around it: {att['attack'].iloc[i - 1]} / {att['attack'].iloc[i]}")

    # 2. labels vs list
    seg = segments(att)
    m = match(attack_list(root), seg)
    m.to_csv(rep / "label_vs_list_2015.csv", index=False)
    lines.append(
        f"\nLabel segments: {len(seg)}; list rows: {m['attack_no'].notna().sum()}")
    for k, v in m["status"].value_counts().items():
        lines.append(f"  {k}: {v}")
    lines.append(
        f"label start offsets (s): {m['start_offset_s'].describe().round(1).to_dict()}")
    lines.append(
        f"label end offsets (s): {m['end_offset_s'].describe().round(1).to_dict()}")

    # 3. 06:30 vs 18:30 window
    window_plot(att, rep / "window_0630_vs_1830.png")
    for a, b in [("2015-12-29 06:30", "2015-12-29 06:42"), ("2015-12-29 18:30", "2015-12-29 18:42")]:
        w = att[(att["timestamp"] >= a) & (att["timestamp"] <= b)]
        lines.append(
            f"\nWindow {a} to {b}: labelled seconds {int(w['attack'].sum())} of {len(w)}")
        for s in WINDOW_SENSORS:
            lines.append(
                f"  {s}: min {w[s].min():.2f} max {w[s].max():.2f} changes {int((w[s].diff() != 0).sum())}")

    # 4. shift between training week and normal part of attack week
    test_norm = att[att["attack"] == 0]
    rows = []
    for s in sensors:
        a, b = nor[s].to_numpy()[::10], test_norm[s].to_numpy()[::10]
        sd = a.std()
        rows.append({"sensor": s, "train_mean": a.mean(), "test_normal_mean": b.mean(),
                     "shift_in_train_sd": (b.mean() - a.mean()) / sd if sd > 0 else np.nan,
                     "ks_stat": ks_2samp(a, b).statistic if sd > 0 or b.std() > 0 else 0.0,
                     "test_outside_train_range_pct": 100 * np.mean((b < a.min()) | (b > a.max())
                                                                   )})
    sh = pd.DataFrame(rows).sort_values("ks_stat", ascending=False)
    sh.to_csv(rep / "shift_2015.csv", index=False, float_format="%.4g")
    lines.append(
        "\nLargest shifts, training week vs normal part of attack week (KS statistic):")
    for _, r in sh.head(12).iterrows():
        lines.append(f"  {r['sensor']:8s} KS {r['ks_stat']:.2f}  shift {r['shift_in_train_sd']:+.2f} sd  "
                     f"outside train range {r['test_outside_train_range_pct']:.1f}%"
                     )

    # 5. split
    usable = nor[nor["timestamp"] >= SETTLE_UNTIL]
    cut = usable["timestamp"].iloc[int(len(usable) * TRAIN_FRACTION)]
    lines.append(f"\nSplit proposal: drop before {SETTLE_UNTIL}; train {usable['timestamp'].iloc[0]} to "
                 f"{cut - pd.Timedelta(seconds=1)} ({int(len(usable) * TRAIN_FRACTION):,} rows); "
                 f"validation {cut} to {usable['timestamp'].iloc[-1]} "
                 f"({len(usable) - int(len(usable) * TRAIN_FRACTION):,} rows)"
                 )

    (rep / "audit_2015.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print("\nDone, Victor.")


if __name__ == "__main__":
    main()
