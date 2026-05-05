import json
import requests

from settings import (
    KB_HOSTNAME,
    KB_USERNAME,
    KB_PASSWORD,
    INDEX_NAME,
)


VIS_ID = "chessable-throughput-vega"
DASHBOARD_ID = "chessable-throughput"


def kibana_url():
    if KB_HOSTNAME.startswith("http"):
        return KB_HOSTNAME.rstrip("/")
    return f"https://{KB_HOSTNAME}:9243"


def headers():
    return {
        "kbn-xsrf": "true",
        "Content-Type": "application/json",
    }


def put_saved_object(object_type, object_id, attributes, references=None):
    url = (
        f"{kibana_url()}"
        f"/api/saved_objects/{object_type}/{object_id}?overwrite=true"
    )

    response = requests.post(
        url,
        headers=headers(),
        auth=(KB_USERNAME, KB_PASSWORD),
        json={
            "attributes": attributes,
            "references": references or [],
        },
        timeout=30,
    )

    if response.status_code not in (200, 201):
        raise RuntimeError(f"{response.status_code}: {response.text}")

    return response.json()


def throughput_vega_spec():
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Study Throughput",
        "data": {
            "url": {
                "%context%": True,
                "%timefield%": "@timestamp",
                "index": INDEX_NAME,
                "body": {
                    "size": 0,
                    "aggs": {
                        "by_day": {
                            "date_histogram": {
                                "field": "@timestamp",
                                "calendar_interval": "day",
                                "min_doc_count": 0,
                            },
                            "aggs": {
                                "new_items": {
                                    "sum": {
                                        "field": "throughput.new_items_today"
                                    }
                                },
                                "reviews_done": {
                                    "sum": {
                                        "field": "throughput.reviews_done_today"
                                    }
                                },
                                "session_minutes": {
                                    "sum": {
                                        "field": "meta.session_minutes"
                                    }
                                },
                            },
                        }
                    },
                },
            },
            "format": {
                "property": "aggregations.by_day.buckets"
            },
        },
        "transform": [
            {
                "calculate": "datum.key_as_string",
                "as": "date",
            },
            {
                "calculate": "datum.new_items.value",
                "as": "New items",
            },
            {
                "calculate": "datum.reviews_done.value",
                "as": "Reviews done",
            },
            {
                "calculate": "datum.session_minutes.value",
                "as": "Session minutes",
            },
            {
                "fold": [
                    "New items",
                    "Reviews done",
                    "Session minutes",
                ],
                "as": [
                    "metric",
                    "value",
                ],
            },
        ],
        "mark": {
            "type": "line",
            "point": True,
            "tooltip": True,
        },
        "encoding": {
            "x": {
                "field": "date",
                "type": "temporal",
                "title": "Date",
            },
            "y": {
                "field": "value",
                "type": "quantitative",
                "title": "Value",
            },
            "color": {
                "field": "metric",
                "type": "nominal",
                "title": "Metric",
            },
            "tooltip": [
                {
                    "field": "date",
                    "type": "temporal",
                    "title": "Date",
                },
                {
                    "field": "metric",
                    "type": "nominal",
                    "title": "Metric",
                },
                {
                    "field": "value",
                    "type": "quantitative",
                    "title": "Value",
                },
            ],
        },
    }


def create_vega_visualization():
    spec = throughput_vega_spec()

    attributes = {
        "title": "Chessable | Throughput | Vega",
        "visState": json.dumps(
            {
                "title": "Chessable | Throughput | Vega",
                "type": "vega",
                "params": {
                    "spec": json.dumps(spec),
                },
                "aggs": [],
            }
        ),
        "uiStateJSON": "{}",
        "description": "Daily study throughput over time.",
        "version": 1,
        "kibanaSavedObjectMeta": {
            "searchSourceJSON": json.dumps(
                {
                    "query": {
                        "query": "",
                        "language": "kuery",
                    },
                    "filter": [],
                }
            )
        },
    }

    put_saved_object("visualization", VIS_ID, attributes)
    print("Created/updated visualization: Chessable | Throughput | Vega")


def create_dashboard():
    panels = [
        {
            "type": "visualization",
            "gridData": {
                "x": 0,
                "y": 0,
                "w": 48,
                "h": 24,
                "i": VIS_ID,
            },
            "panelIndex": VIS_ID,
            "panelRefName": "panel_0",
            "embeddableConfig": {},
        }
    ]

    attributes = {
        "title": "Chessable | Throughput",
        "description": "Daily study throughput over time.",
        "panelsJSON": json.dumps(panels),
        "optionsJSON": json.dumps(
            {
                "hidePanelTitles": False,
                "useMargins": True,
                "syncColors": False,
                "syncCursor": True,
                "syncTooltips": False,
            }
        ),
        "timeRestore": False,
        "kibanaSavedObjectMeta": {
            "searchSourceJSON": json.dumps(
                {
                    "query": {
                        "query": "",
                        "language": "kuery",
                    },
                    "filter": [],
                }
            )
        },
    }

    references = [
        {
            "id": VIS_ID,
            "name": "panel_0",
            "type": "visualization",
        }
    ]

    put_saved_object("dashboard", DASHBOARD_ID, attributes, references)
    print("Created/updated dashboard: Chessable | Throughput")


def main():
    create_vega_visualization()
    create_dashboard()


if __name__ == "__main__":
    main()
