"""Text charts for chat surfaces such as Gemini Enterprise (no image hosting)."""

from __future__ import annotations


def _fmt(v: float, unit: str) -> str:
  if unit == "%":
    return f"{v:,.1f}%"
  if abs(v) >= 1000:
    return f"{v:,.0f}{(' ' + unit) if unit else ''}"
  if float(v).is_integer():
    return f"{v:,.0f}{(' ' + unit) if unit else ''}"
  return f"{v:,.1f}{(' ' + unit) if unit else ''}"


def _bar(value: float, top: float, width: int) -> str:
  n = int(round(abs(value) / top * width)) if top else 0
  if n == 0:
    return "▏"
  return ("░" if value < 0 else "█") * n


def bar_chart(
    title: str, labels: list[str], values: list[float], unit: str = ""
) -> dict:
  """Renders a horizontal bar chart as monospaced text for chat.

  Use for comparisons across categories, for example the risk score of each
  region. Paste the returned `chart` field into your reply exactly as returned.

  Args:
    title: Chart title, e.g. "Readiness risk score by region (0-100)".
    labels: Category names, one per bar (max 15).
    values: Numbers in the same order as labels.
    unit: Short display unit such as "pts", "km/h" or "%".

  Returns:
    A dict with the rendered `chart` (a markdown code block).
  """
  pairs = list(zip(labels, values))[:15]
  if not pairs:
    return {"chart": "```\n(no data)\n```"}
  top = max(abs(v) for _, v in pairs) or 1.0
  label_w = min(max(len(str(l)) for l, _ in pairs), 34)
  rows = [title, ""]
  for label, value in pairs:
    rows.append(
        f"{str(label)[:label_w]:<{label_w}} │ {_bar(value, top, 28)} {_fmt(value, unit)}"
    )
  return {"chart": "```\n" + "\n".join(rows) + "\n```"}


def trend_chart(
    title: str, period_labels: list[str], values: list[float], unit: str = ""
) -> dict:
  """Renders one time series as a text chart with a sparkline for chat.

  Pass at most 24 points, oldest first. Paste the returned `chart` field into
  your reply exactly as returned.

  Args:
    title: Chart title.
    period_labels: Period names, oldest first.
    values: Numbers in the same order as period_labels.
    unit: Short display unit.

  Returns:
    A dict with the rendered `chart`.
  """
  pairs = list(zip(period_labels, values))[-24:]
  if not pairs:
    return {"chart": "```\n(no data)\n```"}
  spark_chars = "▁▂▃▄▅▆▇█"
  lo = min(v for _, v in pairs)
  hi = max(v for _, v in pairs)
  span = (hi - lo) or 1.0
  spark = "".join(
      spark_chars[int((v - lo) / span * (len(spark_chars) - 1))] for _, v in pairs
  )
  top = max(abs(lo), abs(hi)) or 1.0
  label_w = max(len(str(l)) for l, _ in pairs)
  rows = [title, "", f"Trend: {spark}", ""]
  for label, value in pairs:
    rows.append(f"{str(label):<{label_w}} │ {_bar(value, top, 28)} {_fmt(value, unit)}")
  return {"chart": "```\n" + "\n".join(rows) + "\n```"}
