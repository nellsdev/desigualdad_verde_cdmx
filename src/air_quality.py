"""
Air quality data API for Mexican monitoring stations (SINAICA).

Provides programmatic access to the SINAICA data portal
(https://sinaica.inecc.gob.mx/) with pandas-friendly return types.
Hourly measurements are fetched via the internal JSON endpoint and
returned as clean DataFrames with consistent column names.

Typical usage::

    from src.air_quality import fetch_station_data, compute_annual_stats

    df = fetch_station_data(station_id=258, pollutant="NO2",
                            start_date="2023-01-01", end_date="2023-12-31")
    stats = compute_annual_stats(df, year=2023)
    print(stats)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional

import pandas as pd
import requests

# --------------------------------------------------------------------------- #
# Public constants
# --------------------------------------------------------------------------- #

STATION_IDS: dict[str, int] = {
    "Nezahualcoyotl": 258,
    "GAM": 302,
    "Iztapalapa": 268,
    "Centro": 256,
    "Pedregal": 259,
    "Ecatepec": 271,
    "Tlalnepantla": 266,
    "Naucalpan": 243,
    "CCA": 245,
    "UAM Xochimilco": 269,
    "Benito Juárez": 300,
    "Hospital General": 251,
    "Ajusco Medio": 242,
}
"""Mapping of common station names to SINAICA identifiers.

Notes
----
- Centro refers to the Merced (MER) station in the historic centre.
- CCA is the Centro de Ciencias de la Atmósfera at Ciudad Universitaria (UNAM).
- Ecatepec data comes from the Xalostoc (XAL) station.
- Naucalpan uses the Atizapán (ATI) station, the closest available
  monitoring site in the Valle de México network.
