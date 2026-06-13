from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal, NotRequired, TypedDict

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import pandas as pd
import seaborn as sns
from IPython.display import Markdown, display

STATS_SUFFIX = ".mmd.stats"
STATS_COMPARE_SUFFIX = ".mmd.statscompare"
STATS_PATTERN = re.compile(r"^(.+)\.mmd\.stats$")
STATS_COMPARE_PATTERN = re.compile(r"^(.+)\.mmd\.statscompare$")

GroupBy = Literal["method", "app"]

FIGURE_SIZE = (3.5, 2.8)
FACET_HEIGHT = 2.6
FONT_SIZE = 14
TICK_SIZE = 12
LEGEND_SIZE = 10
AXIS_LABEL_SIZE = 10
BAR_LABEL_SIZE = 8

SCORE_METRIC_MARKERS = ("precision", "recall", "f1")


class MetricSection(TypedDict):
    title: str
    metrics: list[str]
    ylabel: str


def discover_data_dir(start: Path | None = None) -> Path:
    anchor = start if start is not None else Path.cwd()
    searched: list[Path] = []
    for base in (anchor, *anchor.parents):
        for relative in ("code/data/final", "data/final"):
            candidate = base / relative
            searched.append(candidate)
            if candidate.is_dir():
                return candidate.resolve()
    paths = "\n".join(f"  - {p}" for p in searched)
    raise FileNotFoundError(f"Could not find data/final directory. Searched:\n{paths}")


def load_json_stats(path: Path) -> dict[str, float | int]:
    text = path.read_text(encoding="utf-8")
    brace = text.find("{")
    if brace < 0:
        raise ValueError(f"No JSON object found in {path}")
    try:
        payload = json.loads(text[brace:])
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}, got {type(payload).__name__}")
    return payload


def _parse_stats_path(path: Path, suffix: str, pattern: re.Pattern[str]) -> tuple[str, str]:
    if not path.name.endswith(suffix):
        raise ValueError(f"Unexpected stats path (expected suffix {suffix!r}): {path}")
    match = pattern.match(path.name)
    if match is None:
        raise ValueError(f"Filename does not match expected pattern: {path.name}")
    method = path.parent.name
    app = match.group(1)
    return method, app


def _load_stats_frame(paths: list[Path], suffix: str, pattern: re.Pattern[str]) -> pd.DataFrame:
    if not paths:
        raise ValueError(f"No files matching *{suffix} under data directory")
    rows: list[dict[str, object]] = []
    for path in sorted(paths):
        method, app = _parse_stats_path(path, suffix, pattern)
        metrics = load_json_stats(path)
        row: dict[str, object] = {"method": method, "app": app}
        row.update(metrics)
        rows.append(row)
    return pd.DataFrame(rows)


def _find_orphan_pairs(
    stats_paths: list[Path],
    compare_paths: list[Path],
) -> list[Path]:
    def key(path: Path, suffix: str, pattern: re.Pattern[str]) -> tuple[str, str]:
        method, app = _parse_stats_path(path, suffix, pattern)
        return method, app

    stats_keys = {key(p, STATS_SUFFIX, STATS_PATTERN): p for p in stats_paths}
    compare_keys = {
        key(p, STATS_COMPARE_SUFFIX, STATS_COMPARE_PATTERN): p for p in compare_paths
    }
    orphans: list[Path] = []
    for pair_key, path in stats_keys.items():
        if pair_key not in compare_keys:
            orphans.append(path)
    for pair_key, path in compare_keys.items():
        if pair_key not in stats_keys:
            orphans.append(path)
    return orphans


def load_all_results(data_dir: Path, required_metrics: list[str]) -> pd.DataFrame:
    stats_paths = sorted(data_dir.glob("**/*.stats"))
    stats_paths = [p for p in stats_paths if p.name.endswith(STATS_SUFFIX)]
    compare_paths = sorted(data_dir.glob("**/*.statscompare"))

    orphans = _find_orphan_pairs(stats_paths, compare_paths)
    if orphans:
        lines = "\n".join(f"  - {p}" for p in orphans)
        raise ValueError(f"Unpaired .stats / .statscompare files:\n{lines}")

    stats_df = _load_stats_frame(stats_paths, STATS_SUFFIX, STATS_PATTERN)
    compare_df = _load_stats_frame(
        compare_paths, STATS_COMPARE_SUFFIX, STATS_COMPARE_PATTERN
    )

    merged = pd.merge(stats_df, compare_df, on=["method", "app"], how="inner")
    if merged.empty:
        raise ValueError(f"No complete (method, app) rows after merge in {data_dir}")

    missing = [m for m in required_metrics if m not in merged.columns]
    if missing:
        raise KeyError(f"Missing metrics in merged data: {missing}")

    return merged


def _camel_to_words(name: str) -> str:
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    return spaced.replace("_", " ").replace("-", " ").title()


