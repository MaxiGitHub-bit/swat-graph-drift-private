# SWaT graph detection and drift study

MSc Data Analytics applied research project (Dublin Business School), 2026/2027.

Can a graph-based attack detector be trusted in practice? This project tests an
unsupervised graph autoencoder on the SWaT water treatment testbed:

1. **Fair scoring:** does a map of the plant's physical connections improve
   detection, localisation and false alarms compared with map-free models?
2. **Drift:** how do models trained on 2015 data behave on later releases of
   the same plant?
3. **Practicality:** are the models fast enough to serve in real time?

## Data

**No SWaT data is included in this repository.** The dataset belongs to iTrust,
Singapore University of Technology and Design, and must be requested from them:
https://www.sutd.edu.sg/itrust/itrust-labs/datasets/

## Layout

```
config/      paths.example.yaml
src/swatlab/ project code
scripts/     command-line tools (inventory, leak check)
notebooks/   exploration and reporting notebooks
docs/        plant map and link register
results/     small result tables and figures only
tests/       tests for scoring and data code
```

## Setup

```
pip install -r requirements.txt
copy config\paths.example.yaml config\paths.yaml
```

Before every push: `python scripts/check_no_leaks.py`

## Status

Private, work in progress. Not for citation.
