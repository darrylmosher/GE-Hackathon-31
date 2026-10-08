import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps.app import App

from .charts import bar_chart, trend_chart
from .prompt import INSTRUCTION
from .sentinel_tools import assess_regions, list_regions

load_dotenv()

root_agent = Agent(
    name="peak_sentinel_dmosher",
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    description=(
        "Peak-Event & Resiliency Sentinel: scores production-readiness risk for"
        " Google Cloud regions from public demand, peak-calendar, weather and"
        " unrest signals, and returns a Production Readiness Advisory with"
        " charts and recommended actions."
    ),
    instruction=INSTRUCTION,
    tools=[assess_regions, list_regions, bar_chart, trend_chart],
)

app = App(root_agent=root_agent, name="app")
