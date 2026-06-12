"""
Matplotlib helpers for zone-coloured bar charts, WHO guideline lines,
and zone legend elements.

Depends on ``matplotlib`` and ``src.stations``.
"""

from __future__ import annotations

from typing import Optional

from matplotlib.patches import Patch

from src.stations import ZONE_COLORS, ZONE_LABELS, WHO_LIMITS


def zone_bar_colors(zones: list[str]) -> list[str]:
    """Map a list of zone keys to their corresponding bar colours.

    Parameters
    ----------
    zones : list[str]
        Zone keys (``"norte"``, ``"centro"``, ``"sur"``, …).

    Returns
    -------
    list[str]
        CSS colour strings.
    """
    return [ZONE_COLORS.get(z, "#888888") for z in zones]


def add_who_guideline(
    ax,
    pollutant: str,
    linewidth: float = 2,
    linestyle: str = "--",
    alpha: float = 0.8,
    label: Optional[str] = None,
):
    """Add a vertical dashed line for the WHO annual guideline.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis to draw on.
    pollutant : str
        ``"PM2.5"`` or ``"PM10"``.
    linewidth : float
        Line width (default 2).
    linestyle : str
        Line style (default ``"--"``).
    alpha : float
        Transparency (default 0.8).
    label : str or None
        Custom label. Falls back to ``"WHO guideline (X µg/m³)"``.
    """
    limit = WHO_LIMITS.get(pollutant)
    if limit is None:
        return
    if label is None:
        label = f"WHO guideline ({limit}\\u00a0\\u03bcg/m\\u00b3)"
    ax.axvline(limit, color="#e74c3c", linestyle=linestyle,
               linewidth=linewidth, alpha=alpha, label=label)


def add_who_horizontal(
    ax,
    pollutant: str,
    linewidth: float = 1.5,
    linestyle: str = ":",
    alpha: float = 0.5,
    text_offset: float = 0.0,
):
    """Add a horizontal dashed line for the WHO annual guideline.

    Useful for grouped bar charts where the guideline is a y-axis threshold
    rather than an x-axis line.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis to draw on.
    pollutant : str
        ``"PM2.5"`` or ``"PM10"``.
    linewidth : float
        Line width (default 1.5).
    linestyle : str
        Line style (default ``":"``).
    alpha : float
        Transparency (default 0.5).
    text_offset : float
        X offset for the label (default 0: places it at the right edge).
    """
    limit = WHO_LIMITS.get(pollutant)
    if limit is None:
        return
    color = "#c0392b" if pollutant == "PM2.5" else "#e67e22"
    ax.axhline(limit, color=color, linestyle=linestyle,
               linewidth=linewidth, alpha=alpha)
    xlim = ax.get_xlim()
    ax.text(xlim[1] + text_offset, limit + 0.5,
            f"WHO PM\\u2082.\\u2085" if pollutant == "PM2.5" else f"WHO PM\\u2081\\u2080",
            fontsize=9, color=color)


def create_zone_legend(
    colors: Optional[dict[str, str]] = None,
    labels: Optional[dict[str, str]] = None,
    loc: str = "lower right",
    fontsize: int = 11,
):
    """Build a matplotlib legend handle for zones.

    Parameters
    ----------
    colors : dict or None
        Zone → colour map. Defaults to :data:`src.stations.ZONE_COLORS`.
    labels : dict or None
        Zone → label map. Defaults to :data:`src.stations.ZONE_LABELS`.
    loc : str
        Legend location (default ``"lower right"``).
    fontsize : int
        Font size for the legend (default 11).

    Returns
    -------
    list[Patch]
        Handles to pass to ``ax.legend()``.
    """
    colors = colors or ZONE_COLORS
    labels = labels or ZONE_LABELS
    return [
        Patch(facecolor=colors["norte"], label=labels["norte"]),
        Patch(facecolor=colors["centro"], label=labels["centro"]),
        Patch(facecolor=colors["sur"],   label=labels["sur"]),
    ]