def _acronym(name: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", name)
    if len(words) >= 2:
        return "".join(word[0] for word in words).upper()
    return name.upper()


def format_label(
    name: str,
    kind: Literal["method", "app", "metric"],
    short_labels: dict[str, str],
) -> str:
    if name in short_labels:
        return short_labels[name]
    if kind == "method":
        return name.upper()
    if kind == "metric":
        lower = name.lower()
        for marker in SCORE_METRIC_MARKERS:
            if marker in lower:
                return "F1" if marker == "f1" else marker.upper()
        return _camel_to_words(name.replace("_", " "))
    if kind == "app":
        words = _camel_to_words(name)
        if len(words) > 12:
            return _acronym(name)
        return words
    raise ValueError(f"Unknown label kind: {kind!r}")


def apply_labels(df: pd.DataFrame, short_labels: dict[str, str]) -> pd.DataFrame:
    out = df.copy()
    out["method_label"] = out["method"].map(
        lambda m: format_label(str(m), "method", short_labels)
    )
    out["app_label"] = out["app"].map(
        lambda a: format_label(str(a), "app", short_labels)
    )
    return out


def setup_style() -> None:
    sns.set_theme(style="whitegrid", context="paper")
    plt.rcParams.update(
        {
            "font.size": FONT_SIZE,
            "axes.titlesize": FONT_SIZE,
            "axes.labelsize": AXIS_LABEL_SIZE,
            "xtick.labelsize": TICK_SIZE,
            "ytick.labelsize": TICK_SIZE,
            "legend.fontsize": LEGEND_SIZE,
            "figure.figsize": FIGURE_SIZE,
        }
    )


def _is_score_metric(metric: str) -> bool:
    lower = metric.lower()
    return any(marker in lower for marker in SCORE_METRIC_MARKERS)


def _needs_rotated_xlabels(labels: pd.Series | list[str]) -> bool:
    return any(len(str(label)) > 6 for label in labels)


def _rotate_x_labels(ax: plt.Axes) -> None:
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_ha("right")
        label.set_rotation_mode("anchor")


def _apply_x_tick_layout(ax: plt.Axes, labels: pd.Series | list[str]) -> None:
    if _needs_rotated_xlabels(labels):
        _rotate_x_labels(ax)


def _apply_y_grid(ax: plt.Axes) -> None:
    ax.minorticks_on()
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    ax.grid(which="major", axis="y", linestyle="-", linewidth=0.6, alpha=0.6)
    ax.grid(which="minor", axis="y", linestyle=":", linewidth=0.4, alpha=0.35)
    ax.set_axisbelow(True)


def _label_bars(ax: plt.Axes, capped_scores: bool) -> None:
    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="%.2f",
            padding=2,
            fontsize=BAR_LABEL_SIZE,
        )
    ymin, ymax = ax.get_ylim()
    if capped_scores and ymax <= 1.0:
        ax.set_ylim(ymin, min(1.12, ymax * 1.1))
    elif ymax > 0:
        ax.set_ylim(ymin, ymax * 1.08)


def _decorate_axes(ax: plt.Axes, capped_scores: bool) -> None:
    _apply_y_grid(ax)
    _label_bars(ax, capped_scores)


def _set_axis_label_fonts(ax: plt.Axes) -> None:
    ax.set_xlabel(ax.get_xlabel(), fontsize=AXIS_LABEL_SIZE)
    ax.set_ylabel(ax.get_ylabel(), fontsize=AXIS_LABEL_SIZE)


def _move_legend_right(ax: plt.Axes) -> None:
    legend = ax.get_legend()
    if legend is None:
        return
    legend.set_title(None)
    sns.move_legend(
        ax,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        ncol=1,
        frameon=False,
    )


def _finalize_single_axes(
    fig: plt.Figure,
    ax: plt.Axes,
    x_labels: pd.Series | list[str],
    x_title: str,
) -> None:
    _apply_x_tick_layout(ax, x_labels)
    _move_legend_right(ax)
    bottom = 0.22 if _needs_rotated_xlabels(x_labels) else 0.18
    fig.subplots_adjust(bottom=bottom, left=0.18, right=0.72, top=0.88)
    ax.set_xlabel(x_title, fontsize=AXIS_LABEL_SIZE, labelpad=4)


def _finalize_facet_grid(
    g: sns.axisgrid.FacetGrid,
    n_facets: int,
    n_hue: int,
    capped_scores: bool,
) -> None:
    sample_ax = g.axes.flat[0]
    if sample_ax is not None:
        tick_texts = [t.get_text() for t in sample_ax.get_xticklabels()]
        for axis in g.axes.flat:
            if axis is not None:
                _apply_x_tick_layout(axis, tick_texts)
                _decorate_axes(axis, capped_scores)
                _set_axis_label_fonts(axis)
    if g._legend is None:
        raise ValueError("FacetGrid legend missing")
    g._legend.set_title(None)
    col_wrap = g._col_wrap if g._col_wrap is not None else n_facets
    n_rows = (n_facets + col_wrap - 1) // col_wrap
    bottom = 0.30 + 0.08 * n_rows
    g.fig.set_size_inches(FIGURE_SIZE[0] * min(n_facets, 3), FACET_HEIGHT * n_rows + 1.0)
    g.fig.subplots_adjust(bottom=bottom, top=0.82, hspace=0.55, wspace=0.35)
    sns.move_legend(
        g,
        "lower center",
        bbox_to_anchor=(0.5, 0.06),
        ncol=max(min(n_hue, 4), 1),
        frameon=False,
        title=None,
    )


