import json
import requests

from settings import (
    KB_HOSTNAME,
    KB_USERNAME,
    KB_PASSWORD,
    INDEX_NAME,
)


VIS_ID = "chessable-balance-vega"
DASHBOARD_ID = "chessable-balance"


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


def balance_vega_spec():
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Study Balance by Course Type",
        "data": {
            "url": {
                "%context%": True,
                "%timefield%": "@timestamp",
                "index": INDEX_NAME,
                "body": {
                    "size": 0,
                    "aggs": {
                        "course_types": {
                            "terms": {
                                "field": "course_type",
                                "size": 20,
                            },
                            "aggs": {
                                "session_minutes": {
                                    "sum": {
                                        "field": "meta.session_minutes"
                                    }
                                },
                                "total_items": {
                                    "sum": {
                                        "field": "progress.total"
                                    }
                                },
                            },
                        }
                    },
                },
            },
            "format": {
                "property": "aggregations.course_types.buckets"
            },
        },
        "transform": [
            {
                "calculate": "datum.key",
                "as": "course_type",
            },
            {
                "calculate": "datum.session_minutes.value",
                "as": "minutes",
            },
            {
                "calculate": "datum.total_items.value",
                "as": "items",
            },
            {
                "calculate": "datum.minutes > 0 ? datum.minutes : datum.items",
                "as": "value",
            },
            {
                "calculate": "datum.minutes > 0 ? 'Session minutes' : 'Indexed items fallback'",
                "as": "metric",
            },
        ],
        "mark": {
            "type": "arc",
            "tooltip": True,
        },
        "encoding": {
            "theta": {
                "field": "value",
                "type": "quantitative",
                "title": "Value",
            },
            "color": {
                "field": "course_type",
                "type": "nominal",
                "title": "Course type",
            },
            "tooltip": [
                {
                    "field": "course_type",
                    "type": "nominal",
                    "title": "Course type",
                },
                {
                    "field": "value",
                    "type": "quantitative",
                    "title": "Value",
                },
                {
                    "field": "minutes",
                    "type": "quantitative",
                    "title": "Session minutes",
                },
                {
                    "field": "items",
                    "type": "quantitative",
                    "title": "Indexed items fallback",
                },
                {
                    "field": "metric",
                    "type": "nominal",
                    "title": "Metric used",
                },
            ],
        },
    }


def create_vega_visualization():
    spec = balance_vega_spec()

    attributes = {
        "title": "Chessable | Balance | Vega",
        "visState": json.dumps(
            {
                "title": "Chessable | Balance | Vega",
                "type": "vega",
                "params": {
                    "spec": json.dumps(spec),
                },
                "aggs": [],
            }
        ),
        "uiStateJSON": "{}",
        "description": "Study balance by course type.",
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
    print("Created/updated visualization: Chessable | Balance | Vega")


def create_dashboard():
    panels = [
        {
            "type": "visualization",
            "gridData": {
                "x": 0,
                "y": 0,
                "w": 24,
                "h": 24,
                "i": VIS_ID,
            },
            "panelIndex": VIS_ID,
            "panelRefName": "panel_0",
            "embeddableConfig": {},
        }
    ]

    attributes = {
        "title": "Chessable | Balance",
        "description": "Study balance by course type.",
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
    print("Created/updated dashboard: Chessable | Balance")


def main():
    create_vega_visualization()
    create_dashboard()


if __name__ == "__main__":
    main()
