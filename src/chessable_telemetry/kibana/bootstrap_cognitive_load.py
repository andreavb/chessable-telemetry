import json
import requests

from settings import (
    KB_HOSTNAME,
    KB_USERNAME,
    KB_PASSWORD,
    INDEX_NAME,
)


VIS_ID = "chessable-cognitive-load-vega"
DASHBOARD_ID = "chessable-cognitive-load"


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


def cognitive_load_vega_spec():
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Cognitive Load",
        "data": {
            "url": {
                "%context%": True,
                "%timefield%": "@timestamp",
                "index": INDEX_NAME,
                "body": {
                    "size": 0,
                    "aggs": {
                        "courses": {
                            "terms": {
                                "field": "course_name",
                                "size": 50,
                            },
                            "aggs": {
                                "latest": {
                                    "top_hits": {
                                        "size": 1,
                                        "sort": [
                                            {
                                                "@timestamp": {
                                                    "order": "desc"
                                                }
                                            }
                                        ],
                                        "_source": [
                                            "course_name",
                                            "reviews.now",
                                            "reviews.one_hour",
                                            "reviews.four_hours",
                                            "reviews.one_day",
                                            "reviews.three_days",
                                            "reviews.seven_days",
                                            "reviews.total_future",
                                        ],
                                    }
                                }
                            },
                        }
                    },
                },
            },
            "format": {
                "property": "aggregations.courses.buckets"
            },
        },
        "transform": [
            {
                "calculate": "datum.latest.hits.hits[0]._source.course_name",
                "as": "course",
            },
            {
                "calculate": "datum.latest.hits.hits[0]._source.reviews.now",
                "as": "Now",
            },
            {
                "calculate": "datum.latest.hits.hits[0]._source.reviews.one_hour",
                "as": "1 hour",
            },
            {
                "calculate": "datum.latest.hits.hits[0]._source.reviews.four_hours",
                "as": "4 hours",
            },
            {
                "calculate": "datum.latest.hits.hits[0]._source.reviews.one_day",
                "as": "1 day",
            },
            {
                "calculate": "datum.latest.hits.hits[0]._source.reviews.three_days",
                "as": "3 days",
            },
            {
                "calculate": "datum.latest.hits.hits[0]._source.reviews.seven_days",
                "as": "7 days",
            },
            {
                "fold": [
                    "Now",
                    "1 hour",
                    "4 hours",
                    "1 day",
                    "3 days",
                    "7 days",
                ],
                "as": [
                    "horizon",
                    "count",
                ],
            },
        ],
        "mark": {
            "type": "bar",
            "tooltip": True,
        },
        "encoding": {
            "y": {
                "field": "course",
                "type": "nominal",
                "title": "Course",
                "sort": "-x",
            },
            "x": {
                "field": "count",
                "type": "quantitative",
                "title": "Reviewable moves/items",
                "stack": "zero",
            },
            "color": {
                "field": "horizon",
                "type": "nominal",
                "title": "Horizon",
                "sort": [
                    "Now",
                    "1 hour",
                    "4 hours",
                    "1 day",
                    "3 days",
                    "7 days",
                ],
            },
            "tooltip": [
                {
                    "field": "course",
                    "type": "nominal",
                    "title": "Course",
                },
                {
                    "field": "horizon",
                    "type": "nominal",
                    "title": "Horizon",
                },
                {
                    "field": "count",
                    "type": "quantitative",
                    "title": "Count",
                },
            ],
        },
    }


def create_vega_visualization():
    spec = cognitive_load_vega_spec()

    attributes = {
        "title": "Chessable | Cognitive Load | Vega",
        "visState": json.dumps(
            {
                "title": "Chessable | Cognitive Load | Vega",
                "type": "vega",
                "params": {
                    "spec": json.dumps(spec),
                },
                "aggs": [],
            }
        ),
        "uiStateJSON": "{}",
        "description": "Review workload by course and time horizon.",
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
    print("Created/updated visualization: Chessable | Cognitive Load | Vega")


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
        "title": "Chessable | Cognitive Load",
        "description": "Review workload by course and time horizon.",
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
    print("Created/updated dashboard: Chessable | Cognitive Load")


def main():
    create_vega_visualization()
    create_dashboard()


if __name__ == "__main__":
    main()