def _melt_metrics(
    df: pd.DataFrame,
    metrics: list[str],
    short_labels: dict[str, str],
) -> pd.DataFrame:
    labeled = apply_labels(df, short_labels)
    long = labeled.melt(
        id_vars=["method", "app", "method_label", "app_label"],
        value_vars=metrics,
        var_name="metric",
        value_name="value",
    )
    long["metric_label"] = long["metric"].map(
        lambda m: format_label(str(m), "metric", short_labels)
    )
    return long


def plot_metric_section(
    df: pd.DataFrame,
    section: MetricSection,
    group_by: GroupBy,
    short_labels: dict[str, str],
    save_path: Path | None = None,
) -> None:
    metrics = section["metrics"]
    for metric in metrics:
        if metric not in df.columns:
            raise KeyError(f"Metric {metric!r} not in dataframe")

    labeled = apply_labels(df, short_labels)
    x_col = "method_label" if group_by == "method" else "app_label"
    hue_col = "app_label" if group_by == "method" else "method_label"
    facet_col = hue_col if len(metrics) > 1 else None

    if len(metrics) > 1:
        plot_df = _melt_metrics(df, metrics, short_labels)
        n_facets = plot_df[facet_col].nunique() if facet_col is not None else 1
        g = sns.catplot(
            data=plot_df,
            kind="bar",
            x=x_col,
            y="value",
            hue="metric_label",
            col=facet_col,
            col_wrap=min(n_facets, 3),
            height=FACET_HEIGHT,
            aspect=FIGURE_SIZE[0] / FACET_HEIGHT,
            legend=True,
            legend_out=True,
            sharey=True,
        )
        grouping = "By Method" if group_by == "method" else "By App"
        x_title = "Method" if group_by == "method" else "App"
        g.fig.suptitle(
            f"{section['title']} ({grouping})",
            y=0.98,
            fontsize=FONT_SIZE,
        )
        g.set_axis_labels(x_title, section["ylabel"])
        g.set_titles(col_template="{col_name}", size=TICK_SIZE)
        capped_scores = all(_is_score_metric(m) for m in metrics)
        if capped_scores:
            g.set(ylim=(0, 1))
        _finalize_facet_grid(
            g, n_facets, plot_df["metric_label"].nunique(), capped_scores
        )
        if save_path is not None:
            g.fig.savefig(save_path, bbox_inches="tight", dpi=150)
            plt.close(g.fig)
        else:
            plt.show()
        return

    plot_df = labeled[[x_col, hue_col, metrics[0]]].rename(
        columns={metrics[0]: "value"}
    )
    capped_scores = all(_is_score_metric(m) for m in metrics)
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    sns.barplot(data=plot_df, x=x_col, y="value", hue=hue_col, ax=ax)
    grouping = "By Method" if group_by == "method" else "By App"
    x_title = "Method" if group_by == "method" else "App"
    ax.set_title(f"{section['title']} ({grouping})")
    ax.set_ylabel(section["ylabel"], fontsize=AXIS_LABEL_SIZE)
    if capped_scores:
        ax.set_ylim(0, 1)
    _decorate_axes(ax, capped_scores)
    _finalize_single_axes(fig, ax, plot_df[x_col].unique(), x_title)
    if save_path is not None:
        fig.savefig(save_path, bbox_inches="tight", dpi=150)
        plt.close(fig)
    else:
        plt.show()


def aggregated_table(
    df: pd.DataFrame,
    metrics: list[str],
    group_by: GroupBy,
    short_labels: dict[str, str],
) -> pd.DataFrame:
    labeled = apply_labels(df, short_labels)
    index_col = "method_label" if group_by == "method" else "app_label"
    column_col = "app_label" if group_by == "method" else "method_label"

    if len(metrics) == 1:
        subset = labeled[[index_col, column_col, metrics[0]]]
        pivot = subset.pivot(index=index_col, columns=column_col, values=metrics[0])
        pivot.columns.name = column_col.replace("_label", "").title()
        pivot.index.name = index_col.replace("_label", "").title()
        return pivot.round(3)

    frames: list[pd.DataFrame] = []
    for metric in metrics:
        subset = labeled[[index_col, column_col, metric]].copy()
        subset = subset.pivot(index=index_col, columns=column_col, values=metric)
        subset.columns = pd.MultiIndex.from_product(
            [[format_label(metric, "metric", short_labels)], subset.columns]
        )
        frames.append(subset)
    combined = pd.concat(frames, axis=1)
    combined.index.name = index_col.replace("_label", "").title()
    return combined.round(3)


def unaggregated_table(
    df: pd.DataFrame,
    metrics: list[str],
    short_labels: dict[str, str],
) -> pd.DataFrame:
    labeled = apply_labels(df, short_labels)
    columns = ["method_label", "app_label", *metrics]
    out = labeled[columns].copy()
    out = out.rename(
        columns={
            "method_label": "Method",
            "app_label": "App",
            **{
                m: format_label(m, "metric", short_labels)
                for m in metrics
            },
        }
    )
    return out.round(3)


