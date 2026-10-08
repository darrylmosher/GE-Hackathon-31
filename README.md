# GE Hackathon - Team 31

## Contents

| Path | Description |
|---|---|
| `ge-config/ge_app_manifest.json` | Gemini Enterprise app configuration and registered agents, exported from the Discovery Engine API. Project ID and number replaced with placeholders. |
| `basic-search-agent/` | Part 1. ADK agent with Google Search, deployed to Agent Engine. |
| `bq-trend-agent/` | Part 2. ADK agent that queries Google Trends in BigQuery with `BigQueryToolset`. |
| `regional-radar/` | Part 3. ADK agent that scores readiness risk for Google Cloud regions from public data. See `regional-radar/README.md`. |

## Setup

In each agent directory:

1. Copy `app/.env.example` to `app/.env` and set the project values.
2. `uv sync`
3. `uv run adk web .` to test locally.
4. `make backend` to deploy to Agent Engine.
