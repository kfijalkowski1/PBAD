"""Tests for comparator.compare.

All test cases use hand-built nx.DiGraph instances — no Mermaid parsing
required — so these tests run without Node.js.
"""

from __future__ import annotations

import pytest
import networkx as nx
from comparator import (
    node_precision,
    node_recall,
    node_f1,
    edge_precision,
    edge_recall,
    edge_f1,
    compare_architectures,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_graph(nodes: list[str], edges: list[tuple[str, str]]) -> nx.DiGraph:
    g: nx.DiGraph = nx.DiGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    return g


# ---------------------------------------------------------------------------
# Node metrics
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "base_nodes, gen_nodes, exp_precision, exp_recall, exp_f1",
    [
        # Full overlap
        pytest.param(
            ["A", "B", "C"], ["A", "B", "C"],
            1.0, 1.0, 1.0,
            id="full_overlap",
        ),
        # No overlap
        pytest.param(
            ["A", "B"], ["C", "D"],
            0.0, 0.0, 0.0,
            id="no_overlap",
        ),
        # 50 % recall: generated recovers 1 of 2 base nodes
        pytest.param(
            ["A", "B"], ["A", "C"],
            0.5, 0.5, 0.5,
            id="half_overlap",
        ),
        # Generated is superset: precision drops
        pytest.param(
            ["A", "B"], ["A", "B", "C", "D"],
            0.5, 1.0, 2 / 3,
            id="generated_superset",
        ),
        # Generated is subset: recall drops
        pytest.param(
            ["A", "B", "C", "D"], ["A", "B"],
            1.0, 0.5, 2 / 3,
            id="generated_subset",
        ),
        # Empty generated
        pytest.param(
            ["A", "B"], [],
            0.0, 0.0, 0.0,
            id="empty_generated",
        ),
        # Empty base
        pytest.param(
            [], ["A", "B"],
            0.0, 0.0, 0.0,
            id="empty_base",
        ),
    ],
)
def test_node_metrics(
    base_nodes: list[str],
    gen_nodes: list[str],
    exp_precision: float,
    exp_recall: float,
    exp_f1: float,
) -> None:
    base = make_graph(base_nodes, [])
    gen = make_graph(gen_nodes, [])
    assert node_precision(base, gen) == pytest.approx(exp_precision)
    assert node_recall(base, gen) == pytest.approx(exp_recall)
    assert node_f1(base, gen) == pytest.approx(exp_f1)


# ---------------------------------------------------------------------------
# Edge metrics
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "base_edges, gen_edges, exp_precision, exp_recall, exp_f1",
    [
        # Full overlap
        pytest.param(
            [("A", "B"), ("B", "C")], [("A", "B"), ("B", "C")],
            1.0, 1.0, 1.0,
            id="full_overlap",
        ),
        # No overlap
        pytest.param(
            [("A", "B")], [("C", "D")],
            0.0, 0.0, 0.0,
            id="no_overlap",
        ),
        # Half overlap
        pytest.param(
            [("A", "B"), ("B", "C")], [("A", "B"), ("C", "D")],
            0.5, 0.5, 0.5,
            id="half_overlap",
        ),
        # Empty generated
        pytest.param(
            [("A", "B")], [],
            0.0, 0.0, 0.0,
            id="empty_generated",
        ),
        # Empty base
        pytest.param(
            [], [("A", "B")],
            0.0, 0.0, 0.0,
            id="empty_base",
        ),
    ],
)
def test_edge_metrics(
    base_edges: list[tuple[str, str]],
    gen_edges: list[tuple[str, str]],
    exp_precision: float,
    exp_recall: float,
    exp_f1: float,
) -> None:
    all_nodes = list({n for e in base_edges + gen_edges for n in e})
    base = make_graph(all_nodes, base_edges)
    gen = make_graph(all_nodes, gen_edges)
    assert edge_precision(base, gen) == pytest.approx(exp_precision)
    assert edge_recall(base, gen) == pytest.approx(exp_recall)
    assert edge_f1(base, gen) == pytest.approx(exp_f1)


# ---------------------------------------------------------------------------
# Case-insensitive normalisation
# ---------------------------------------------------------------------------

def test_node_matching_is_case_insensitive() -> None:
    base = make_graph(["ServiceA", "ServiceB"], [])
    gen = make_graph(["servicea", "SERVICEB"], [])
    assert node_recall(base, gen) == pytest.approx(1.0)
    assert node_precision(base, gen) == pytest.approx(1.0)


def test_edge_matching_is_case_insensitive() -> None:
    base = make_graph([], [("ServiceA", "ServiceB")])
    gen = make_graph([], [("servicea", "serviceb")])
    assert edge_recall(base, gen) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# compare_architectures — keys and consistency
# ---------------------------------------------------------------------------

COMPARE_CASES = [
    pytest.param(
        ["A", "B", "C"], [("A", "B"), ("B", "C")],
        ["A", "B", "C"], [("A", "B"), ("B", "C")],
        id="identical",
    ),
    pytest.param(
        ["A", "B"], [("A", "B")],
        ["C", "D"], [("C", "D")],
        id="no_overlap",
    ),
    pytest.param(
        ["A", "B", "C"], [("A", "B"), ("B", "C")],
        ["A", "B"], [("A", "B")],
        id="partial_overlap",
    ),
]


@pytest.mark.parametrize(
    "base_nodes, base_edges, gen_nodes, gen_edges",
    COMPARE_CASES,
)
def test_compare_architectures_keys(
    base_nodes, base_edges, gen_nodes, gen_edges
) -> None:
    base = make_graph(base_nodes, base_edges)
    gen = make_graph(gen_nodes, gen_edges)
    result = compare_architectures(base, gen)
    expected_keys = {
        "node_precision", "node_recall", "node_f1",
        "edge_precision", "edge_recall", "edge_f1",
        "base_node_count", "generated_node_count", "common_node_count",
        "base_edge_count", "generated_edge_count", "common_edge_count",
    }
    assert set(result.keys()) == expected_keys


@pytest.mark.parametrize(
    "base_nodes, base_edges, gen_nodes, gen_edges",
    COMPARE_CASES,
)
def test_compare_architectures_consistent_with_individual_functions(
    base_nodes, base_edges, gen_nodes, gen_edges
) -> None:
    base = make_graph(base_nodes, base_edges)
    gen = make_graph(gen_nodes, gen_edges)
    result = compare_architectures(base, gen)
    assert result["node_precision"] == pytest.approx(node_precision(base, gen))
    assert result["node_recall"] == pytest.approx(node_recall(base, gen))
    assert result["node_f1"] == pytest.approx(node_f1(base, gen))
    assert result["edge_precision"] == pytest.approx(edge_precision(base, gen))
    assert result["edge_recall"] == pytest.approx(edge_recall(base, gen))
    assert result["edge_f1"] == pytest.approx(edge_f1(base, gen))
