from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal, TypedDict

import matplotlib.pyplot as plt
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
