import json
import transform
import requests
import time
from datetime import datetime
import os

BASE_PORT = 8000
BASE_URL = f"http://localhost:{BASE_PORT}/"
SIZE = 1
ENDPOINTS = [
    "tracks",
    "users",
    "listen_history"
]
OUPUT_FILES = {
    "tracks": "tracks_data",
    "users": "users_data",
    "listen_history": "listen_history_data"
}
MAX_RETRIES = 1
WAIT_SECONDS = 1

def fetch_from_endpoint(endpoint : str,output_file : str):
    """
    Takes an endpoint as paramater and fetch data with pagination from this source
    Call transform_endpoint function to transform data
    """
    page = 1

    while True :
        success = False

        url = f"{BASE_URL}/{endpoint}?page={page}&size={SIZE}"

        for attempt in range(0,MAX_RETRIES):
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status() # Raise exeception if status > 400, skip next lines and directly go in except block
                data = response.json()

                items = data.get("items", []) # check if there is still data 
                if not items:
                    print(f"[INFO] Fin de la pagination à la page {page}")
                    return
                
                transformed_data = transform_endpoint(endpoint, items)
                write(transformed_data, output_file)
                success = True

                if page == 1:
                    return
                break

            except requests.exceptions.HTTPError as e: 
                print(f"[ERROR] HTTP {response.status_code} - {e}")
            except requests.exceptions.Timeout:
                print(f"[ERROR] Timeout sur la page {page}")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Requête échouée : {e}")
            
            if attempt < MAX_RETRIES:
                print(f"[WAIT] Attente {WAIT_SECONDS}s avant retry...")
                time.sleep(WAIT_SECONDS)

        if not success:
            print("[FAIL] Échec définitif, arrêt.")
            break

        page += 1


def transform_endpoint(endpoint : str, data : list) -> list:
    """
    Call transform module to apply data transformation following the endpoint name
    """
    print(f"[TRANSFORM] {endpoint} - {len(data)} items")
    transformed_data = transform.main(endpoint, data)
    return transformed_data

def write(data : list,output_file : str):
    """
    Write into jsonl file
    """
    folder_name = "data"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with open(f"data/{output_file}", "a", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")
    return 0

def get_output_filename(base_name: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return f"{base_name}_{timestamp}.jsonl"

def run_pipeline(endpoints:list):
    for endpoint in endpoints:
        output_file = get_output_filename(OUPUT_FILES[endpoint])
        fetch_from_endpoint(endpoint,output_file)
    return 0

if __name__ == "__main__":
    run_pipeline(ENDPOINTS)