import os
import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

from .utils import get_latest_refresh_date, load_nl2sql_with_few_shot_prompt

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
latest_refresh_date = get_latest_refresh_date() or "2025-08-25"
SYSTEM_INSTRUCTION = load_nl2sql_with_few_shot_prompt(
    refresh_date_value=latest_refresh_date
)

credentials, _ = google.auth.default()
bq_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=credentials),
    bigquery_tool_config=BigQueryToolConfig(
        write_mode=WriteMode.BLOCKED,
        compute_project_id=PROJECT_ID,
    ),
)

root_agent = Agent(
    name="google_trends_bigquery_analyst_dmosher",
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    description=(
        "BigQuery SQL expert that answers natural language questions about "
        "top trending and rising international search terms from Google Trends."
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[bq_toolset],
)

app = App(root_agent=root_agent, name="app")
