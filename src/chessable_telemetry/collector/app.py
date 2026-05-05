import argparse
from datetime import datetime, timezone

from chessable_telemetry.storage.es_util import (
    get_client,
    ensure_index,
    index_document,
)


def build_document(args: argparse.Namespace) -> dict:
    total = args.not_learned + args.learning + args.mature + args.difficult

    mature_percent = (args.mature / total * 100) if total else 0
    difficult_percent = (args.difficult / total * 100) if total else 0

    total_future_reviews = (
        args.review_now
        + args.review_1h
        + args.review_4h
        + args.review_1d
        + args.review_3d
        + args.review_7d
    )

    return {
        "@timestamp": args.date or datetime.now(timezone.utc).isoformat(),

        "platform": "chessable",
        "course_name": args.course,
        "course_type": args.course_type,

        "progress": {
            "not_learned": args.not_learned,
            "learning": args.learning,
            "mature": args.mature,
            "difficult": args.difficult,
            "total": total,
            "mature_percent": round(mature_percent, 2),
            "difficult_percent": round(difficult_percent, 2),
        },

        "reviews": {
            "now": args.review_now,
            "one_hour": args.review_1h,
            "four_hours": args.review_4h,
            "one_day": args.review_1d,
            "three_days": args.review_3d,
            "seven_days": args.review_7d,
            "total_future": total_future_reviews,
        },

        "throughput": {
            "new_items_today": args.new_items_today,
            "reviews_done_today": args.reviews_done_today,
        },

        "meta": {
            "session_minutes": args.session_minutes,
            "mode": args.mode,
            "notes": args.notes,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Chessable study telemetry and index it into Elasticsearch."
    )

    parser.add_argument("--course", required=True)
    parser.add_argument("--course-type", default="unknown")

    parser.add_argument("--not-learned", type=int, required=True)
    parser.add_argument("--learning", type=int, required=True)
    parser.add_argument("--mature", type=int, required=True)
    parser.add_argument("--difficult", type=int, required=True)

    parser.add_argument("--review-now", type=int, default=0)
    parser.add_argument("--review-1h", type=int, default=0)
    parser.add_argument("--review-4h", type=int, default=0)
    parser.add_argument("--review-1d", type=int, default=0)
    parser.add_argument("--review-3d", type=int, default=0)
    parser.add_argument("--review-7d", type=int, default=0)

    parser.add_argument("--new-items-today", type=int, default=0)
    parser.add_argument("--reviews-done-today", type=int, default=0)
    parser.add_argument("--session-minutes", type=int, default=0)

    parser.add_argument("--mode", default="normal")
    parser.add_argument("--notes", default="")
    parser.add_argument("--date", default=None)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    document = build_document(args)

    es = get_client()
    ensure_index(es)
    response = index_document(es, document)

    print(f"Indexed document: {response['_id']}")


if __name__ == "__main__":
    main()
