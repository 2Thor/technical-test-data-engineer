import json
import requests
import os
from datetime import datetime
from prefect import flow, task, get_run_logger
from typing import List

from src.data_pipeline import transform

BASE_PORT = 8000
BASE_URL = f"http://localhost:{BASE_PORT}"
SIZE = 90
ENDPOINTS = ["tracks", "users", "listen_history"]
OUTPUT_FILES = {
    "tracks": "tracks_data",
    "users": "users_data",
    "listen_history": "listen_history_data"
}

@task
def get_output_filename(base_name: str) -> str:
    """
    Getting output filename from the dictionnary OUTPUT_FILES
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return f"{base_name}_{timestamp}.jsonl"

@task(retries=1, retry_delay_seconds=5, timeout_seconds=10)
def call_api_page(endpoint: str, page: int, size: int) -> List[dict]:
    url = f"{BASE_URL}/{endpoint}?page={page}&size={size}"
    logger = get_run_logger()
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        items = response.json().get("items", [])
        logger.info(f"[{endpoint}] Page {page} - {len(items)} items récupérés")
        return items
    except Exception as e:
        logger.error(f"[{endpoint}] Échec page {page} : {e}")
        raise

@task
def write_to_jsonl(data: List[dict], output_file: str):
    """
    Write into jsonl file
    """
    os.makedirs("data", exist_ok=True)
    path = f"data/{output_file}"
    with open(path, "a", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

@task
def fetch_endpoint(endpoint: str):
    logger = get_run_logger()
    logger.info(f"--- Début extraction : {endpoint} ---")
    page = 1
    output_file = get_output_filename(OUTPUT_FILES[endpoint])

    while True:
        items = call_api_page(endpoint, page, SIZE)
        if not items:
            logger.info(f"[{endpoint}] Fin de la pagination.")
            break

        transformed = transform.main(endpoint, items)
        write_to_jsonl(transformed, output_file)

        if len(items) < SIZE:
            logger.info(f"[{endpoint}] Page finale atteinte.")
            break

        page += 1

@flow(name="ETL Pipeline - Prefect")
def run_pipeline(endpoints: List[str] = ENDPOINTS):
    for endpoint in endpoints:
        fetch_endpoint.submit((endpoint))  # Exécution en parallèle

if __name__ == "__main__":
    run_pipeline.serve(
        name="daily-etl",
        schedule={"interval": 3600}  # toutes les 24h
    )