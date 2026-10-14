"""Loads local data locations from config/paths.yaml."""
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parents[2]


def load_paths():
    cfg_file = REPO / "config" / "paths.yaml"
    if not cfg_file.exists():
        raise FileNotFoundError(
            "config/paths.yaml not found. Copy config/paths.example.yaml to "
            "config/paths.yaml and set your local folders."
        )
    cfg = yaml.safe_load(cfg_file.read_text(encoding="utf-8"))
    paths = {k: Path(v) for k, v in cfg.items()}
    for k, p in paths.items():
        if REPO in p.resolve().parents or p.resolve() == REPO:
            raise ValueError(
                f"{k} points inside the repository. Keep data outside it.")
    return paths