def show_results_table(table: pd.DataFrame, caption: str) -> None:
    display(Markdown(f"**{caption}**"))
    display(table)
    latex = table.to_latex(
        float_format=lambda x: f"{x:.3f}",
        bold_rows=False,
    )
    print(latex)


COMPARISON_METRICS: list[str] = [
    "average_change_impact",
    "dep_avg",
    "node_precision",
    "node_recall",
    "node_f1",
    "edge_precision",
    "edge_recall",
    "edge_f1",
]


def _comparison_metric_label(metric: str, short_labels: dict[str, str]) -> str:
    if metric in short_labels:
        return short_labels[metric]
    base = format_label(metric, "metric", short_labels)
    if metric.startswith("node_"):
        return f"Node {base.title() if base.isupper() else base}"
    if metric.startswith("edge_"):
        return f"Edge {base.title() if base.isupper() else base}"
    return format_label(metric, "metric", short_labels)


def mean_by_group_table(
    df: pd.DataFrame,
    metrics: list[str],
    group_by: GroupBy,
    short_labels: dict[str, str],
) -> pd.DataFrame:
    group_col = "method" if group_by == "method" else "app"
    label_col = f"{group_col}_label"
    kind: Literal["method", "app"] = group_by

    means = df.groupby(group_col, as_index=False)[metrics].mean()
    means[label_col] = means[group_col].map(
        lambda value: format_label(str(value), kind, short_labels)
    )
    out = means[[label_col, *metrics]].copy()
    out = out.rename(
        columns={
            label_col: kind.title(),
            **{
                metric: _comparison_metric_label(metric, short_labels)
                for metric in metrics
            },
        }
    )
    return out.round(3)


def plot_mean_comparison(
    df: pd.DataFrame,
    metrics: list[str],
    group_by: GroupBy,
    short_labels: dict[str, str],
) -> None:
    table = mean_by_group_table(df, metrics, group_by, short_labels)
    label_col = "Method" if group_by == "method" else "App"
    plot_df = table.melt(
        id_vars=[label_col],
        var_name="metric_label",
        value_name="value",
    )
    capped_scores = all(_is_score_metric(metric) for metric in metrics)
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    sns.barplot(
        data=plot_df,
        x=label_col,
        y="value",
        hue="metric_label",
        ax=ax,
    )
    x_title = label_col
    ax.set_ylabel("Score" if capped_scores else "Value", fontsize=AXIS_LABEL_SIZE)
    if capped_scores:
        ax.set_ylim(0, 1)
    _decorate_axes(ax, capped_scores)
    _finalize_single_axes(fig, ax, plot_df[label_col].unique(), x_title)
    plt.show()


def render_comparison_summary(
    df: pd.DataFrame,
    short_labels: dict[str, str],
) -> None:
    display(Markdown("## Comparison Summary (Mean over Apps / Methods)"))

    for group_by in ("method", "app"):
        if group_by == "method":
            heading = "### By Method — mean over apps"
            caption = "Comparison — By Method (Mean over Apps)"
        else:
            heading = "### By App — mean over methods"
            caption = "Comparison — By App (Mean over Methods)"

        display(Markdown(heading))
        plot_mean_comparison(df, COMPARISON_METRICS, group_by, short_labels)
        table = mean_by_group_table(df, COMPARISON_METRICS, group_by, short_labels)
        show_results_table(table, caption)


def render_section(
    df: pd.DataFrame,
    section: MetricSection,
    short_labels: dict[str, str],
) -> None:
    metrics = section["metrics"]
    display(Markdown(f"## {section['title']}"))

    for group_by in ("method", "app"):
        grouping = "By Method" if group_by == "method" else "By App"
        display(Markdown(f"### {grouping}"))
        plot_metric_section(df, section, group_by, short_labels)
        agg = aggregated_table(df, metrics, group_by, short_labels)
        show_results_table(agg, f"{section['title']} — {grouping} (Aggregated)")

    raw = unaggregated_table(df, metrics, short_labels)
    show_results_table(raw, f"{section['title']} — Unaggregated")


def all_required_metrics(sections: list[MetricSection]) -> list[str]:
    seen: dict[str, None] = {}
    for section in sections:
        for metric in section["metrics"]:
            seen[metric] = None
    return list(seen.keys())


ChartKind = Literal["structural", "f1"]


class ChartMetric(TypedDict):
    metric: str
    slug: str
    kind: ChartKind


CHART_METRICS: list[ChartMetric] = [
    {
        "metric": "average_change_impact",
        "slug": "change_impact",
        "kind": "structural",
    },
    {"metric": "dep_avg", "slug": "dependency_degree", "kind": "structural"},
    {"metric": "node_f1", "slug": "node_f1", "kind": "f1"},
    {"metric": "edge_f1", "slug": "edge_f1", "kind": "f1"},
]


class PresentationMetric(TypedDict):
    metric: str
    ylabel: str
    slug: str
    italic_ylabel: NotRequired[bool]


