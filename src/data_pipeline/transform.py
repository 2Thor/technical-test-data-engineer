
def transform_tracks(data : list) -> list:
    return data


def transform_users(data : list) -> list:
    return data


def transform_listen_history(data : list) -> list:
    return data

transform_map = {
    "tracks": transform_tracks,
    "users": transform_users,
    "listen_history": transform_listen_history
}


def main(endpoint: str, data: list):
    try:
        return transform_map[endpoint](data)
    except KeyError:
        raise ValueError(f"No transformation found for endpoint '{endpoint}'")
