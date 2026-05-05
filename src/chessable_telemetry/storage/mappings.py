INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "@timestamp": {"type": "date"},

            "platform": {"type": "keyword"},
            "course_name": {"type": "keyword"},
            "course_type": {"type": "keyword"},

            "progress": {
                "properties": {
                    "not_learned": {"type": "integer"},
                    "learning": {"type": "integer"},
                    "mature": {"type": "integer"},
                    "difficult": {"type": "integer"},
                    "total": {"type": "integer"},
                    "mature_percent": {"type": "float"},
                    "difficult_percent": {"type": "float"},
                }
            },

            "reviews": {
                "properties": {
                    "now": {"type": "integer"},
                    "one_hour": {"type": "integer"},
                    "four_hours": {"type": "integer"},
                    "one_day": {"type": "integer"},
                    "three_days": {"type": "integer"},
                    "seven_days": {"type": "integer"},
                    "total_future": {"type": "integer"},
                }
            },

            "throughput": {
                "properties": {
                    "new_items_today": {"type": "integer"},
                    "reviews_done_today": {"type": "integer"},
                }
            },

            "meta": {
                "properties": {
                    "session_minutes": {"type": "integer"},
                    "mode": {"type": "keyword"},
                    "notes": {"type": "text"},
                }
            },
        }
    }
}
