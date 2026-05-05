"""Tests for mermaid_utils.parser.

The parser wraps mermaid-parser-py which requires Node.js.  Each test case is
a (mermaid_text, expected_nodes, expected_edges) tuple so that adding new
fixtures is straightforward.
"""

from __future__ import annotations

import pytest
import networkx as nx
from mermaid_utils import parse_mermaid


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SINGLE_NODE = (
    "flowchart TD\n    A[ServiceA]",
    {"servicea"},
    set(),
)

LINEAR_CHAIN = (
    "flowchart TD\n    A[ServiceA] --> B[ServiceB] --> C[ServiceC]",
    {"servicea", "serviceb", "servicec"},
    {("servicea", "serviceb"), ("serviceb", "servicec")},
)

FORK = (
    "flowchart TD\n    A[Gateway] --> B[Auth]\n    A[Gateway] --> C[Catalog]",
    {"gateway", "auth", "catalog"},
    {("gateway", "auth"), ("gateway", "catalog")},
)

DIAMOND = (
    "flowchart TD\n"
    "    A[A] --> B[B]\n"
    "    A[A] --> C[C]\n"
    "    B[B] --> D[D]\n"
    "    C[C] --> D[D]",
    {"a", "b", "c", "d"},
    {("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")},
)

CYCLE = (
    "flowchart TD\n    A[A] --> B[B]\n    B[B] --> A[A]",
    {"a", "b"},
    {("a", "b"), ("b", "a")},
)


@pytest.mark.parametrize(
    "text, expected_nodes, expected_edges",
    [
        pytest.param(*SINGLE_NODE, id="single_node"),
        pytest.param(*LINEAR_CHAIN, id="linear_chain"),
        pytest.param(*FORK, id="fork"),
        pytest.param(*DIAMOND, id="diamond"),
        pytest.param(*CYCLE, id="cycle"),
    ],
)
def test_parse_mermaid_nodes(
    text: str, expected_nodes: set[str], expected_edges: set[tuple[str, str]]
) -> None:
    graph = parse_mermaid(text)
    assert isinstance(graph, nx.DiGraph)
    assert set(graph.nodes()) == expected_nodes


@pytest.mark.parametrize(
    "text, expected_nodes, expected_edges",
    [
        pytest.param(*LINEAR_CHAIN, id="linear_chain"),
        pytest.param(*FORK, id="fork"),
        pytest.param(*DIAMOND, id="diamond"),
        pytest.param(*CYCLE, id="cycle"),
    ],
)
def test_parse_mermaid_edges(
    text: str, expected_nodes: set[str], expected_edges: set[tuple[str, str]]
) -> None:
    graph = parse_mermaid(text)
    assert set(graph.edges()) == expected_edges


def test_parse_mermaid_returns_digraph() -> None:
    graph = parse_mermaid("flowchart TD\n    A[A] --> B[B]")
    assert isinstance(graph, nx.DiGraph)


def test_parse_mermaid_normalises_whitespace() -> None:
    graph = parse_mermaid("flowchart TD\n    A[  My Service  ] --> B[  Other  ]")
    assert "my service" in graph.nodes()
    assert "other" in graph.nodes()
