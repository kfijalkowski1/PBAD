"""Architecture quality metrics derived from a dependency graph.

All three metrics are taken from the project paper (section "Miarodajne
metryki"):

- **DepAvg** – average out-degree; measures mean coupling per component.
- **ACI**    – average change impact; approximates how far a change spreads.
- **Stab**   – stability index; fraction of components unaffected per scenario,
               summed across all scenarios.

Scenarios are auto-simulated: one scenario per component, where that
component is assumed to be the origin of the change and every component
transitively reachable from it (via directed edges) counts as "affected".
"""

from __future__ import annotations

import networkx as nx


def dep_avg(g: nx.DiGraph) -> float:
    """Mean out-degree across all components.

    ``DepAvg = (1 / |C|) * Σ_{k ∈ C} d_k``

    where ``d_k`` is the number of outgoing edges of component ``k``.

    Returns 0.0 for an empty graph.
    """
    if g.number_of_nodes() == 0:
        return 0.0
    total = sum(d for _, d in g.out_degree())
    return total / g.number_of_nodes()


def average_change_impact(g: nx.DiGraph) -> float:
    """Average Change Impact (ACI).

    For each component ``i``, simulate a change originating there and count
    how many *other* components are transitively reachable (i.e. must also be
    modified).  Normalise by the total component count and average across all
    N = |C| simulated scenarios:

    ``ACI = (1/C) * (1/N) * Σ_{i=1}^{N} c_i``

    Because N = C, this simplifies to:

    ``ACI = (1/C²) * Σ_{i=1}^{C} c_i``

    Returns 0.0 for a graph with fewer than 2 nodes.
    """
    n = g.number_of_nodes()
    if n < 2:
        return 0.0

    total_affected = sum(
        len(nx.descendants(g, node)) for node in g.nodes()
    )
    return total_affected / (n * n)


def stability_index(g: nx.DiGraph) -> float:
    """Architecture Stability Index (Stab).

    For each simulated scenario (change originating at component ``i``),
    stable components are those *not* reachable from ``i`` (excluding ``i``
    itself).  The index is the sum of the per-scenario stability ratios:

    ``Stab = Σ_{i=1}^{N} (|C_stable| / |C_all|)``

    Returns 0.0 for an empty graph.
    """
    n = g.number_of_nodes()
    if n == 0:
        return 0.0

    total = 0.0
    for node in g.nodes():
        affected = len(nx.descendants(g, node))
        stable = n - 1 - affected  # exclude the origin node itself
        total += stable / n
    return total


def calculate_all_metrics(g: nx.DiGraph) -> dict[str, float]:
    """Return all three metrics as a dictionary.

    Keys: ``"dep_avg"``, ``"average_change_impact"``, ``"stability_index"``.
    """
    return {
        "dep_avg": dep_avg(g),
        "average_change_impact": average_change_impact(g),
        "stability_index": stability_index(g),
    }
