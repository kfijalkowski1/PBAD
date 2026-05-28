"""Export "by method" bar charts to tex/assets/ as PDFs."""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

sys.path.insert(0, str(Path(__file__).parent.parent))

from notebooks._experiment_viz import (  # noqa: E402
    MetricSection,
    all_required_metrics,
    discover_data_dir,
    load_all_results,
    plot_metric_section,
    setup_style,
)

METRIC_SECTIONS: list[MetricSection] = [
    {
        "title": "Average Dependency Degree",
        "metrics": ["dep_avg"],
        "ylabel": "AvgDepDeg",
    },
    {
        "title": "Average Change Impact",
        "metrics": ["average_change_impact"],
        "ylabel": "ACI",
    },
    {
        "title": "Node Similarity",
        "metrics": ["node_precision", "node_recall", "node_f1"],
        "ylabel": "Score",
    },
    {
        "title": "Edge Similarity",
        "metrics": ["edge_precision", "edge_recall", "edge_f1"],
        "ylabel": "Score",
    },
]

SHORT_LABELS: dict[str, str] = {
    "dep_avg": "DepAvg",
    "average_change_impact": "ACI",
    "node_precision": "Precision",
    "node_recall": "Recall",
    "node_f1": "F1",
    "edge_precision": "Precision",
    "edge_recall": "Recall",
    "edge_f1": "F1",
    "pitstop": "Pitstop",
    "EventTicketSystem": "ETS",
    "HotelPricingSystem": "HPS",
    "add": "ADD",
    "pps": "PPS",
}

CHART_NAMES: dict[str, str] = {
    "Average Dependency Degree": "fig_depavg_method",
    "Average Change Impact": "fig_aci_method",
    "Node Similarity": "fig_node_method",
    "Edge Similarity": "fig_edge_method",
}


def main() -> None:
    assets_dir = Path(__file__).parent.parent.parent / "tex" / "assets"
    if not assets_dir.is_dir():
        raise FileNotFoundError(f"Assets directory not found: {assets_dir}")

    setup_style()
    data_dir = discover_data_dir(Path(__file__).parent)
    df = load_all_results(data_dir, all_required_metrics(METRIC_SECTIONS))

    for section in METRIC_SECTIONS:
        name = CHART_NAMES[section["title"]]
        out_path = assets_dir / f"{name}.pdf"
        plot_metric_section(df, section, "method", SHORT_LABELS, save_path=out_path)
        print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
