"""Peak-Event & Resiliency Sentinel tools.

Signals (all public data):
  * Demand: Google Trends top rising terms (BigQuery public dataset), weekly.
  * Calendar: published dates of major retail peak events.
  * Weather: Open-Meteo 7-day forecast (no API key).
  * Unrest: GDELT 2.0 events (BigQuery public dataset), daily.

Scoring is deterministic so the same data always produces the same advisory.
The model writes the narrative; it never invents the numbers.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import urllib.parse
import urllib.request
from collections import defaultdict

from .charts import bar_chart, trend_chart

MAX_BYTES_BILLED = 20 * 1024**3  # 20 GB guardrail per query
HTTP_HEADERS = {"User-Agent": "curl/8.5.0"}

# region -> (published location, lat, lon, Trends country, GDELT FIPS country,
#            GDELT ADM1 code or "")
REGIONS: dict[str, tuple[str, float, float, str, str, str]] = {
    "us-east1": ("Moncks Corner, South Carolina", 33.20, -80.01, "US", "US", "USSC"),
    "us-east4": ("Ashburn, Virginia", 39.04, -77.49, "US", "US", "USVA"),
    "us-east5": ("Columbus, Ohio", 39.96, -83.00, "US", "US", "USOH"),
    "us-central1": ("Council Bluffs, Iowa", 41.26, -95.86, "US", "US", "USIA"),
    "us-south1": ("Dallas, Texas", 32.78, -96.80, "US", "US", "USTX"),
    "us-west1": ("The Dalles, Oregon", 45.60, -121.18, "US", "US", "USOR"),
    "us-west2": ("Los Angeles, California", 34.05, -118.24, "US", "US", "USCA"),
    "us-west3": ("Salt Lake City, Utah", 40.76, -111.89, "US", "US", "USUT"),
    "us-west4": ("Las Vegas, Nevada", 36.17, -115.14, "US", "US", "USNV"),
    "northamerica-northeast1": ("Montreal, Canada", 45.50, -73.57, "CA", "CA", ""),
    "northamerica-northeast2": ("Toronto, Canada", 43.65, -79.38, "CA", "CA", ""),
    "southamerica-east1": ("Sao Paulo, Brazil", -23.55, -46.63, "BR", "BR", ""),
    "europe-west1": ("St. Ghislain, Belgium", 50.45, 3.82, "BE", "BE", ""),
    "europe-west2": ("London, UK", 51.51, -0.13, "GB", "UK", ""),
    "europe-west3": ("Frankfurt, Germany", 50.11, 8.68, "DE", "GM", ""),
    "europe-west4": ("Eemshaven, Netherlands", 53.44, 6.83, "NL", "NL", ""),
    "europe-west9": ("Paris, France", 48.86, 2.35, "FR", "FR", ""),
    "asia-south1": ("Mumbai, India", 19.08, 72.88, "IN", "IN", ""),
    "asia-northeast1": ("Tokyo, Japan", 35.68, 139.69, "JP", "JA", ""),
    "asia-southeast1": ("Jurong West, Singapore", 1.34, 103.71, "SG", "SN", ""),
    "australia-southeast1": ("Sydney, Australia", -33.87, 151.21, "AU", "AS", ""),
}

# Published dates of major retail peaks, keyed by Trends country code.
PEAK_EVENTS: list[tuple[str, str, tuple[str, ...]]] = [
    ("Diwali", "2026-11-08", ("IN", "SG")),
    ("Singles Day (11.11)", "2026-11-11", ("SG",)),
    ("Black Friday", "2026-11-27",
     ("US", "CA", "GB", "DE", "FR", "NL", "BE", "BR", "AU")),
    ("Cyber Monday", "2026-11-30", ("US", "CA", "GB", "DE", "FR", "NL", "BE", "BR", "AU")),
    ("Christmas peak", "2026-12-24",
     ("US", "CA", "GB", "DE", "FR", "NL", "BE", "BR", "AU", "SG", "JP")),
    ("Boxing Day", "2026-12-26", ("GB", "CA", "AU")),
    ("New Year shopping (Hatsuuri)", "2027-01-02", ("JP",)),
    ("Lunar New Year", "2027-02-06", ("SG",)),
]

RETAIL_PATTERN = re.compile(
    r"\b(black friday|cyber monday|prime day|big deal days|deals?|sales?|"
    r"discounts?|coupons?|promo|boxing day|singles day|11\.11|diwali|amazon|"
    r"walmart|target|costco|best buy|shein|temu|flipkart|myntra|mercado libre|"
    r"shopee|lazada|rakuten|zalando|argos|presale|pre-order|restock|tickets?|"
    r"ticketmaster|iphone|playstation|xbox|nintendo)\b"
)

WEATHER_LIMITS = {
    # variable: (elevated, critical, label, unit, direction)
    "wind_gusts_10m_max": (60, 90, "wind gusts", "km/h", "max"),
    "temperature_2m_max": (35, 40, "heat", "°C", "max"),
    "temperature_2m_min": (-10, -20, "extreme cold", "°C", "min"),
    "precipitation_sum": (40, 100, "heavy rain", "mm", "max"),
    "snowfall_sum": (5, 20, "snow", "cm", "max"),
}

DOCS = {
    "quotas": "https://cloud.google.com/docs/quotas/view-manage",
    "reservations": "https://cloud.google.com/compute/docs/instances/future-reservations-overview",
    "autoscaler": "https://cloud.google.com/kubernetes-engine/docs/concepts/cluster-autoscaler",
    "freeze": "https://cloud.google.com/deploy/docs/deploy-policy",
    "dr": "https://cloud.google.com/architecture/dr-scenarios-planning-guide",
    "armor": "https://cloud.google.com/armor/docs/rate-limiting-overview",
    "support": "https://cloud.google.com/support/docs/premium",
    "status": "https://status.cloud.google.com/",
}

_bq_client = None


def _bq():
  global _bq_client
  if _bq_client is None:
    from google.cloud import bigquery  # pylint: disable=g-import-not-at-top

    _bq_client = bigquery.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
  return _bq_client


def _query(sql: str, params: list) -> list[dict]:
  from google.cloud import bigquery  # pylint: disable=g-import-not-at-top

  cfg = bigquery.QueryJobConfig(
      query_parameters=params, maximum_bytes_billed=MAX_BYTES_BILLED
  )
  return [dict(r.items()) for r in _bq().query(sql, job_config=cfg).result()]


def _param(name: str, kind: str, value):
  from google.cloud import bigquery  # pylint: disable=g-import-not-at-top

  if isinstance(value, list):
    return bigquery.ArrayQueryParameter(name, kind, value)
  return bigquery.ScalarQueryParameter(name, kind, value)


def _today() -> dt.date:
  return dt.datetime.now(dt.timezone.utc).date()


# ---------------------------------------------------------------- demand ---

_TRENDS_US = "bigquery-public-data.google_trends.top_rising_terms"
_TRENDS_INTL = "bigquery-public-data.google_trends.international_top_rising_terms"


def _latest_refresh(table: str) -> dt.date | None:
  rows = _query(
      f"SELECT MAX(refresh_date) AS r FROM `{table}` "
      "WHERE refresh_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)",
      [],
  )
  return rows[0]["r"] if rows else None


def _trends_rows(countries: set[str]) -> list[dict]:
  """Returns (cc, area, term, gain, week, refresh) rows for the latest week."""
  out: list[dict] = []
  if "US" in countries:
    r = _latest_refresh(_TRENDS_US)
    if r:
      out += _query(
          f"""
          SELECT 'US' AS cc, dma_name AS area, term, percent_gain AS gain,
                 week, refresh_date AS refresh
          FROM `{_TRENDS_US}`
          WHERE refresh_date = @r
            AND week = (SELECT MAX(week) FROM `{_TRENDS_US}` WHERE refresh_date = @r)
          """,
          [_param("r", "DATE", r)],
      )
  intl = sorted(c for c in countries if c != "US")
  if intl:
    r = _latest_refresh(_TRENDS_INTL)
    if r:
      out += _query(
          f"""
          SELECT country_code AS cc, region_name AS area, term,
                 percent_gain AS gain, week, refresh_date AS refresh
          FROM `{_TRENDS_INTL}`
          WHERE refresh_date = @r AND country_code IN UNNEST(@ccs)
            AND week = (SELECT MAX(week) FROM `{_TRENDS_INTL}` WHERE refresh_date = @r)
          """,
          [_param("r", "DATE", r), _param("ccs", "STRING", intl)],
      )
  return out


def summarize_demand(rows: list[dict], cc: str) -> dict:
  """Aggregates Trends rows for one country into a demand signal."""
  rows = [r for r in rows if r["cc"] == cc]
  if not rows:
    return {"level": "Unknown", "points": 0,
            "note": f"No Google Trends rows for {cc} in the last 14 days."}
  areas = {r["area"] for r in rows}
  by_term: dict[str, dict] = {}
  for r in rows:
    t = by_term.setdefault(r["term"], {"areas": set(), "gain": 0})
    t["areas"].add(r["area"])
    t["gain"] = max(t["gain"], r["gain"] or 0)
  retail_terms = {t for t in by_term if RETAIL_PATTERN.search(t.lower())}
  retail_areas = {r["area"] for r in rows if r["term"] in retail_terms}
  breadth = round(100 * len(retail_areas) / len(areas), 1)
  points = 30 if breadth >= 20 else 15 if breadth >= 5 else 0
  level = "Critical" if breadth >= 40 else "Elevated" if points else "Low"

  def top(terms):
    ranked = sorted(terms, key=lambda t: (-len(by_term[t]["areas"]), -by_term[t]["gain"]))
    return [
        {"term": t, "areas": len(by_term[t]["areas"]), "max_gain_pct": by_term[t]["gain"]}
        for t in ranked[:8]
    ]

  return {
      "level": level,
      "points": points,
      "week_of": str(rows[0]["week"]),
      "refresh_date": str(rows[0]["refresh"]),
      "areas_tracked": len(areas),
      "area_type": "metro areas (DMAs)" if cc == "US" else "regions",
      "retail_breadth_pct": breadth,
      "retail_terms": top(retail_terms),
      "top_rising_terms": top(by_term),
  }


def calendar_signal(cc: str, today: dt.date | None = None) -> dict:
  today = today or _today()
  upcoming = []
  for name, day, ccs in PEAK_EVENTS:
    days = (dt.date.fromisoformat(day) - today).days
    if cc in ccs and 0 <= days <= 60:
      upcoming.append({"event": name, "date": day, "days_away": days})
  nearest = min((e["days_away"] for e in upcoming), default=None)
  points = 0 if nearest is None else 20 if nearest <= 14 else 10 if nearest <= 45 else 0
  level = "Elevated" if points else "Low"
  return {"level": level, "points": points, "upcoming_events": upcoming}


# --------------------------------------------------------------- weather ---

def _fetch_weather(regions: list[str]) -> dict[str, dict]:
  lats = ",".join(str(REGIONS[r][1]) for r in regions)
  lons = ",".join(str(REGIONS[r][2]) for r in regions)
  qs = urllib.parse.urlencode({
      "latitude": lats, "longitude": lons, "forecast_days": 7, "timezone": "UTC",
      "daily": ",".join(WEATHER_LIMITS),
  })
  req = urllib.request.Request(
      f"https://api.open-meteo.com/v1/forecast?{qs}", headers=HTTP_HEADERS
  )
  data = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
  if isinstance(data, dict):
    data = [data]
  return {r: d.get("daily", {}) for r, d in zip(regions, data)}


def summarize_weather(daily: dict) -> dict:
  """Turns an Open-Meteo `daily` block into a hazard signal."""
  days = daily.get("time") or []
  if not days:
    return {"level": "Unknown", "points": 0, "note": "No forecast returned."}
  hazards, worst = [], "Low"
  for var, (elev, crit, label, unit, how) in WEATHER_LIMITS.items():
    vals = [v for v in daily.get(var) or [] if v is not None]
    if not vals:
      continue
    peak = max(vals) if how == "max" else min(vals)
    hit_c = peak >= crit if how == "max" else peak <= crit
    hit_e = peak >= elev if how == "max" else peak <= elev
    if hit_c or hit_e:
      idx = (daily[var]).index(peak)
      sev = "Critical" if hit_c else "Elevated"
      hazards.append({"hazard": label, "peak": peak, "unit": unit,
                      "date": days[idx], "severity": sev})
      if sev == "Critical" or worst == "Low":
        worst = max(worst, sev, key=["Low", "Elevated", "Critical"].index)
  points = 40 if worst == "Critical" else 20 if worst == "Elevated" else 0
  gusts = daily.get("wind_gusts_10m_max") or []
  return {
      "level": worst,
      "points": points,
      "forecast_window": f"{days[0]} to {days[-1]}",
      "hazards": hazards,
      "peak_gust_kmh": max([g for g in gusts if g is not None], default=None),
      "max_temp_c": max([t for t in daily.get("temperature_2m_max") or [] if t is not None], default=None),
      "min_temp_c": min([t for t in daily.get("temperature_2m_min") or [] if t is not None], default=None),
      "_days": days,
      "_gusts": gusts,
  }


# ---------------------------------------------------------------- unrest ---

_GDELT = "gdelt-bq.gdeltv2.events_partitioned"


def _gdelt_rows(regions: list[str]) -> list[dict]:
  ccs = sorted({REGIONS[r][4] for r in regions})
  adm1s = sorted({REGIONS[r][5] for r in regions if REGIONS[r][5]}) or ["-"]
  start = int((_today() - dt.timedelta(days=37)).strftime("%Y%m%d"))
  return _query(
      f"""
      SELECT ActionGeo_CountryCode AS cc,
             IF(ActionGeo_ADM1Code IN UNNEST(@adm1s), ActionGeo_ADM1Code, '') AS adm1,
             PARSE_DATE('%Y%m%d', CAST(SQLDATE AS STRING)) AS d,
             COUNT(*) AS total,
             COUNTIF(QuadClass = 4 OR CAST(EventRootCode AS STRING) = '14') AS unrest
      FROM `{_GDELT}`
      WHERE _PARTITIONTIME >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 39 DAY))
        AND SQLDATE >= @start
        AND ActionGeo_CountryCode IN UNNEST(@ccs)
      GROUP BY 1, 2, 3
      """,
      [_param("ccs", "STRING", ccs), _param("adm1s", "STRING", adm1s),
       _param("start", "INT64", start)],
  )


def summarize_unrest(rows: list[dict], fips: str, adm1: str,
                     place: str, today: dt.date | None = None) -> dict:
  """Compares protest/conflict share of news events: last 7 days vs prior 30."""
  today = today or _today()
  scope, label = "state", place
  sel = [r for r in rows if r["cc"] == fips and adm1 and r["adm1"] == adm1]
  if sum(r["total"] for r in sel) < 300:
    sel = [r for r in rows if r["cc"] == fips]
    scope, label = "country", place.split(", ")[-1]
  daily: dict[dt.date, list[int]] = defaultdict(lambda: [0, 0])
  for r in sel:
    daily[r["d"]][0] += r["total"]
    daily[r["d"]][1] += r["unrest"]
  if not daily:
    return {"level": "Unknown", "points": 0, "note": "No GDELT events found."}
  recent = [today - dt.timedelta(days=i) for i in range(1, 8)]
  prior = [today - dt.timedelta(days=i) for i in range(8, 38)]

  def share(days):
    tot = sum(daily[d][0] for d in days if d in daily)
    un = sum(daily[d][1] for d in days if d in daily)
    return (un / tot if tot else 0.0), un

  s_recent, n_recent = share(recent)
  s_prior, _ = share(prior)
  ratio = round(s_recent / s_prior, 2) if s_prior else 0.0
  if n_recent < 30:
    level = "Low"
  else:
    level = "Critical" if ratio >= 2.0 else "Elevated" if ratio >= 1.4 else "Low"
  points = 40 if level == "Critical" else 20 if level == "Elevated" else 0
  chart_days = sorted(d for d in daily if d < today)[-21:]
  return {
      "level": level,
      "points": points,
      "scope": f"{scope} ({label})",
      "unrest_share_last_7d_pct": round(100 * s_recent, 1),
      "unrest_share_prior_30d_pct": round(100 * s_prior, 1),
      "ratio_vs_baseline": ratio,
      "unrest_events_last_7d": n_recent,
      "data_through": str(max(daily)),
      "_days": [d.strftime("%m-%d") for d in chart_days],
      "_share": [round(100 * daily[d][1] / daily[d][0], 1) if daily[d][0] else 0.0
                 for d in chart_days],
  }


# --------------------------------------------------------------- scoring ---

def score(signals: dict) -> tuple[int, str]:
  pts = min(100, sum(s.get("points", 0) for s in signals.values()))
  levels = [s.get("level") for s in signals.values()]
  if pts >= 60 or "Critical" in levels:
    return pts, "Critical"
  if pts >= 20 or "Elevated" in levels:
    return pts, "Elevated"
  return pts, "Low"


def recommendations(region: str, signals: dict, level: str) -> list[dict]:
  recs: list[dict] = []
  demand_hot = signals["demand"].get("points", 0) or signals["calendar"].get("points", 0)
  if demand_hot:
    recs += [
        {"action": f"Review regional quotas in {region} and request increases ahead of the peak",
         "owner": "Customer platform team, TAM to track", "link": DOCS["quotas"]},
        {"action": "Secure capacity with future reservations for the peak window",
         "owner": "Customer platform team", "link": DOCS["reservations"]},
        {"action": "Load-test and raise autoscaler max limits so scale-out is not capped",
         "owner": "Customer SRE", "link": DOCS["autoscaler"]},
        {"action": "Agree a code-freeze window and enforce it with Cloud Deploy deploy policies",
         "owner": "Customer release management", "link": DOCS["freeze"]},
        {"action": "Add Cloud Armor rate limiting to absorb bot and scalper traffic",
         "owner": "Customer security team", "link": DOCS["armor"]},
        {"action": "Register the event with Google Cloud support for event management",
         "owner": "TAM", "link": DOCS["support"]},
    ]
  if signals["weather"].get("points", 0):
    recs += [
        {"action": "Walk through the DR runbook and confirm failover to a second region is tested",
         "owner": "Customer SRE, TAM to facilitate", "link": DOCS["dr"]},
        {"action": "Confirm on-call coverage for staff and offices in the affected area",
         "owner": "Customer operations", "link": DOCS["dr"]},
    ]
  if signals["unrest"].get("points", 0):
    recs += [
        {"action": "Review multi-region traffic steering so user traffic can shift away quickly",
         "owner": "Customer SRE", "link": DOCS["dr"]},
        {"action": "Subscribe incident channels to the Google Cloud status dashboard",
         "owner": "Customer operations", "link": DOCS["status"]},
    ]
  if level == "Low":
    recs.append({"action": "No special action this week; keep the standard ORR cadence",
                 "owner": "TAM", "link": DOCS["dr"]})
  return recs


# ----------------------------------------------------------------- tools ---

def list_regions() -> dict:
  """Lists the Google Cloud regions the Sentinel can assess.

  Returns:
    A dict mapping region IDs to their published location.
  """
  return {"regions": {r: v[0] for r, v in REGIONS.items()}}


def _resolve(regions: list[str]) -> tuple[list[str], list[str]]:
  if not regions or any(r.strip().lower() in ("all", "*") for r in regions):
    return list(REGIONS), []
  known, unknown = [], []
  for r in regions:
    key = r.strip().lower()
    (known if key in REGIONS else unknown).append(key)
  return list(dict.fromkeys(known)), unknown


def assess_regions(regions: list[str]) -> dict:
  """Scores production-readiness risk for Google Cloud regions.

  Combines four public signals per region: Google Trends retail demand,
  the peak-event calendar, the Open-Meteo 7-day weather forecast, and GDELT
  protest/conflict news activity. Returns risk levels, scores, drivers,
  recommended actions and pre-rendered charts. Paste charts verbatim.

  Args:
    regions: Region IDs such as ["us-east1", "us-central1"], or ["all"] to
      scan every supported region.

  Returns:
    A dict with one assessment per region, a summary chart, and sources.
  """
  ids, unknown = _resolve(regions)
  if not ids:
    return {"error": f"Unknown regions: {unknown}. Call list_regions.",
            "unknown_regions": unknown}
  errors: dict[str, str] = {}

  def guarded(name, fn, default):
    try:
      return fn()
    except Exception as e:  # pylint: disable=broad-except
      errors[name] = f"{type(e).__name__}: {e}"[:300]
      return default

  trends = guarded("google_trends", lambda: _trends_rows({REGIONS[r][3] for r in ids}), None)
  weather = guarded("open_meteo", lambda: _fetch_weather(ids), None)
  gdelt = guarded("gdelt", lambda: _gdelt_rows(ids), None)

  unknown_sig = {"level": "Unknown", "points": 0, "note": "Data source unavailable."}
  detail = len(ids) <= 3
  results = []
  for r in ids:
    place, _, _, cc, fips, adm1 = REGIONS[r]
    signals = {
        "demand": summarize_demand(trends, cc) if trends is not None else dict(unknown_sig),
        "calendar": calendar_signal(cc),
        "weather": summarize_weather(weather.get(r, {})) if weather is not None else dict(unknown_sig),
        "unrest": summarize_unrest(gdelt, fips, adm1, place) if gdelt is not None else dict(unknown_sig),
    }
    pts, level = score(signals)
    drivers = [k for k, s in signals.items() if s.get("points")]
    charts = []
    if detail:
      w, u, d = signals["weather"], signals["unrest"], signals["demand"]
      if w.get("_days"):
        charts.append(bar_chart(f"{r} forecast peak wind gust by day (km/h)",
                                [x[5:] for x in w["_days"]], [g or 0 for g in w["_gusts"]], "km/h")["chart"])
      if u.get("_days"):
        charts.append(trend_chart(f"{r} protest/conflict share of GDELT news events, {u['scope']}",
                                  u["_days"], u["_share"], "%")["chart"])
      terms = d.get("retail_terms") or d.get("top_rising_terms") or []
      if terms:
        kind = "Retail" if d.get("retail_terms") else "Top"
        charts.append(bar_chart(f"{kind} rising searches, {cc}: {d['area_type']} where rising",
                                [t["term"] for t in terms], [t["areas"] for t in terms])["chart"])
    for s in signals.values():
      for k in [k for k in s if k.startswith("_")]:
        s.pop(k)
    results.append({
        "region": r, "location": place, "risk_level": level, "risk_score": pts,
        "drivers": drivers or ["none"], "signals": signals,
        "recommendations": recommendations(r, signals, level), "charts": charts,
    })
  results.sort(key=lambda x: -x["risk_score"])
  summary = bar_chart("Readiness risk score by region (0-100)",
                      [x["region"] for x in results], [x["risk_score"] for x in results],
                      "pts")["chart"] if len(results) > 1 else ""
  return {
      "assessed_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M"),
      "assessments": results,
      "summary_chart": summary,
      "unknown_regions": unknown,
      "source_errors": errors,
      "sources": [
          "Google Trends top rising terms (bigquery-public-data.google_trends), weekly",
          "GDELT 2.0 events (gdelt-bq.gdeltv2), daily",
          "Open-Meteo 7-day forecast (open-meteo.com)",
          "Published retail peak-event dates",
      ],
      "caveat": "Early indicators for readiness planning, not outage predictions.",
  }
