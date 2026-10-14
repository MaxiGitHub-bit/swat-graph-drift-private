import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAX_BYTES = 5 * 1024 * 1024
DATA_EXT = {".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".pcap", ".pcapng",
            ".zip", ".npy", ".npz", ".h5", ".pt", ".pth", ".pkl", ".joblib"}
PATTERNS = [r"[A-Za-z]:\\\\?Users\\\\?", r"OneDrive",
            r"anaconda3", r"/Users/[^/\s]+", r"/home/[^/\s]+"]


def tracked_files():
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                         cwd=REPO, capture_output=True, text=True, check=True).stdout
    return [REPO / f for f in out.splitlines() if f]


def main():
    pats = list(PATTERNS)
    local = REPO / "local_patterns.txt"
    if local.exists():
        pats += [re.escape(l.strip())
                 for l in local.read_text(encoding="utf-8").splitlines() if l.strip()]
    rx = re.compile("|".join(pats), re.IGNORECASE)
    problems = []
    for f in tracked_files():
        rel = f.relative_to(REPO).as_posix()
        if rel == "scripts/check_no_leaks.py" or not f.exists():
            continue
        if f.suffix.lower() in DATA_EXT:
            problems.append(f"DATA FILE   {rel}")
            continue
        if f.stat().st_size > MAX_BYTES:
            problems.append(
                f"LARGE FILE  {rel} ({f.stat().st_size / 1e6:.1f} MB)")
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            m = rx.search(line)
            if m:
                problems.append(f"PATTERN     {rel}:{i}  '{m.group(0)}'")
    if problems:
        print("Do NOT push yet. Fix these:\n  " + "\n  ".join(problems))
        sys.exit(1)
    print("Clean: nothing private or data-like found.")


if __name__ == "__main__":
    main()
