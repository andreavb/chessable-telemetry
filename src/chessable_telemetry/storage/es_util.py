from elasticsearch import Elasticsearch

from settings import (
    ES_HOSTNAME,
    ES_USERNAME,
    ES_PASSWORD,
    INDEX_NAME,
    VERIFY_CERTS,
    CA_CERTS,
)

from chessable_telemetry.storage.mappings import INDEX_MAPPING


def get_client() -> Elasticsearch:
    return Elasticsearch(
        f"https://{ES_HOSTNAME}:9243",
        basic_auth=(ES_USERNAME, ES_PASSWORD),
        verify_certs=VERIFY_CERTS,
        ca_certs=CA_CERTS,
    )


def ensure_index(es: Elasticsearch, index_name: str = INDEX_NAME) -> None:
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=INDEX_MAPPING)


def index_document(es: Elasticsearch, document: dict, index_name: str = INDEX_NAME) -> dict:
    return es.index(index=index_name, document=document)
