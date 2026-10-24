"""Run with: python -m pytest tests (or) python tests/test_graph.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np  # noqa: E402
from swatlab import graph  # noqa: E402

ORDER = [n["tag"] for n in graph.load_nodes()]


def test_register_uses_known_tags():
    tags = set(ORDER)
    for row in graph.load_links():
        assert row["node_a"] in tags and row["node_b"] in tags, row["link_id"]


def test_51_nodes():
    assert len(ORDER) == 51


def test_engineering_is_symmetric_without_self_loops():
    A = graph.build("engineering", ORDER)
    assert np.array_equal(A, A.T) and np.trace(A) == 0 and graph.n_links(A) > 0


def test_full_has_at_least_documented_links():
    assert graph.n_links(graph.build("engineering_full", ORDER)) >= graph.n_links(
        graph.build("engineering", ORDER))


def test_random_matches_engineering_link_count():
    eng = graph.build("engineering", ORDER)
    for s in range(5):
        assert graph.n_links(graph.build(
            "random", ORDER, seed=s)) == graph.n_links(eng)


def test_uncertain_links_excluded():
    A = graph.build("engineering_full", ORDER)
    i, j = ORDER.index("AIT402"), ORDER.index("P205")
    assert A[i, j] == 0


def test_edge_index_shape():
    ei = graph.to_edge_index(graph.build("engineering", ORDER))
    assert ei.shape[0] == 2


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
