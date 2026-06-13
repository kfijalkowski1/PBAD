"""Export paper column bar charts to tex/assets/ (PDF) and output/paper/ (PNG)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

sys.path.insert(0, str(Path(__file__).parent.parent))

from notebooks._experiment_viz import (  # noqa: E402
    chart_required_metrics,
    discover_data_dir,
    export_paper_charts,
    load_all_results,
    setup_paper_chart_style,
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
    pdf_dir = Path(__file__).parent.parent.parent / "tex" / "assets"
    png_dir = Path(__file__).parent / "output" / "paper"
    if not pdf_dir.is_dir():
        raise FileNotFoundError(f"Assets directory not found: {pdf_dir}")

    setup_paper_chart_style()
    data_dir = discover_data_dir(Path(__file__).parent)
    df = load_all_results(data_dir, chart_required_metrics())

    saved = export_paper_charts(df, SHORT_LABELS, pdf_dir, png_dir)
    for path in saved:
        print(f"Saved: {path}")


if __name__ == "__main__":
    main()
