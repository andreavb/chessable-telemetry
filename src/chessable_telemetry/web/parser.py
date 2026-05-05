import re


def extract_last_number(text):
    matches = re.findall(r"(\d+)", text)

    if not matches:
        return 0

    return int(matches[-1])


def parse_progress(text):
    result = {
        "not_learned": 0,
        "learning": 0,
        "mature": 0,
        "difficult": 0,
    }

    lines = text.splitlines()

    for line in lines:
        lower = line.lower()

        value = extract_last_number(line)

        if "not learned" in lower:
            result["not_learned"] = value

        elif "learning" in lower:
            result["learning"] = value

        elif "mature" in lower:
            result["mature"] = value

        elif "difficult" in lower:
            result["difficult"] = value

    return result


def parse_reviews(text):
    result = {
        "review_now": 0,
        "review_1h": 0,
        "review_4h": 0,
        "review_1d": 0,
        "review_3d": 0,
        "review_7d": 0,
    }

    lines = text.splitlines()

    for line in lines:
        lower = line.lower()

        value = extract_last_number(line)

        if "now" in lower:
            result["review_now"] = value

        elif "1 hour" in lower:
            result["review_1h"] = value

        elif "4 hr" in lower or "4 hour" in lower:
            result["review_4h"] = value

        elif "1 day" in lower:
            result["review_1d"] = value

        elif "3 day" in lower:
            result["review_3d"] = value

        elif "7 day" in lower:
            result["review_7d"] = value

    return result
