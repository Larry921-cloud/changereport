"""Matplotlib chart generation — each function returns a BytesIO PNG buffer."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from io import BytesIO

from changereport.constants import CHART_COLORS


def _apply_style():
    plt.rcParams.update({
        "figure.dpi": 150,
        "font.size": 9,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })


def _fig_to_buffer(fig) -> BytesIO:
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    buf.seek(0)
    plt.close(fig)
    return buf


def generate_all_charts(df: pd.DataFrame, analysis: dict) -> dict:
    """Generate all charts and return as dict of BytesIO buffers."""
    _apply_style()
    charts = {}

    if not analysis["by_category"].empty:
        charts["by_category"] = chart_by_category(analysis["by_category"])

    if not analysis["by_type"].empty:
        charts["by_type"] = chart_by_type(analysis["by_type"])

    if not analysis["by_impact"].empty:
        charts["by_impact"] = chart_by_impact(analysis["by_impact"])

    if not analysis["timeline"].empty:
        charts["timeline"] = chart_timeline(analysis["timeline"])

    if not analysis["hourly"].empty:
        charts["hourly"] = chart_hourly(analysis["hourly"])

    impl = analysis["implementer_workload"]
    if not impl.empty:
        charts["implementer"] = chart_implementer_workload(impl)

    return charts


def chart_by_category(data: pd.Series) -> BytesIO:
    """Horizontal bar chart: changes by network category."""
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = CHART_COLORS[:len(data)]
    bars = ax.barh(range(len(data)), data.values, color=colors)
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels(data.index, fontsize=8)
    ax.set_xlabel("Number of Changes")
    ax.set_title("Changes by Network Category")
    ax.invert_yaxis()

    for i, v in enumerate(data.values):
        ax.text(v + 0.3, i, str(v), va="center", fontsize=8, fontweight="bold")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _fig_to_buffer(fig)


def chart_by_type(data: pd.Series) -> BytesIO:
    """Donut chart: change type distribution."""
    fig, ax = plt.subplots(figsize=(6, 5))
    colors = CHART_COLORS[:len(data)]
    wedges, texts, autotexts = ax.pie(
        data.values,
        labels=data.index,
        autopct=lambda pct: f"{pct:.0f}%\n({int(round(pct / 100 * data.sum()))})",
        colors=colors,
        wedgeprops={"width": 0.55, "edgecolor": "white", "linewidth": 2},
        startangle=90,
        textprops={"fontsize": 9},
    )
    for t in autotexts:
        t.set_fontsize(8)
        t.set_fontweight("bold")
    ax.set_title("Change Type Distribution")
    fig.tight_layout()
    return _fig_to_buffer(fig)


def chart_by_impact(data: pd.Series) -> BytesIO:
    """Horizontal bar chart: impact distribution."""
    # Define a color map based on impact severity
    impact_colors = {
        "No Impact": "#4CAF50",
        "Site Down": "#F44336",
        "Users Disconnected": "#FF9800",
        "Degradation in Service": "#FF5722",
        "Application Unavailable / Reset / Restart": "#E91E63",
        "Application Unavailable": "#E91E63",
    }

    fig, ax = plt.subplots(figsize=(8, 3.5))
    colors = [impact_colors.get(idx, "#607D8B") for idx in data.index]
    ax.barh(range(len(data)), data.values, color=colors)
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels(data.index, fontsize=8)
    ax.set_xlabel("Number of Changes")
    ax.set_title("Impact Distribution")
    ax.invert_yaxis()

    for i, v in enumerate(data.values):
        ax.text(v + 0.3, i, str(v), va="center", fontsize=8, fontweight="bold")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _fig_to_buffer(fig)


def chart_timeline(data: pd.Series) -> BytesIO:
    """Line chart with markers: changes per day."""
    fig, ax = plt.subplots(figsize=(10, 4.5))
    dates = pd.to_datetime(data.index)
    ax.plot(dates, data.values, color=CHART_COLORS[0], marker="o",
            linewidth=2, markersize=5, markerfacecolor=CHART_COLORS[0])
    ax.fill_between(dates, data.values, alpha=0.15, color=CHART_COLORS[0])

    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Changes")
    ax.set_title("Change Activity Timeline")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates) // 10)))
    plt.xticks(rotation=45, ha="right", fontsize=7)

    # Annotate peak day
    peak_idx = data.values.argmax()
    ax.annotate(
        f"{data.values[peak_idx]} changes",
        xy=(dates[peak_idx], data.values[peak_idx]),
        xytext=(15, 20),
        textcoords="offset points",
        fontsize=8,
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="gray"),
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.subplots_adjust(bottom=0.2)
    fig.tight_layout()
    return _fig_to_buffer(fig)


def chart_hourly(data: pd.Series) -> BytesIO:
    """Bar chart: changes by hour of day."""
    fig, ax = plt.subplots(figsize=(8, 3.5))

    # Color bars differently for business hours vs off-hours
    colors = []
    for h in data.index:
        if 8 <= h <= 17:
            colors.append(CHART_COLORS[0])
        elif h >= 22 or h <= 5:
            colors.append(CHART_COLORS[3])
        else:
            colors.append(CHART_COLORS[2])

    ax.bar(data.index, data.values, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Number of Changes")
    ax.set_title("Change Activity by Hour of Day")
    ax.set_xticks(range(24))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(24)], rotation=45,
                       ha="right", fontsize=7)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CHART_COLORS[0], label="Business hours (08-17)"),
        Patch(facecolor=CHART_COLORS[2], label="Evening (18-21)"),
        Patch(facecolor=CHART_COLORS[3], label="Night/early morning (22-05)"),
    ]
    ax.legend(handles=legend_elements, fontsize=7, loc="upper right")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _fig_to_buffer(fig)


def chart_implementer_workload(data: pd.DataFrame) -> BytesIO:
    """Horizontal bar chart: top implementers by change count."""
    # Show top 15 implementers
    top = data.head(15)
    fig, ax = plt.subplots(figsize=(8, max(3.5, len(top) * 0.35)))
    colors = CHART_COLORS[:len(top)] * (len(top) // len(CHART_COLORS) + 1)
    colors = colors[:len(top)]

    ax.barh(range(len(top)), top["change_count"].values, color=colors)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top.index, fontsize=8)
    ax.set_xlabel("Number of Changes")
    ax.set_title("Top Change Implementers")
    ax.invert_yaxis()

    for i, v in enumerate(top["change_count"].values):
        ax.text(v + 0.2, i, str(v), va="center", fontsize=8, fontweight="bold")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _fig_to_buffer(fig)
