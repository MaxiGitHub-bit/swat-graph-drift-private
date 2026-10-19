"""Shared helpers for scripts: find data folders from args or config/paths.yaml."""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

# Accept either key naming in config/paths.yaml
ROOT_KEYS = ("raw_swat_dataset_dir", "swat_root")
WORK_KEYS = ("output_cache_dir", "work_dir")


def _pick(cfg, keys):
    for k in keys:
        if k in cfg:
            return Path(cfg[k])
    sys.exit(f"config/paths.yaml needs one of: {', '.join(keys)}")


def get_paths(description):
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("--swat-root", help="folder holding the raw iTrust SWaT files")
    ap.add_argument("--work-dir", help="folder for processed outputs (outside the repo)")
    args = ap.parse_args()
    if args.swat_root and args.work_dir:
        root, work = Path(args.swat_root), Path(args.work_dir)
    else:
        from swatlab.paths import load_paths
        p = load_paths()
        root = Path(args.swat_root) if args.swat_root else _pick(p, ROOT_KEYS)
        work = Path(args.work_dir) if args.work_dir else _pick(p, WORK_KEYS)
    if not root.exists():
        sys.exit(f"SWaT folder not found: {root}")
    work.mkdir(parents=True, exist_ok=True)
    return root, work


def find_file(root, name):
    hits = [p for p in Path(root).rglob(name) if p.is_file()]
    if not hits:
        sys.exit(f"Could not find {name} under {root}. Unzip the 2015 files first.")
    if len(hits) > 1:
        print(f"Note: {name} found {len(hits)} times; using {hits[0].relative_to(root)}")
    return hits[0]
