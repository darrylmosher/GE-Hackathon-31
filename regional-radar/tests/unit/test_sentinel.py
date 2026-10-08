"""Offline unit tests for the Sentinel: no BigQuery or network calls."""

import datetime as dt
import json


from app import sentinel_tools as st
from app.prompt import INSTRUCTION

TODAY = dt.datetime.now(dt.timezone.utc).date()


def _trends(cc, terms_by_area):
  return [
      {"cc": cc, "area": a, "term": t, "gain": 500, "week": "2026-10-04",
       "refresh": "2026-10-07"}
      for a, terms in terms_by_area.items() for t in terms
  ]


def _gdelt(cc, adm1, base_share, recent_share, total=400):
  rows = []
  for i in range(1, 38):
    share = recent_share if i <= 7 else base_share
    rows.append({"cc": cc, "adm1": adm1, "d": TODAY - dt.timedelta(days=i),
                 "total": total, "unrest": int(total * share)})
  return rows


def _daily(gust=30, tmax=20, tmin=5, rain=0, snow=0):
  days = [str(TODAY + dt.timedelta(days=i)) for i in range(7)]
  return {"time": days, "wind_gusts_10m_max": [gust] * 7,
          "temperature_2m_max": [tmax] * 7, "temperature_2m_min": [tmin] * 7,
          "precipitation_sum": [rain] * 7, "snowfall_sum": [snow] * 7}


def test_prompt_has_no_braces():
  assert "{" not in INSTRUCTION and "}" not in INSTRUCTION


def test_retail_pattern():
  assert st.RETAIL_PATTERN.search("black friday deals")
  assert st.RETAIL_PATTERN.search("taylor swift tickets")
  assert not st.RETAIL_PATTERN.search("salem witch trials")
  assert not st.RETAIL_PATTERN.search("monday night football")


def test_demand_no_retail_is_low():
  rows = _trends("US", {"Atlanta": ["mnf", "kahoot"], "Boston": ["eames"]})
  d = st.summarize_demand(rows, "US")
  assert d["level"] == "Low" and d["retail_breadth_pct"] == 0
  assert d["top_rising_terms"][0]["term"] in ("mnf", "kahoot", "eames")


def test_demand_retail_breadth():
  rows = _trends("US", {"A": ["prime big deal days"], "B": ["walmart deals"],
                        "C": ["mnf"], "D": ["kahoot"]})
  d = st.summarize_demand(rows, "US")
  assert d["retail_breadth_pct"] == 50.0 and d["points"] == 30
  assert d["level"] == "Critical"


def test_calendar_window():
  c = st.calendar_signal("US", dt.date(2026, 11, 20))
  assert c["points"] == 20 and c["upcoming_events"][0]["event"] == "Black Friday"
  assert st.calendar_signal("JA", dt.date(2026, 11, 20))["points"] == 0


def test_weather_levels():
  assert st.summarize_weather(_daily())["level"] == "Low"
  w = st.summarize_weather(_daily(gust=70))
  assert w["level"] == "Elevated" and w["hazards"][0]["hazard"] == "wind gusts"
  w = st.summarize_weather(_daily(gust=70, tmin=-25))
  assert w["level"] == "Critical" and w["points"] == 40
  assert st.summarize_weather({})["level"] == "Unknown"


def test_unrest_ratio_and_fallback():
  rows = _gdelt("US", "USSC", 0.10, 0.25)
  u = st.summarize_unrest(rows, "US", "USSC", "Moncks Corner, South Carolina", TODAY)
  assert u["level"] == "Critical" and u["ratio_vs_baseline"] == 2.5
  assert u["scope"].startswith("state")
  small = _gdelt("US", "USSC", 0.1, 0.1, total=5) + _gdelt("US", "", 0.1, 0.15)
  u = st.summarize_unrest(small, "US", "USSC", "Moncks Corner, South Carolina", TODAY)
  assert u["scope"].startswith("country") and u["level"] == "Elevated"


def test_score():
  low = {"level": "Low", "points": 0}
  assert st.score({"a": low, "b": low}) == (0, "Low")
  assert st.score({"a": {"level": "Elevated", "points": 20}, "b": low}) == (20, "Elevated")
  assert st.score({"a": {"level": "Critical", "points": 40}, "b": low})[1] == "Critical"


def test_assess_regions_end_to_end(monkeypatch):
  monkeypatch.setattr(st, "_trends_rows", lambda ccs: _trends("US", {"A": ["walmart deals"], "B": ["mnf"]}))
  monkeypatch.setattr(st, "_gdelt_rows", lambda ids: _gdelt("US", "USSC", 0.1, 0.1) + _gdelt("US", "USIA", 0.1, 0.1))
  monkeypatch.setattr(st, "_fetch_weather", lambda ids: {r: _daily(gust=95 if r == "us-east1" else 20) for r in ids})
  out = st.assess_regions(["us-east1", "US-CENTRAL1", "mars-1"])
  assert [a["region"] for a in out["assessments"]] == ["us-east1", "us-central1"]
  east = out["assessments"][0]
  assert east["risk_level"] == "Critical" and "weather" in east["drivers"]
  assert len(east["charts"]) == 3 and out["summary_chart"].startswith("```")
  assert out["unknown_regions"] == ["mars-1"]
  json.dumps(out, default=str)  # tool output must be serializable
  assert not any(k.startswith("_") for a in out["assessments"]
                 for s in a["signals"].values() for k in s)


def test_source_failure_is_isolated(monkeypatch):
  def boom(*_):
    raise RuntimeError("quota")
  monkeypatch.setattr(st, "_trends_rows", boom)
  monkeypatch.setattr(st, "_gdelt_rows", boom)
  monkeypatch.setattr(st, "_fetch_weather", lambda ids: {r: _daily() for r in ids})
  out = st.assess_regions(["all"])
  assert len(out["assessments"]) == len(st.REGIONS)
  assert set(out["source_errors"]) == {"google_trends", "gdelt"}
  assert out["assessments"][0]["signals"]["demand"]["level"] == "Unknown"
  assert out["assessments"][0]["charts"] == []  # no per-region charts for big scans
