from argparse import Namespace

from flask import Flask, redirect, render_template, request, url_for

from settings import INDEX_NAME

from chessable_telemetry.collector.app import build_document
from chessable_telemetry.storage.es_util import (
    get_client,
    ensure_index,
    index_document,
)
from chessable_telemetry.web.parser import parse_progress, parse_reviews


app = Flask(__name__)


def list_courses(es):
    response = es.search(
        index=INDEX_NAME,
        size=0,
        aggs={
            "courses": {
                "terms": {
                    "field": "course_name",
                    "size": 100,
                    "order": {"_key": "asc"},
                },
                "aggs": {
                    "latest": {
                        "top_hits": {
                            "size": 1,
                            "sort": [{"@timestamp": {"order": "desc"}}],
                            "_source": [
                                "course_name",
                                "course_type",
                            ],
                        }
                    }
                },
            }
        },
    )

    courses = []

    for bucket in response["aggregations"]["courses"]["buckets"]:
        latest = bucket["latest"]["hits"]["hits"][0]["_source"]
        courses.append(
            {
                "course_name": latest["course_name"],
                "course_type": latest.get("course_type", "unknown"),
            }
        )

    return courses


@app.route("/", methods=["GET"])
def index():
    es = get_client()
    ensure_index(es)

    courses = list_courses(es)

    return render_template(
        "index.html",
        courses=courses,
    )


@app.route("/snapshot", methods=["POST"])
def snapshot():
    course_name = request.form["course_name"]
    course_type = request.form.get("course_type", "unknown")

    progress_text = request.form.get("progress_text", "")
    reviews_text = request.form.get("reviews_text", "")

    session_minutes = int(request.form.get("session_minutes") or 0)
    new_items_today = int(request.form.get("new_items_today") or 0)
    reviews_done_today = int(request.form.get("reviews_done_today") or 0)

    mode = request.form.get("mode") or "normal"
    notes = request.form.get("notes") or ""

    progress = parse_progress(progress_text)
    reviews = parse_reviews(reviews_text)

    args = Namespace(
        course=course_name,
        course_type=course_type,

        not_learned=progress["not_learned"],
        learning=progress["learning"],
        mature=progress["mature"],
        difficult=progress["difficult"],

        review_now=reviews["review_now"],
        review_1h=reviews["review_1h"],
        review_4h=reviews["review_4h"],
        review_1d=reviews["review_1d"],
        review_3d=reviews["review_3d"],
        review_7d=reviews["review_7d"],

        new_items_today=new_items_today,
        reviews_done_today=reviews_done_today,
        session_minutes=session_minutes,

        mode=mode,
        notes=notes,
        date=None,
    )

    document = build_document(args)

    es = get_client()
    ensure_index(es)
    index_document(es, document)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
