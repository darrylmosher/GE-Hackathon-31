"""Writes a Readiness Assessment report (markdown) from live public data.

No LLM is involved: the report is rendered straight from assess_regions output,
so it doubles as a reproducible sample of what the agent sees.

Usage:
  uv run python scripts/readiness_report.py docs/readiness-assessment.md
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.sentinel_tools import assess_regions  # pylint: disable=g-import-not-at-top

ICON = {"Critical": "🔴", "Elevated": "🟠", "Low": "🟢", "Unknown": "⚪"}


def _signal_lines(s: dict) -> list[str]:
  d, c, w, u = s["demand"], s["calendar"], s["weather"], s["unrest"]
  out = []
  if d.get("level") == "Unknown":
    out.append(f"- **Demand:** unknown ({d.get('note', 'source unavailable')})")
  else:
    terms = d.get("retail_terms") or []
    if terms:
      named = ", ".join(f"{t['term']} ({t['areas']})" for t in terms[:5])
      out.append(
          f"- **Demand:** {d['retail_breadth_pct']}% of {d['areas_tracked']}"
          f" {d['area_type']} show a rising retail search, week of"
          f" {d['week_of']}: {named}"
      )
    else:
      top = ", ".join(t["term"] for t in (d.get("top_rising_terms") or [])[:3])
      out.append(
          f"- **Demand:** no retail terms among the top rising searches, week of"
          f" {d['week_of']}. Top rising: {top}"
      )
  events = c.get("upcoming_events") or []
  out.append(
      "- **Calendar:** "
      + (", ".join(f"{e['event']} in {e['days_away']} days" for e in events)
         if events else "no major retail event in the next 60 days")
  )
  if w.get("level") == "Unknown":
    out.append(f"- **Weather:** unknown ({w.get('note', 'source unavailable')})")
  elif w.get("hazards"):
    hz = "; ".join(
        f"{h['hazard']} {h['peak']} {h['unit']} on {h['date']} ({h['severity']})"
        for h in w["hazards"]
    )
    out.append(f"- **Weather ({w['forecast_window']}):** {hz}")
  else:
    out.append(
        f"- **Weather ({w['forecast_window']}):** no hazards; peak gust"
        f" {w.get('peak_gust_kmh')} km/h"
    )
  if u.get("level") == "Unknown":
    out.append(f"- **Unrest:** unknown ({u.get('note', 'source unavailable')})")
  else:
    out.append(
        f"- **Unrest, {u['scope']}:** {u['unrest_share_last_7d_pct']}% of news"
        f" events were protest or conflict in the last 7 days vs"
        f" {u['unrest_share_prior_30d_pct']}% over the prior 30 (ratio"
        f" {u['ratio_vs_baseline']}, data through {u['data_through']})"
    )
  return out


def render() -> str:
  scan = assess_regions(["all"])
  rows = scan["assessments"]
  top = [a["region"] for a in rows[:3]]
  detail = {a["region"]: a for a in assess_regions(top)["assessments"]}

  lines = [
      "# Regional Radar: Readiness Assessment",
      "",
      f"Generated {scan['assessed_at_utc']} UTC from public data by"
      " `scripts/readiness_report.py`. No LLM was used; every number comes"
      " from the scoring rules in `app/sentinel_tools.py`.",
      "",
      f"*{scan['caveat']}*",
      "",
      "## Risk by region",
      "",
      "| Region | Location | Level | Score | Drivers |",
      "|---|---|---|---|---|",
  ]
  for a in rows:
    lines.append(
        f"| {a['region']} | {a['location']} | {ICON[a['risk_level']]}"
        f" {a['risk_level']} | {a['risk_score']} | {', '.join(a['drivers'])} |"
    )
  lines += ["", scan["summary_chart"], "", "## Top regions in detail", ""]
  for r in top:
    a = detail[r]
    lines += [
        f"### {r} ({a['location']}): {ICON[a['risk_level']]} {a['risk_level']},"
        f" score {a['risk_score']}",
        "",
        *_signal_lines(a["signals"]),
        "",
    ]
    for ch in a["charts"]:
      lines += [ch, ""]

  merged: dict[str, dict] = {}
  for a in rows:
    for rec in a["recommendations"]:
      m = merged.setdefault(rec["action"], {**rec, "regions": []})
      m["regions"].append(a["region"])
  lines += ["## Recommended actions", ""]
  for i, (action, m) in enumerate(merged.items(), 1):
    regions = m["regions"]
    where = "all regions" if len(regions) == len(rows) else ", ".join(regions)
    lines.append(
        f"{i}. {action} ([docs]({m['link']})). *Owner: {m['owner']}.*"
        f" Applies to: {where}."
    )
  lines += ["", "## Sources", ""]
  lines += [f"- {s}" for s in scan["sources"]]
  if scan["source_errors"]:
    lines += ["", "**Source errors:** " + "; ".join(
        f"{k}: {v}" for k, v in scan["source_errors"].items())]
  return "\n".join(lines) + "\n"


if __name__ == "__main__":
  out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs/readiness-assessment.md")
  out.parent.mkdir(parents=True, exist_ok=True)
  out.write_text(render())
  print(f"Wrote {out}")
