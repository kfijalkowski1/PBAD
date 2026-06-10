"""Export slide-ready bar charts to code/notebooks/output/presentation/."""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

sys.path.insert(0, str(Path(__file__).parent.parent))

from notebooks._experiment_viz import (  # noqa: E402
    discover_data_dir,
    export_presentation_charts,
    load_all_results,
    presentation_required_metrics,
    setup_presentation_style,
)

SHORT_LABELS: dict[str, str] = {
    "add": "ADD",
    "pps": "PPS",
    "pp": "PP",
    "EventTicketSystem": "ETS",
    "HotelPricingSystem": "HPS",
    "eShop": "eShop",
    "pitstop": "Pitstop",
}


def main() -> None:
    output_dir = Path(__file__).parent / "output" / "presentation"
    setup_presentation_style()
    data_dir = discover_data_dir(Path(__file__).parent)
    df = load_all_results(data_dir, presentation_required_metrics())

    saved = export_presentation_charts(df, SHORT_LABELS, output_dir)
    for path in saved:
        print(f"Saved: {path}")


if __name__ == "__main__":
    main()