- Hospital General (HGM) is the Hospital General de México in Cuauhtémoc.
- Ajusco Medio (AJM) is in the Tlalpan borough, southern CDMX.
"""

STATION_NAMES: dict[int, str] = {v: k for k, v in STATION_IDS.items()}
"""Reverse lookup: SINAICA ID -> common name."""

POLLUTANT_CODES: dict[str, str] = {
    "SO2": "SO2",
    "NO2": "NO2",
    "CO": "CO",
    "O3": "O3",
    "PM10": "PM10",
    "PM2.5": "PM2.5",
    "NO": "NO",
    "NOx": "NOx",
}
"""Pollutant codes recognised by the SINAICA endpoint."""

POLLUTANT_UNITS: dict[str, str] = {
    "SO2": "ppm",
    "NO2": "ppm",
    "CO": "ppm",
    "O3": "ppm",
    "PM10": "µg/m³",
    "PM2.5": "µg/m³",
    "NO": "ppm",
    "NOx": "ppm",
}
"""Measurement units per pollutant."""

# --------------------------------------------------------------------------- #
# Internal constants
# --------------------------------------------------------------------------- #

_BASE_URL: str = "https://sinaica.inecc.gob.mx"
_DATA_ENDPOINT: str = f"{_BASE_URL}/lib/libd/cnxn.php"
_SESSION_TIMEOUT: int = 30
_REQUEST_DELAY: float = 0.5  # seconds between requests (rate limiting)

# --------------------------------------------------------------------------- #
# Custom exceptions
# --------------------------------------------------------------------------- #


class SinaicaError(Exception):
    """Base exception for SINAICA API errors."""


class SinaicaConnectionError(SinaicaError):
    """Raised when the SINAICA server is unreachable or returns an error."""


class SinaicaDataError(SinaicaError):
    """Raised when the response has an unexpected format or is empty."""


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


def _build_session() -> requests.Session:
    """Return a session primed with SINAICA cookies.

    The portal sets a session cookie on the initial page visit; this helper
    replicates that handshake so subsequent POST calls are accepted.
    """
    session = requests.Session()
    session.get(f"{_BASE_URL}/data.php?tipo=V", timeout=_SESSION_TIMEOUT)
    return session


def _post_json(
    payload: dict[str, Any],
    session: Optional[requests.Session] = None,
) -> list[dict[str, Any]]:
    """POST to the JSON data endpoint and return the decoded list.

    Parameters
    ----------
    payload : dict
        Form parameters sent to ``cnxn.php``.
    session : requests.Session or None
        Reusable session.  A new one is created if omitted.

    Returns
    -------
    list[dict]
        Parsed JSON response (array of record objects).

    Raises
    ------
    SinaicaConnectionError
        On HTTP or connection failures.
    SinaicaDataError
        If the response is not valid JSON or not a list.
    """
    close_session = session is None
    session = session or _build_session()

    try:
        resp = session.post(_DATA_ENDPOINT, data=payload, timeout=_SESSION_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise SinaicaConnectionError(
            f"Request failed for payload {payload}: {exc}"
        ) from exc
    finally:
        if close_session:
            session.close()

    try:
        data: list[dict[str, Any]] = json.loads(resp.text)
    except json.JSONDecodeError as exc:
        raise SinaicaDataError(
            f"Invalid JSON response for payload {payload}: {resp.text[:200]}"
        ) from exc

    if not isinstance(data, list):
        raise SinaicaDataError(
            f"Expected a JSON array, got {type(data).__name__}: {resp.text[:200]}"
        )

    return data


def _convert_to_dataframe(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalise raw SINAICA records into a clean DataFrame.

    The JSON response from ``getDatos`` uses Spanish column names.
    This function maps them to English, parses dates, and resolves
    the effective validated value.

    Value resolution priority:
    1. ``valorAct`` (validated by a technician)
    2. ``valorOrig`` (original instrument reading)

    Parameters
    ----------
    records : list[dict]
        Raw records from ``getDatos``.

    Returns
    -------
    pd.DataFrame
        Columns: station_id, station_name, date, hour, pollutant,
        raw_value, validated_value, value, is_valid, unit.
    """
    if not records:
        return pd.DataFrame(
            columns=[
                "station_id",
                "station_name",
                "date",
                "hour",
                "pollutant",
                "raw_value",
                "validated_value",
                "value",
                "is_valid",
                "unit",
            ]
        )

    rows = []
    for rec in records:
        validated = rec.get("valorAct")
        raw = rec.get("valorOrig")
        rows.append(
            {
                "station_id": rec.get("estacionesId"),
                "station_name": STATION_NAMES.get(rec.get("estacionesId"), "Unknown"),
                "date": rec.get("fecha"),
                "hour": rec.get("hora"),
                "pollutant": rec.get("parametro"),
                "raw_value": raw,
                "validated_value": validated,
                "value": validated if validated is not None else raw,
                "is_valid": bool(rec.get("validoAct", 0)),
                "unit": POLLUTANT_UNITS.get(rec.get("parametro"), ""),
            }
        )

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df.sort_values(["station_id", "date", "hour"]).reset_index(drop=True)
    return df


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def list_stations(
    session: Optional[requests.Session] = None,
) -> pd.DataFrame:
    """Return metadata for all stations in the Valle de México network.

    The network is pre-defined (CDMX + Estado de México stations);
    this function enriches the hardcoded map with additional information
    available through the SINAICA portal.

    Parameters
    ----------
    session : requests.Session or None
        Reusable HTTP session.

    Returns
    -------
    pd.DataFrame
        Columns: station_id, name, common_name.
    """
    records = []
    for common_name, station_id in STATION_IDS.items():
        records.append(
            {
                "station_id": station_id,
                "name": common_name,
            }
        )
    return pd.DataFrame(records)


def list_pollutants(
    station_id: int,
    session: Optional[requests.Session] = None,
) -> pd.DataFrame:
    """Return the pollutants measured by a given station.

    Parameters
    ----------
    station_id : int
        SINAICA station identifier.
    session : requests.Session or None
        Reusable HTTP session.

    Returns
    -------
    pd.DataFrame
        Columns: pollutant_id, pollutant_name.
    """
    payload: dict[str, Any] = {
        "metodo": "getParamsPorEstAjax",
        "estId": str(station_id),
        "tipoDatos": "V",
    }
    data = _post_json(payload, session)

    if not data:
        return pd.DataFrame(columns=["pollutant_id", "pollutant_name"])

    return pd.DataFrame(data).rename(
        columns={"id": "pollutant_id", "nombre": "pollutant_name"}
    )


