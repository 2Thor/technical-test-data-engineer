
def transform_tracks(data : list) -> list:
    return data


def transform_users(data : list) -> list:
    return data


def transform_listen_history(data: list) -> list:
    flattened = []

    for record in data:
        user_id = record["user_id"]
        created_at = record["created_at"]
        updated_at = record["updated_at"]

        for track_id in record["items"]:
            flattened.append({
                "user_id": user_id,
                "track_id": track_id,
                "created_at": created_at,
                "updated_at": updated_at
            })

    return flattened

transform_function_map = {
    "tracks": transform_tracks,
    "users": transform_users,
    "listen_history": transform_listen_history
}


def main(endpoint: str, data: list):
    try:
        return transform_function_map[endpoint](data)
    except KeyError:
        raise ValueError(f"No transformation found for endpoint '{endpoint}'")
