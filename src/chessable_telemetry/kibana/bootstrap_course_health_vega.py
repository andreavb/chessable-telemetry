import json
import requests

from settings import (
    KB_HOSTNAME,
    KB_USERNAME,
    KB_PASSWORD,
    INDEX_NAME,
)


VIS_ID = "chessable-course-health-vega"
DASHBOARD_ID = "chessable-course-health"


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
        raise RuntimeError(
            f"{response.status_code}: {response.text}"
        )

    return response.json()


def course_health_vega_spec():
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Course Health",
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
                                            "course_type",
                                            "progress.not_learned",
                                            "progress.learning",
                                            "progress.mature",
                                            "progress.difficult",
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
                "calculate": (
                    "datum.latest.hits.hits[0]._source.course_name"
                ),
                "as": "course",
            },
            {
                "calculate": (
                    "datum.latest.hits.hits[0]._source."
                    "progress.not_learned"
                ),
                "as": "Not learned",
            },
            {
                "calculate": (
                    "datum.latest.hits.hits[0]._source."
                    "progress.learning"
                ),
                "as": "Learning",
            },
            {
                "calculate": (
                    "datum.latest.hits.hits[0]._source."
                    "progress.mature"
                ),
                "as": "Mature",
            },
            {
                "calculate": (
                    "datum.latest.hits.hits[0]._source."
                    "progress.difficult"
                ),
                "as": "Difficult",
            },
            {
                "fold": [
                    "Not learned",
                    "Learning",
                    "Mature",
                    "Difficult",
                ],
                "as": [
                    "status",
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
                "title": "Items / moves",
                "stack": "zero",
            },
            "color": {
                "field": "status",
                "type": "nominal",
                "title": "Status",
            },
            "tooltip": [
                {
                    "field": "course",
                    "type": "nominal",
                    "title": "Course",
                },
                {
                    "field": "status",
                    "type": "nominal",
                    "title": "Status",
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
    spec = course_health_vega_spec()

    attributes = {
        "title": "Chessable | Course Health | Vega",
        "visState": json.dumps(
            {
                "title": (
                    "Chessable | Course Health | Vega"
                ),
                "type": "vega",
                "params": {
                    "spec": json.dumps(spec),
                },
                "aggs": [],
            }
        ),
        "uiStateJSON": "{}",
        "description": (
            "Course health by progress status."
        ),
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

    put_saved_object(
        "visualization",
        VIS_ID,
        attributes,
    )

    print(
        "Created/updated visualization: "
        "Chessable | Course Health | Vega"
    )


def create_dashboard():
    panels = [
        {
            "version": "8.8.0",
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
        "title": "Chessable | Course Health",
        "description": (
            "Course health by progress status."
        ),
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
        "timeFrom": "now-90d/d",
        "timeTo": "now",
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

    put_saved_object(
        "dashboard",
        DASHBOARD_ID,
        attributes,
        references,
    )

    print(
        "Created/updated dashboard: "
        "Chessable | Course Health"
    )


def main():
    create_vega_visualization()
    create_dashboard()


if __name__ == "__main__":
    main()