def fetch_station_data(
    station_id: int,
    pollutant: str,
    start_date: str | date,
    end_date: str | date,
    session: Optional[requests.Session] = None,
    raw_only: bool = False,
) -> pd.DataFrame:
    """Fetch hourly air quality data for a single station.

    Parameters
    ----------
    station_id : int
        SINAICA station identifier.
    pollutant : str
        Pollutant code (e.g. ``"NO2"``, ``"PM10"``, ``"O3"``).
    start_date : str or date
        Inclusive start date (``"YYYY-MM-DD"`` or ``datetime.date``).
    end_date : str or date
        Inclusive end date.
    session : requests.Session or None
        Reusable HTTP session.  Created automatically if omitted.
    raw_only : bool
        If True, skip validated values and return only ``valorOrig``.
        Useful when querying the current year (not yet validated).

    Returns
    -------
    pd.DataFrame
        Columns: station_id, station_name, date, hour, pollutant,
        raw_value, validated_value, value, is_valid, unit.

    Raises
    ------
    SinaicaError
        On connection or data errors.
    """
    start = start_date if isinstance(start_date, str) else start_date.isoformat()
    end = end_date if isinstance(end_date, str) else end_date.isoformat()

    # Build the payload matching the portal's AJAX call.
    payload: dict[str, Any] = {
        "metodo": "getDatos",
        "estacionesId": str(station_id),
        "fechaInit": start,
        "fechaFin": end,
        "paramId": pollutant,
        "nivel": 1000,  # show all validation levels
        "inc": 1,  # include data rows
    }

    records = _post_json(payload, session)
    df = _convert_to_dataframe(records)

    if df.empty:
        return df

    if raw_only:
        df["value"] = df["raw_value"]
        df["is_valid"] = df["raw_value"].notna()

    return df


def fetch_multiple_stations(
    station_ids: list[int],
    pollutant: str,
    start_date: str | date,
    end_date: str | date,
    raw_only: bool = False,
) -> pd.DataFrame:
    """Fetch hourly data for several stations and combine the results.

    Uses a single HTTP session and enforces a small delay between
    requests to avoid overwhelming the SINAICA server.

    Parameters
    ----------
    station_ids : list[int]
        One or more SINAICA station identifiers.
    pollutant : str
        Pollutant code.
    start_date : str or date
        Inclusive start date.
    end_date : str or date
        Inclusive end date.
    raw_only : bool
        If True, return only raw (unvalidated) values.

    Returns
    -------
    pd.DataFrame
        Concatenated data for all requested stations.
    """
    session = _build_session()
    frames: list[pd.DataFrame] = []

    try:
        for sid in station_ids:
            df = fetch_station_data(
                station_id=sid,
                pollutant=pollutant,
                start_date=start_date,
                end_date=end_date,
                session=session,
                raw_only=raw_only,
            )
            frames.append(df)
            time.sleep(_REQUEST_DELAY)
    finally:
        session.close()

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True).sort_values(
        ["station_id", "date", "hour"]
    )


def fetch_multiple_pollutants(
    station_ids: list[int],
    pollutants: list[str],
    start_date: str | date,
    end_date: str | date,
    raw_only: bool = False,
) -> pd.DataFrame:
    """Fetch hourly data for multiple stations **and** multiple pollutants.

    Iterates over all (station, pollutant) combinations and concatenates
    the results.  A single HTTP session is reused across all requests
    and a small delay is enforced between calls.

    Parameters
    ----------
    station_ids : list[int]
        One or more SINAICA station identifiers.
    pollutants : list[str]
        Pollutant codes (e.g. ``["NO2", "PM10", "PM2.5"]``).
    start_date : str or date
        Inclusive start date.
    end_date : str or date
        Inclusive end date.
    raw_only : bool
        If True, return only raw (unvalidated) values.

    Returns
    -------
    pd.DataFrame
        Concatenated data for every (station, pollutant) combination.
    """
    session = _build_session()
    frames: list[pd.DataFrame] = []

    try:
        for pid in pollutants:
            for sid in station_ids:
                df = fetch_station_data(
                    station_id=sid,
                    pollutant=pid,
                    start_date=start_date,
                    end_date=end_date,
                    session=session,
                    raw_only=raw_only,
                )
                frames.append(df)
                time.sleep(_REQUEST_DELAY)
    finally:
        session.close()

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True).sort_values(
        ["station_id", "date", "hour", "pollutant"]
    )


