"""Compare a generated architecture against a base (reference) architecture.

Uses the "Reference Service Graph" approach described in the project paper:
precision, recall, and F1 are computed separately for nodes (components) and
edges (dependencies).

Node matching is case-insensitive; node labels are normalised the same way as
in ``mermaid_utils.parser``.
"""

from __future__ import annotations

import networkx as nx


def _node_set(g: nx.DiGraph) -> set[str]:
    return {str(n).strip().lower() for n in g.nodes()}


def _edge_set(g: nx.DiGraph) -> set[tuple[str, str]]:
    return {
        (str(u).strip().lower(), str(v).strip().lower())
        for u, v in g.edges()
    }


def _precision(tp: int, predicted: int) -> float:
    return tp / predicted if predicted > 0 else 0.0


def _recall(tp: int, actual: int) -> float:
    return tp / actual if actual > 0 else 0.0


def _f1(precision: float, recall: float) -> float:
    denom = precision + recall
    return 2 * precision * recall / denom if denom > 0 else 0.0


def node_precision(base: nx.DiGraph, generated: nx.DiGraph) -> float:
    """Fraction of generated nodes that are also in the base architecture."""
    base_nodes = _node_set(base)
    gen_nodes = _node_set(generated)
    tp = len(gen_nodes & base_nodes)
    return _precision(tp, len(gen_nodes))


def node_recall(base: nx.DiGraph, generated: nx.DiGraph) -> float:
    """Fraction of base nodes that were recovered in the generated architecture."""
    base_nodes = _node_set(base)
    gen_nodes = _node_set(generated)
    tp = len(gen_nodes & base_nodes)
    return _recall(tp, len(base_nodes))


def node_f1(base: nx.DiGraph, generated: nx.DiGraph) -> float:
    """Harmonic mean of node precision and node recall."""
    return _f1(node_precision(base, generated), node_recall(base, generated))


def edge_precision(base: nx.DiGraph, generated: nx.DiGraph) -> float:
    """Fraction of generated edges that are also in the base architecture."""
    base_edges = _edge_set(base)
    gen_edges = _edge_set(generated)
    tp = len(gen_edges & base_edges)
    return _precision(tp, len(gen_edges))


def edge_recall(base: nx.DiGraph, generated: nx.DiGraph) -> float:
    """Fraction of base edges that were recovered in the generated architecture."""
    base_edges = _edge_set(base)
    gen_edges = _edge_set(generated)
    tp = len(gen_edges & base_edges)
    return _recall(tp, len(base_edges))


def edge_f1(base: nx.DiGraph, generated: nx.DiGraph) -> float:
    """Harmonic mean of edge precision and edge recall."""
    return _f1(edge_precision(base, generated), edge_recall(base, generated))


def compare_architectures(
    base: nx.DiGraph, generated: nx.DiGraph
) -> dict[str, float | int]:
    """Return all six comparison metrics plus raw overlap counts.

    Keys in the returned dict:

    - ``node_precision``, ``node_recall``, ``node_f1``
    - ``edge_precision``, ``edge_recall``, ``edge_f1``
    - ``base_node_count``, ``generated_node_count``, ``common_node_count``
    - ``base_edge_count``, ``generated_edge_count``, ``common_edge_count``
    """
    base_nodes = _node_set(base)
    gen_nodes = _node_set(generated)
    base_edges = _edge_set(base)
    gen_edges = _edge_set(generated)

    common_nodes = gen_nodes & base_nodes
    common_edges = gen_edges & base_edges

    n_prec = _precision(len(common_nodes), len(gen_nodes))
    n_rec = _recall(len(common_nodes), len(base_nodes))
    e_prec = _precision(len(common_edges), len(gen_edges))
    e_rec = _recall(len(common_edges), len(base_edges))

    return {
        "node_precision": n_prec,
        "node_recall": n_rec,
        "node_f1": _f1(n_prec, n_rec),
        "edge_precision": e_prec,
        "edge_recall": e_rec,
        "edge_f1": _f1(e_prec, e_rec),
        "base_node_count": len(base_nodes),
        "generated_node_count": len(gen_nodes),
        "common_node_count": len(common_nodes),
        "base_edge_count": len(base_edges),
        "generated_edge_count": len(gen_edges),
        "common_edge_count": len(common_edges),
    }