_PRESENTATION_YLABELS: dict[str, tuple[str, bool]] = {
    "average_change_impact": ("Change Impact", True),
    "dep_avg": ("Maintainability Index", True),
    "node_f1": ("F1 (usługi)", False),
    "edge_f1": ("F1 (krawędzie)", False),
}

_PRESENTATION_SLUG_OVERRIDES: dict[str, str] = {
    "dep_avg": "maintainability_index",
}


def _build_presentation_metrics() -> list[PresentationMetric]:
    metrics: list[PresentationMetric] = []
    for spec in CHART_METRICS:
        metric = spec["metric"]
        ylabel, italic = _PRESENTATION_YLABELS[metric]
        entry: PresentationMetric = {
            "metric": metric,
            "ylabel": ylabel,
            "slug": _PRESENTATION_SLUG_OVERRIDES.get(metric, spec["slug"]),
        }
        if italic:
            entry["italic_ylabel"] = True
        metrics.append(entry)
    return metrics


PRESENTATION_METRICS: list[PresentationMetric] = _build_presentation_metrics()

BAR_LABEL_PAD_FRACTION = 0.12
BAR_LABEL_PAD_MIN = 0.03

PRES_WIDTH_METHOD = 3.2
PRES_WIDTH_APP = 12.0
PRES_HEIGHT = 4.2
PRES_DPI = 200
PRES_XLABEL_APP = "Aplikacja"
PRES_XLABEL_METHOD = "Metoda"
PRES_BAR_LABEL_SIZE = 10
PRES_MARGIN_LEFT = 0.14
PRES_MARGIN_BOTTOM = 0.18
PRES_MARGIN_TOP = 0.92
PRES_MARGIN_RIGHT = 0.94
PRES_MARGIN_RIGHT_LEGEND = 0.78
VERDANA_FONT_DIR = Path("/usr/share/fonts/truetype/msttcorefonts")

PAPER_WIDTH = 3.35
PAPER_HEIGHT = 2.7
PAPER_HEIGHT_METHOD = 2.0
PAPER_DPI = 200
PAPER_BAR_WIDTH = 0.85
PAPER_BAR_GAP = 0.05
PAPER_SAVEFIG_PAD_INCHES = 0.08
PAPER_BAR_LABEL_SIZE = 5
PAPER_BAR_LABEL_SIZE_AGG = 7
PAPER_AXIS_LABEL_SIZE = 8
PAPER_TICK_SIZE = 7
PAPER_LEGEND_SIZE = 7
PAPER_XLABEL_APP = "Aplikacja"
PAPER_XLABEL_METHOD = "Metoda"
PAPER_MARGIN_LEFT = 0.22
PAPER_MARGIN_BOTTOM = 0.38
PAPER_MARGIN_BOTTOM_COMPACT = 0.20
PAPER_MARGIN_TOP = 0.95
PAPER_MARGIN_RIGHT = 0.98

_PAPER_YLABEL_NAMES: dict[str, str] = {
    "average_change_impact": "Change Impact",
    "dep_avg": "Dependency degree",
    "node_f1": "F1 (usługi)",
    "edge_f1": "F1 (krawędzie)",
}

_PAPER_YLABEL_HINTS: dict[ChartKind, str] = {
    "structural": "(mniej = lepiej)",
    "f1": "(więcej = lepiej)",
}


def _register_verdana_fonts() -> None:
    if not VERDANA_FONT_DIR.is_dir():
        return
    for filename in (
        "Verdana.ttf",
        "Verdana_Italic.ttf",
        "verdana.ttf",
        "verdanai.ttf",
    ):
        font_path = VERDANA_FONT_DIR / filename
        if font_path.is_file():
            fm.fontManager.addfont(str(font_path))


def setup_presentation_style() -> None:
    _register_verdana_fonts()
    sns.set_theme(style="whitegrid", context="talk")
    sns.set_palette("Set2")
    plt.rcParams.update(
        {
            "font.family": "Verdana",
            "font.size": 11,
            "axes.labelsize": 12,
            "axes.titlesize": 12,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "legend.fontsize": 10,
        }
    )


def _set_presentation_ylabel(ax: plt.Axes, ylabel: str, *, italic: bool = False) -> None:
    ax.set_ylabel(ylabel, fontstyle="italic" if italic else "normal")


def _label_bars_exact(
    ax: plt.Axes,
    fmt: str = "%.3f",
    *,
    fontsize: float = PRES_BAR_LABEL_SIZE,
    rotation: float = 0,
    padding: float = 3,
) -> None:
    for container in ax.containers:
        ax.bar_label(
            container,
            fmt=fmt,
            padding=padding,
            fontsize=fontsize,
            rotation=rotation,
        )


