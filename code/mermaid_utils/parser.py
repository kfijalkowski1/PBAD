"""Parse Mermaid flowchart diagrams into networkx directed graphs."""

from __future__ import annotations

import networkx as nx
from mermaid_parser import FlowChartConverter


def _normalise(label: str) -> str:
    return label.strip().lower()


def parse_mermaid(text: str) -> nx.DiGraph:
    """Parse a Mermaid flowchart string and return a normalised DiGraph.

    Node identifiers in the returned graph are lowercased and stripped of
    surrounding whitespace so that label matching across diagrams is
    consistent.

    Parameters
    ----------
    text:
        A Mermaid flowchart definition, e.g.::

            flowchart TD
                A[Service A] --> B[Service B]
                B --> C[Service C]

    Returns
    -------
    nx.DiGraph
        Directed graph where each node is a normalised label string and edges
        represent directed dependencies.
    """
    converter = FlowChartConverter()
    flowchart = converter.convert(text)

    graph: nx.DiGraph = nx.DiGraph()

    for node in flowchart.nodes:
        label = _normalise(node.content if node.content else node.id_)
        graph.add_node(label)

    for link in flowchart.links:
        src_label = _normalise(link.origin.content if link.origin.content else link.origin.id_)
        dst_label = _normalise(link.end.content if link.end.content else link.end.id_)
        graph.add_edge(src_label, dst_label)

    return graph


def parse_mermaid_file(path: str) -> nx.DiGraph:
    """Read a Mermaid file from *path* and return a normalised DiGraph.

    Parameters
    ----------
    path:
        Filesystem path to a ``.mmd`` (or any text) file containing a Mermaid
        flowchart definition.
    """
    with open(path, encoding="utf-8") as fh:
        return parse_mermaid(fh.read())