def compute_annual_stats(
    df: pd.DataFrame,
    year: Optional[int] = None,
) -> pd.DataFrame:
    """Compute annual statistics for each station and pollutant.

    Parameters
    ----------
    df : pd.DataFrame
        Data returned by ``fetch_station_data`` or
        ``fetch_multiple_stations``.
    year : int or None
        Filter to a specific year before computing.  If None, uses all
        available data.

    Returns
    -------
    pd.DataFrame
        Columns: station_id, station_name, pollutant, year, annual_mean,
        p05, p25, p50, p75, p95, max_value, count_valid, unit.
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                "station_id",
                "station_name",
                "pollutant",
                "year",
                "annual_mean",
                "p05",
                "p25",
                "p50",
                "p75",
                "p95",
                "max_value",
                "count_valid",
                "unit",
            ]
        )

    working = df.copy()
    working["year"] = pd.to_datetime(working["date"]).dt.year

    if year is not None:
        working = working[working["year"] == year].copy()

    if working.empty:
        return pd.DataFrame()

    numeric = working[pd.to_numeric(working["value"], errors="coerce").notna()].copy()
    numeric["value"] = pd.to_numeric(numeric["value"], errors="coerce")

    def _stats(group: pd.DataFrame) -> dict[str, Any]:
        vals = group["value"].dropna()
        unit = group["unit"].iloc[0] if "unit" in group.columns else ""
        return {
            "station_id": group["station_id"].iloc[0],
            "station_name": group["station_name"].iloc[0],
            "pollutant": group["pollutant"].iloc[0],
            "year": group["year"].iloc[0],
            "annual_mean": vals.mean(),
            "p05": vals.quantile(0.05),
            "p25": vals.quantile(0.25),
            "p50": vals.median(),
            "p75": vals.quantile(0.75),
            "p95": vals.quantile(0.95),
            "max_value": vals.max(),
            "count_valid": len(vals),
            "unit": unit,
        }

    results: list[dict[str, Any]] = []
    for (sid, yr, pol), group in numeric.groupby(
        ["station_id", "year", "pollutant"], sort=False
    ):
        results.append(_stats(group))
    result = pd.DataFrame(results)
    return result.sort_values(["station_id", "year", "pollutant"]).reset_index(drop=True)


def download_csv(
    station_id: int,
    pollutant: str,
    start_date: str | date,
    end_date: str | date,
    output_path: str,
) -> str:
    """Download a CSV file directly from the SINAICA portal.

    Uses the portal's ``descarga.php`` endpoint to generate a CSV
    identical to what the "Descargar" button produces in the browser.

    .. caution::
       This endpoint sometimes returns the HTML page instead of a CSV
       when the session cookie is missing.  The JSON-based functions
       (``fetch_station_data``) are more reliable.

    Parameters
    ----------
    station_id : int
        SINAICA station identifier.
    pollutant : str
        Pollutant code.
    start_date : str or date
        Inclusive start date.
    end_date : str or date
        Inclusive end date.
    output_path : str
        Destination file path (e.g. ``"data/nez_no2_2023.csv"``).

    Returns
    -------
    str
        The ``output_path`` on success.

    Raises
    ------
    SinaicaConnectionError
        If the CSV download fails.
    """
    start = start_date if isinstance(start_date, str) else start_date.isoformat()
    end = end_date if isinstance(end_date, str) else end_date.isoformat()

    session = _build_session()
    url = f"{_BASE_URL}/lib/j/php/descarga.php"
    payload = {
        "fechaInit": start,
        "fechaFin": end,
        "estacionesId": str(station_id),
        "param": pollutant,
    }

    try:
        resp = session.post(url, data=payload, timeout=_SESSION_TIMEOUT)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        disposition = resp.headers.get("content-disposition", "")

        if "text/html" in content_type and len(resp.text) > 1000:
            raise SinaicaConnectionError(
                "Received HTML instead of CSV. "
                "The SINAICA download endpoint may require a fresh browser session. "
                "Use fetch_station_data() instead."
            )

        with open(output_path, "wb") as f:
            f.write(resp.content)
    except requests.RequestException as exc:
        raise SinaicaConnectionError(f"CSV download failed: {exc}") from exc
    finally:
        session.close()

    return output_path