def _expand_bar_ylim(
    ax: plt.Axes,
    capped_scores: bool,
) -> None:
    ymin, _ = ax.get_ylim()
    if capped_scores:
        ymin = 0.0

    fig = ax.figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    content_top = ymin
    for container in ax.containers:
        for patch in container:
            top = patch.get_xy()[1] + patch.get_height()
            content_top = max(content_top, top)

    label_top = content_top
    for text in ax.texts:
        bbox = text.get_window_extent(renderer=renderer)
        label_top = max(label_top, bbox.transformed(ax.transData.inverted()).y1)

    if label_top <= ymin:
        ax.set_ylim(ymin, ymin + 1.0)
        return

    span = label_top - ymin
    pad = max(span * BAR_LABEL_PAD_FRACTION, BAR_LABEL_PAD_MIN)
    new_ymax = label_top + pad
    if capped_scores and content_top > 0.85:
        new_ymax = max(new_ymax, 1.08)

    ax.set_ylim(ymin, new_ymax)
    ax.minorticks_on()
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))


def _decorate_presentation_axes(ax: plt.Axes, capped_scores: bool) -> None:
    _apply_y_grid(ax)
    _label_bars_exact(ax)
    _expand_bar_ylim(ax, capped_scores)
    sns.despine(trim=True)


def _finalize_presentation_layout(
    fig: plt.Figure,
    ax: plt.Axes,
    *,
    legend_right: bool = False,
) -> None:
    for label in ax.get_xticklabels():
        label.set_rotation(0)
        label.set_ha("center")
    if legend_right:
        _move_legend_right(ax)
    fig.subplots_adjust(
        left=PRES_MARGIN_LEFT,
        bottom=PRES_MARGIN_BOTTOM,
        top=PRES_MARGIN_TOP,
        right=PRES_MARGIN_RIGHT_LEGEND if legend_right else PRES_MARGIN_RIGHT,
    )


def _save_presentation_figure(fig: plt.Figure, base_path: Path) -> list[Path]:
    saved: list[Path] = []
    for ext in (".png", ".pdf"):
        out = base_path.with_suffix(ext)
        fig.savefig(out, bbox_inches="tight", dpi=PRES_DPI)
        saved.append(out)
    plt.close(fig)
    return saved


def plot_presentation_by_app(
    df: pd.DataFrame,
    metric: str,
    ylabel: str,
    short_labels: dict[str, str],
    save_base: Path | None = None,
    *,
    italic_ylabel: bool = False,
) -> None:
    if metric not in df.columns:
        raise KeyError(f"Metric {metric!r} not in dataframe")

    labeled = apply_labels(df, short_labels)
    plot_df = labeled[["app_label", "method_label", metric]].rename(
        columns={metric: "value"}
    )
    capped_scores = _is_score_metric(metric)

    fig, ax = plt.subplots(figsize=(PRES_WIDTH_APP, PRES_HEIGHT))
    sns.barplot(
        data=plot_df,
        x="app_label",
        y="value",
        hue="method_label",
        palette="Set2",
        ax=ax,
    )
    _set_presentation_ylabel(ax, ylabel, italic=italic_ylabel)
    ax.set_xlabel(PRES_XLABEL_APP, labelpad=4)
    _decorate_presentation_axes(ax, capped_scores)
    _finalize_presentation_layout(fig, ax, legend_right=True)

    if save_base is not None:
        _save_presentation_figure(fig, save_base)
    else:
        plt.show()


def plot_presentation_by_method_mean(
    df: pd.DataFrame,
    metric: str,
    ylabel: str,
    short_labels: dict[str, str],
    save_base: Path | None = None,
    *,
    italic_ylabel: bool = False,
) -> None:
    if metric not in df.columns:
        raise KeyError(f"Metric {metric!r} not in dataframe")

    means = df.groupby("method", as_index=False)[metric].mean()
    means["method_label"] = means["method"].map(
        lambda value: format_label(str(value), "method", short_labels)
    )
    plot_df = means.rename(columns={metric: "value"})
    capped_scores = _is_score_metric(metric)
    n_methods = len(plot_df)
    palette = sns.color_palette("Set2", n_colors=n_methods)

    fig, ax = plt.subplots(figsize=(PRES_WIDTH_METHOD, PRES_HEIGHT))
    sns.barplot(
        data=plot_df,
        x="method_label",
        y="value",
        hue="method_label",
        palette=palette,
        dodge=False,
        legend=False,
        ax=ax,
    )
    _set_presentation_ylabel(ax, ylabel, italic=italic_ylabel)
    ax.set_xlabel(PRES_XLABEL_METHOD, labelpad=4)
    _decorate_presentation_axes(ax, capped_scores)
    _finalize_presentation_layout(fig, ax)

    if save_base is not None:
        _save_presentation_figure(fig, save_base)
    else:
        plt.show()


def _presentation_italic_ylabel(spec: PresentationMetric) -> bool:
    return bool(spec.get("italic_ylabel", False))


def render_presentation_charts(
    df: pd.DataFrame,
    short_labels: dict[str, str],
) -> None:
    for spec in PRESENTATION_METRICS:
        metric = spec["metric"]
        ylabel = spec["ylabel"]
        italic = _presentation_italic_ylabel(spec)
        display(Markdown(f"### {ylabel} — by app"))
        plot_presentation_by_app(
            df, metric, ylabel, short_labels, italic_ylabel=italic
        )
        display(Markdown(f"### {ylabel} — by method (mean over apps)"))
        plot_presentation_by_method_mean(
            df, metric, ylabel, short_labels, italic_ylabel=italic
        )


