"""
Ground monitoring station metadata, zone classification, and helpers.

Single source of truth for station names, locations, zone assignments,
and zone-based styling constants used across notebooks.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Station metadata — 13 stations across 3 zones
# --------------------------------------------------------------------------- #
STATIONS_META: dict[str, dict] = {
    "Ajusco Medio":   {"id": 242, "lat": 19.272, "lng": -99.208,
                       "municipio": "Tlalpan", "zone": "sur"},
    "Benito Juárez":  {"id": 300, "lat": 19.372, "lng": -99.159,
                       "municipio": "Benito Juárez", "zone": "centro"},
    "CCA":            {"id": 245, "lat": 19.326, "lng": -99.176,
                       "municipio": "Coyoacán", "zone": "sur"},
    "Camarones": {"id": 244, "lat": 19.4686, "lng": -99.1700,
                  "municipio": "Azcapotzalco", "zone": "norte"},
    "Centro":         {"id": 256, "lat": 19.428, "lng": -99.144,
                       "municipio": "Cuauhtémoc", "zone": "centro"},
    "Cuajimalpa": {"id": 248, "lat": 19.3656, "lng": -99.2919,
                   "municipio": "Cuajimalpa de Morelos", "zone": "sur"},
    "Ecatepec":       {"id": 271, "lat": 19.527, "lng": -99.083,
                       "municipio": "Ecatepec de Morelos", "zone": "norte"},
    "GAM":            {"id": 302, "lat": 19.489, "lng": -99.119,
                       "municipio": "Gustavo A. Madero", "zone": "norte"},
    "Hospital General": {"id": 251, "lat": 19.412, "lng": -99.152,
                         "municipio": "Cuauhtémoc", "zone": "centro"},
    "Iztacalco": {"id": 252, "lat": 19.3844, "lng": -99.1178,
                  "municipio": "Iztacalco", "zone": "norte"},
    "Iztapalapa":     {"id": 268, "lat": 19.359, "lng": -99.073,
                       "municipio": "Iztapalapa", "zone": "norte"},
    "Miguel Hidalgo": {"id": 263, "lat": 19.4040, "lng": -99.2027,
                       "municipio": "Miguel Hidalgo", "zone": "centro"},
    "Milpa Alta": {"id": 299, "lat": 19.2007, "lng": -99.0113,
                   "municipio": "Milpa Alta", "zone": "sur"},
    "Naucalpan":      {"id": 243, "lat": 19.574, "lng": -99.241,
                        "municipio": "Naucalpan de Juárez", "zone": "norte"},
    "Nezahualcoyotl": {"id": 258, "lat": 19.405, "lng": -99.032,
                       "municipio": "Nezahualcóyotl", "zone": "norte"},
    "Pedregal":       {"id": 259, "lat": 19.326, "lng": -99.204,
                       "municipio": "Álvaro Obregón", "zone": "sur"},
    "Tlahuac": {"id": 265, "lat": 19.2467, "lng": -99.0108,
                "municipio": "Tláhuac", "zone": "sur"},
    "Tlalnepantla":   {"id": 266, "lat": 19.537, "lng": -99.195,
                       "municipio": "Tlalnepantla de Baz", "zone": "norte"},
    "UAM Xochimilco": {"id": 269, "lat": 19.304, "lng": -99.104,
                        "municipio": "Xochimilco", "zone": "sur"},
    "Villa de las Flores": {"id": 270, "lat": 19.6575, "lng": -99.0967,
                            "municipio": "Coacalco de Berriozábal", "zone": "norte"},
}

STATION_IDS_LIST: list[int] = [m["id"] for m in STATIONS_META.values()]
"""List of all SINAICA station IDs, for mass-fetching."""

POLLUTANTS: list[str] = ["NO2", "PM10", "PM2.5"]
"""Default set of pollutants."""

# --------------------------------------------------------------------------- #
# WHO air quality guidelines
# --------------------------------------------------------------------------- #
WHO_LIMITS: dict[str, float] = {
    "PM2.5": 5,
    "PM10": 15,
}
"""Annual mean WHO guideline limits in µg/m³."""

# --------------------------------------------------------------------------- #
# Zone colour and label constants
# --------------------------------------------------------------------------- #
ZONE_COLORS: dict[str, str] = {
    "norte": "#e74c3c",
    "centro": "#f39c12",
    "sur": "#27ae60",
}
"""Colours for each zone (used in maps and bar charts)."""

ZONE_LABELS: dict[str, str] = {
    "norte": "Norte (nororiente)",
    "centro": "Centro",
    "sur": "Sur (reference)",
}
"""Human-readable labels for each zone."""

# Pre-computed station lists per zone
_STATIONS_BY_ZONE: dict[str, list[str]] = {}
for _name, _meta in STATIONS_META.items():
    _z = _meta["zone"]
    _STATIONS_BY_ZONE.setdefault(_z, []).append(_name)

STATIONS_BY_ZONE: dict[str, list[str]] = dict(_STATIONS_BY_ZONE)
"""dict mapping zone -> list of station names."""

# --------------------------------------------------------------------------- #
# Lookup helpers
# --------------------------------------------------------------------------- #


def get_zone(name: str) -> str:
    """Return the zone key for a station name.

    Examples
    --------
    >>> get_zone("GAM")
    'norte'
    >>> get_zone("Pedregal")
    'sur'
    """
    return STATIONS_META.get(name, {}).get("zone", "")


def get_color(name_or_zone: str) -> str:
    """Return the zone colour for a station name *or* a zone key.

    Examples
    --------
    >>> get_color("GAM")
    '#e74c3c'
    >>> get_color("norte")
    '#e74c3c'
    """
    if name_or_zone in STATIONS_META:
        zone = STATIONS_META[name_or_zone]["zone"]
    else:
        zone = name_or_zone
    return ZONE_COLORS.get(zone, "#888888")


def get_label(name_or_zone: str) -> str:
    """Return the human-readable zone label.

    Examples
    --------
    >>> get_label("GAM")
    'Norte (nororiente)'
    >>> get_label("norte")
    'Norte (nororiente)'
    """
    if name_or_zone in STATIONS_META:
        zone = STATIONS_META[name_or_zone]["zone"]
    else:
        zone = name_or_zone
    return ZONE_LABELS.get(zone, zone)


# --------------------------------------------------------------------------- #
# Aggregation helpers
# --------------------------------------------------------------------------- #


def zone_stats(stats_df, station_names):
    """Compute aggregate mean for a zone across pollutants.

    Parameters
    ----------
    stats_df : pd.DataFrame
        Output of ``compute_annual_stats``.
    station_names : list[str]
        Station names belonging to the zone.

    Returns
    -------
    pd.DataFrame
        Grouped by pollutant with mean, std, min, max columns.
    """
    subset = stats_df[stats_df["station_name"].isin(station_names)]
    return subset.groupby("pollutant")["annual_mean"].agg(["mean", "std", "min", "max"])
