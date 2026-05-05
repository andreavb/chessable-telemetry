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
