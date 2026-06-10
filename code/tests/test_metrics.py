"""Tests for metrics.calculator.

All test cases use hand-built nx.DiGraph instances — no Mermaid parsing
required — so these tests run without Node.js.
"""

from __future__ import annotations

import pytest
import networkx as nx
from metrics import dep_avg, average_change_impact, calculate_all_metrics


# ---------------------------------------------------------------------------
# Helper to build graphs quickly
# ---------------------------------------------------------------------------

def make_graph(edges: list[tuple[str, str]], isolated: list[str] | None = None) -> nx.DiGraph:
    g: nx.DiGraph = nx.DiGraph()
    g.add_edges_from(edges)
    if isolated:
        g.add_nodes_from(isolated)
    return g


# ---------------------------------------------------------------------------
# dep_avg
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "edges, isolated, expected",
    [
        pytest.param([], ["A"], 0.0, id="single_isolated_node"),
        pytest.param([("A", "B"), ("B", "C")], None, 2 / 3, id="linear_chain_ABC"),
        pytest.param([("A", "B"), ("A", "C"), ("A", "D")], None, 3 / 4, id="star_hub_A"),
        pytest.param(
            [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")], None, 4 / 4, id="diamond"
        ),
        pytest.param([("A", "B"), ("B", "A")], None, 2 / 2, id="two_node_cycle"),
        pytest.param([], [], 0.0, id="empty_graph"),
    ],
)
def test_dep_avg(
    edges: list[tuple[str, str]], isolated: list[str] | None, expected: float
) -> None:
    g = make_graph(edges, isolated)
    assert dep_avg(g) == pytest.approx(expected)


# ---------------------------------------------------------------------------
# average_change_impact
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "edges, isolated, expected",
    [
        pytest.param([], ["A"], 0.0, id="single_node_no_impact"),
        # A->B->C: A affects 2, B affects 1, C affects 0  → (2+1+0)/(3*3) = 3/9
        pytest.param([("A", "B"), ("B", "C")], None, 3 / 9, id="linear_chain_ABC"),
        # Star: A affects 3, B/C/D affect 0 each  → 3/(4*4) = 3/16
        pytest.param([("A", "B"), ("A", "C"), ("A", "D")], None, 3 / 16, id="star_hub_A"),
        # Diamond A->B, A->C, B->D, C->D:
        # A:3, B:1, C:1, D:0  → 5/16
        pytest.param(
            [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")], None, 5 / 16, id="diamond"
        ),
        # Cycle A<->B: A affects 1, B affects 1 → 2/(2*2) = 0.5
        pytest.param([("A", "B"), ("B", "A")], None, 0.5, id="two_node_cycle"),
    ],
)
def test_average_change_impact(
    edges: list[tuple[str, str]], isolated: list[str] | None, expected: float
) -> None:
    g = make_graph(edges, isolated)
    assert average_change_impact(g) == pytest.approx(expected)


# ---------------------------------------------------------------------------
# calculate_all_metrics
# ---------------------------------------------------------------------------

def test_calculate_all_metrics_keys() -> None:
    g = make_graph([("A", "B"), ("B", "C")])
    result = calculate_all_metrics(g)
    assert set(result.keys()) == {"dep_avg", "average_change_impact"}


@pytest.mark.parametrize(
    "edges, isolated",
    [
        pytest.param([], ["A"], id="single_node"),
        pytest.param([("A", "B"), ("B", "C")], None, id="chain"),
        pytest.param([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")], None, id="diamond"),
    ],
)
def test_calculate_all_metrics_matches_individual(
    edges: list[tuple[str, str]], isolated: list[str] | None
) -> None:
    g = make_graph(edges, isolated)
    result = calculate_all_metrics(g)
    assert result["dep_avg"] == pytest.approx(dep_avg(g))
    assert result["average_change_impact"] == pytest.approx(average_change_impact(g))
