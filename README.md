# Chessable Telemetry

A small personal study-observability project for tracking Chessable course progress with Elasticsearch and Kibana.

The goal is simple: turn daily Chessable study snapshots into searchable metrics, dashboards, and eventually useful study signals such as workload, balance, throughput, and overload detection.

> This is an unofficial personal project. It is not affiliated with, endorsed by, or sponsored by Chessable.

## Why this exists

Chessable is great for spaced repetition, but it can be hard to see the broader picture across multiple courses:

- Which courses are healthy?
- Which ones are overloaded with difficult items?
- How much review load is coming soon?
- Am I spending too much time on openings and too little on endgames?
- Am I actually making progress, or just creating backlog?

This project sends manual Chessable snapshots into Elasticsearch and visualizes them in Kibana.

## Current status

The project currently supports:

- CLI-based snapshot collection
- Flask web form for easier daily input
- Elasticsearch indexing
- Kibana dashboards created programmatically through the Kibana API
- Vega-based dashboards for reproducible visualizations

## Dashboards

The current dashboard set includes:

### Course Health

Shows current progress by course:

- Not learned
- Learning
- Mature
- Difficult

Useful for seeing which courses are stable, raw, mature, or overloaded.

### Cognitive Load

Shows upcoming review pressure by course and time horizon:

- Now
- 1 hour
- 4 hours
- 1 day
- 3 days
- 7 days

Useful for understanding how much the spaced repetition system is about to demand.

### Balance

Shows study distribution by course type.

When session minutes are available, it uses study time. Otherwise, it falls back to indexed item counts.

### Throughput

Shows daily study activity over time:

- New items
- Reviews done
- Session minutes

This becomes more useful after collecting multiple daily snapshots.

## Architecture

```text
Chessable manual input
        ↓
CLI or Flask collector
        ↓
Elasticsearch index
        ↓
Kibana dashboards
```

## Setup

Create a local settings file:

```bash
cp settings.example.py settings.py
```

Edit `settings.py` with your Elasticsearch and Kibana connection details.

Example:

```python
# ========================
# Elasticsearch and Kibana
# ========================

ES_HOSTNAME = "your-es-host.es.region.cloud.es.io"
ES_USERNAME = "elastic"
ES_PASSWORD = "your-password"
ES_PORT = 9243
ES_SCHEME = "https"

KB_HOSTNAME = "your-kibana-host.kb.region.cloud.es.io"
KB_API_URL = f"https://{KB_HOSTNAME}/api/saved_objects/index-pattern/"
KB_USERNAME = ES_USERNAME
KB_PASSWORD = ES_PASSWORD

# ========================
# Index / Kibana Data View
# ========================

INDEX_NAME = "study-metrics-chessable"

DATA_VIEW_ID = "study-metrics-chessable"
DATA_VIEW_TITLE = "study-metrics-chessable*"

# ========================
# SSL / TLS
# ========================

VERIFY_CERTS = True
CA_CERTS = None
```

Install dependencies:

```bash
pip3 install --user -r requirements.txt
```

## CLI usage

Example snapshot:

```bash
PYTHONPATH=src python3 -m chessable_telemetry.collector.app \
  --course "100 Endgames You Must Know" \
  --course-type endgames \
  --not-learned 116 \
  --learning 54 \
  --mature 95 \
  --difficult 6 \
  --review-1d 10 \
  --review-3d 13 \
  --review-7d 36
```

## Web input

Run the Flask web app:

```bash
PYTHONPATH=src python3 -m chessable_telemetry.web.app
```

Then open:

```text
http://localhost:5000/
```

The page lists known courses from Elasticsearch and lets you paste Chessable progress/review blocks.
Currently, we do not support adding a new course via Web, but you can do so using the CLI.

## Kibana dashboards

Dashboards are created through the Kibana API.

Example:

```bash
PYTHONPATH=src python3 -m chessable_telemetry.kibana.bootstrap_course_health_vega
PYTHONPATH=src python3 -m chessable_telemetry.kibana.bootstrap_cognitive_load
PYTHONPATH=src python3 -m chessable_telemetry.kibana.bootstrap_balance
PYTHONPATH=src python3 -m chessable_telemetry.kibana.bootstrap_throughput
```

## Data model

Each snapshot document looks roughly like this:

```json
{
  "@timestamp": "2026-05-05T23:19:48.527600+00:00",
  "platform": "chessable",
  "course_name": "100 Endgames You Must Know",
  "course_type": "endgames",
  "progress": {
    "not_learned": 116,
    "learning": 54,
    "mature": 95,
    "difficult": 6,
    "total": 271,
    "mature_percent": 35.05,
    "difficult_percent": 2.21
  },
  "reviews": {
    "now": 0,
    "one_hour": 0,
    "four_hours": 0,
    "one_day": 10,
    "three_days": 13,
    "seven_days": 36,
    "total_future": 59
  },
  "throughput": {
    "new_items_today": 6,
    "reviews_done_today": 28
  },
  "meta": {
    "session_minutes": 45,
    "mode": "normal",
    "notes": ""
  }
}
```

## Roadmap

Planned improvements:

- `pyproject.toml`
- CLI entrypoint
- Better web input flow
- Create new courses from the web UI
- Preserve previous review data when only progress is updated
- Finish-date projection
- Overload/collapse detection
- Study efficiency metrics
- General study score
- Optional correlation with chess performance data

## What this project does not do

This project does not download or extract Chessable course content.

It only tracks manually provided progress/review metadata for personal study observability.

## License

This project is licensed under MIT License.