def export_presentation_charts(
    df: pd.DataFrame,
    short_labels: dict[str, str],
    output_dir: Path,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for spec in PRESENTATION_METRICS:
        metric = spec["metric"]
        ylabel = spec["ylabel"]
        slug = spec["slug"]
        italic = _presentation_italic_ylabel(spec)

        by_app_base = output_dir / f"{slug}_by_app"
        plot_presentation_by_app(
            df,
            metric,
            ylabel,
            short_labels,
            save_base=by_app_base,
            italic_ylabel=italic,
        )
        saved.extend([by_app_base.with_suffix(ext) for ext in (".png", ".pdf")])

        by_method_base = output_dir / f"{slug}_by_method_mean"
        plot_presentation_by_method_mean(
            df,
            metric,
            ylabel,
            short_labels,
            save_base=by_method_base,
            italic_ylabel=italic,
        )
        saved.extend([by_method_base.with_suffix(ext) for ext in (".png", ".pdf")])

    return saved


def chart_required_metrics() -> list[str]:
    return [spec["metric"] for spec in CHART_METRICS]


def presentation_required_metrics() -> list[str]:
    return chart_required_metrics()


def setup_paper_chart_style() -> None:
    sns.set_theme(style="whitegrid", context="paper")
    sns.set_palette("Set2")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman", "Times", "serif"],
            "font.size": PAPER_TICK_SIZE,
            "axes.labelsize": PAPER_AXIS_LABEL_SIZE,
            "axes.titlesize": PAPER_AXIS_LABEL_SIZE,
            "xtick.labelsize": PAPER_TICK_SIZE,
            "ytick.labelsize": PAPER_TICK_SIZE,
            "legend.fontsize": PAPER_LEGEND_SIZE,
        }
    )


def _paper_ylabel_text(spec: ChartMetric) -> str:
    name = _PAPER_YLABEL_NAMES[spec["metric"]]
    hint = _PAPER_YLABEL_HINTS[spec["kind"]]
    return f"{name}\n{hint}"


def _set_paper_ylabel(ax: plt.Axes, spec: ChartMetric) -> None:
    ax.set_ylabel(_paper_ylabel_text(spec), fontsize=PAPER_AXIS_LABEL_SIZE)


def _decorate_paper_axes(
    ax: plt.Axes,
    spec: ChartMetric,
    *,
    bar_label_size: float = PAPER_BAR_LABEL_SIZE,
    bar_label_rotation: float = 0,
) -> None:
    capped_scores = _is_score_metric(spec["metric"])
    fix_ymax_at_one = spec["kind"] == "f1"
    _label_bars_exact(
        ax,
        fontsize=bar_label_size,
        rotation=bar_label_rotation,
        padding=2 if bar_label_rotation else 3,
    )
    if fix_ymax_at_one:
        ax.set_ylim(0, 1.0)
        ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    else:
        _expand_bar_ylim(ax, capped_scores)
    _apply_y_grid(ax)


def _finalize_paper_layout(
    fig: plt.Figure,
    ax: plt.Axes,
    *,
    legend_below: bool = False,
    diagonal_xticks: bool = False,
) -> None:
    if diagonal_xticks:
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha("right")
            label.set_rotation_mode("anchor")
    else:
        for label in ax.get_xticklabels():
            label.set_rotation(0)
            label.set_ha("center")
    if legend_below:
        ax.set_xlabel(ax.get_xlabel(), fontsize=PAPER_AXIS_LABEL_SIZE, labelpad=10)
        fig.subplots_adjust(
            left=PAPER_MARGIN_LEFT,
            bottom=PAPER_MARGIN_BOTTOM,
            top=PAPER_MARGIN_TOP,
            right=PAPER_MARGIN_RIGHT,
        )
        fig.canvas.draw()
        handles, labels = ax.get_legend_handles_labels()
        legend = ax.get_legend()
        if legend is not None:
            legend.remove()
        if handles:
            fig.legend(
                handles,
                labels,
                loc="lower left",
                bbox_to_anchor=(0.02, 0.02),
                bbox_transform=fig.transFigure,
                ncol=1,
                frameon=True,
                fontsize=PAPER_LEGEND_SIZE,
            )
    else:
        ax.set_xlabel(ax.get_xlabel(), fontsize=PAPER_AXIS_LABEL_SIZE, labelpad=4)
        ax.tick_params(axis="both", labelsize=PAPER_TICK_SIZE)
        fig.subplots_adjust(
            left=PAPER_MARGIN_LEFT,
            bottom=PAPER_MARGIN_BOTTOM_COMPACT,
            top=PAPER_MARGIN_TOP,
            right=PAPER_MARGIN_RIGHT,
        )
    ax.tick_params(axis="y", labelsize=PAPER_TICK_SIZE)
    if diagonal_xticks:
        ax.tick_params(axis="x", labelsize=PAPER_TICK_SIZE)


def _set_paper_app_xlim(ax: plt.Axes, n_apps: int) -> None:
    ax.set_xlim(-0.5, n_apps - 0.5)


