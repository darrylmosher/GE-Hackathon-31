import os
import google
import google.auth
from dotenv import find_dotenv, load_dotenv
from google.cloud import bigquery
from jinja2 import Environment, FileSystemLoader

load_dotenv(find_dotenv(usecwd=True), override=True)

PROMPTS_DIR_NAME = "prompts"
PROMPT_FILE_NAME = "google_trends_nl2sql_with_few_shot.j2"
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")


def load_nl2sql_with_few_shot_prompt(
    refresh_date_value: str,
    prompts_dir_name: str = PROMPTS_DIR_NAME,
    prompt_file_name: str = PROMPT_FILE_NAME,
) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, prompts_dir_name)
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(prompt_file_name)
    template_vars = {
        "refresh_date_value": refresh_date_value,
        "GOOGLE_CLOUD_PROJECT": GOOGLE_CLOUD_PROJECT,
    }
    return template.render(**template_vars)


def setup_bq_connection():
    load_dotenv(find_dotenv(usecwd=True), override=True)
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        try:
            _, project_id = google.auth.default()
        except Exception:
            project_id = "your-project-id"
    return bigquery.Client(project=project_id or "your-project-id")


def get_latest_refresh_date(
    table_name: str = "bigquery-public-data.google_trends.international_top_terms",
) -> str | None:
    try:
        bq_client = setup_bq_connection()
        query = f"""
            SELECT MAX(refresh_date) AS latest_date
            FROM `{table_name}`
        """
        results = bq_client.query(query).result()
        for row in results:
            if row and row.latest_date:
                latest_refresh_date = row.latest_date.strftime("%Y-%m-%d")
                print(f"   ...found latest refresh_date: {latest_refresh_date}")
                return latest_refresh_date
        return None
    except Exception as e:
        print(f"Warning fetching refresh_date: {e}")
        return None