def _save_paper_figure(
    fig: plt.Figure,
    base_path: Path,
    png_dir: Path | None = None,
) -> list[Path]:
    saved: list[Path] = []
    pdf_path = base_path.with_suffix(".pdf")
    fig.savefig(pdf_path, bbox_inches="tight", pad_inches=PAPER_SAVEFIG_PAD_INCHES)
    saved.append(pdf_path)
    if png_dir is not None:
        png_dir.mkdir(parents=True, exist_ok=True)
        png_path = png_dir / f"{base_path.name}.png"
        fig.savefig(
            png_path,
            bbox_inches="tight",
            pad_inches=PAPER_SAVEFIG_PAD_INCHES,
            dpi=PAPER_DPI,
        )
        saved.append(png_path)
    plt.close(fig)
    return saved


def plot_paper_by_app(
    df: pd.DataFrame,
    spec: ChartMetric,
    short_labels: dict[str, str],
    save_base: Path | None = None,
    png_dir: Path | None = None,
) -> None:
    metric = spec["metric"]
    if metric not in df.columns:
        raise KeyError(f"Metric {metric!r} not in dataframe")

    labeled = apply_labels(df, short_labels)
    plot_df = labeled[["app_label", "method_label", metric]].rename(
        columns={metric: "value"}
    )

    fig, ax = plt.subplots(figsize=(PAPER_WIDTH, PAPER_HEIGHT))
    sns.barplot(
        data=plot_df,
        x="app_label",
        y="value",
        hue="method_label",
        palette="Set2",
        width=PAPER_BAR_WIDTH,
        gap=PAPER_BAR_GAP,
        ax=ax,
    )
    _set_paper_app_xlim(ax, plot_df["app_label"].nunique())
    _set_paper_ylabel(ax, spec)
    ax.set_xlabel(PAPER_XLABEL_APP, labelpad=4)
    _decorate_paper_axes(
        ax,
        spec,
        bar_label_size=PAPER_BAR_LABEL_SIZE,
        bar_label_rotation=90,
    )
    _finalize_paper_layout(fig, ax, legend_below=True, diagonal_xticks=True)

    if save_base is not None:
        _save_paper_figure(fig, save_base, png_dir)
    else:
        plt.show()


def plot_paper_by_method_mean(
    df: pd.DataFrame,
    spec: ChartMetric,
    short_labels: dict[str, str],
    save_base: Path | None = None,
    png_dir: Path | None = None,
) -> None:
    metric = spec["metric"]
    if metric not in df.columns:
        raise KeyError(f"Metric {metric!r} not in dataframe")

    means = df.groupby("method", as_index=False)[metric].mean()
    means["method_label"] = means["method"].map(
        lambda value: format_label(str(value), "method", short_labels)
    )
    plot_df = means.rename(columns={metric: "value"})
    capped_scores = _is_score_metric(metric)
    n_methods = len(plot_df)
    palette = sns.color_palette("Set2", n_colors=n_methods)

    fig, ax = plt.subplots(figsize=(PAPER_WIDTH, PAPER_HEIGHT_METHOD))
    sns.barplot(
        data=plot_df,
        x="method_label",
        y="value",
        hue="method_label",
        palette=palette,
        dodge=False,
        legend=False,
        width=PAPER_BAR_WIDTH,
        ax=ax,
    )
    _set_paper_ylabel(ax, spec)
    ax.set_xlabel(PAPER_XLABEL_METHOD, labelpad=4)
    _decorate_paper_axes(
        ax,
        spec,
        bar_label_size=PAPER_BAR_LABEL_SIZE_AGG,
    )
    _finalize_paper_layout(fig, ax)

    if save_base is not None:
        _save_paper_figure(fig, save_base, png_dir)
    else:
        plt.show()


def render_paper_charts(
    df: pd.DataFrame,
    short_labels: dict[str, str],
) -> None:
    for spec in CHART_METRICS:
        ylabel = _paper_ylabel_text(spec)
        display(Markdown(f"### {ylabel} — by app"))
        plot_paper_by_app(df, spec, short_labels)
        display(Markdown(f"### {ylabel} — by method (mean over apps)"))
        plot_paper_by_method_mean(df, spec, short_labels)


def export_paper_charts(
    df: pd.DataFrame,
    short_labels: dict[str, str],
    pdf_dir: Path,
    png_dir: Path | None = None,
) -> list[Path]:
    pdf_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for spec in CHART_METRICS:
        slug = spec["slug"]

        by_app_base = pdf_dir / f"{slug}_by_app"
        plot_paper_by_app(
            df, spec, short_labels, save_base=by_app_base, png_dir=png_dir
        )
        saved.append(by_app_base.with_suffix(".pdf"))
        if png_dir is not None:
            saved.append(png_dir / f"{by_app_base.name}.png")

        by_method_base = pdf_dir / f"{slug}_by_method_mean"
        plot_paper_by_method_mean(
            df, spec, short_labels, save_base=by_method_base, png_dir=png_dir
        )
        saved.append(by_method_base.with_suffix(".pdf"))
        if png_dir is not None:
            saved.append(png_dir / f"{by_method_base.name}.png")

    return saved
