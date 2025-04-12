import pytest
from unittest.mock import mock_open, patch,Mock
from requests.exceptions import HTTPError

from src.data_pipeline.main import call_api_page,write,transform_data

@pytest.fixture
def sample_data():
    return [{"id": 1}, {"id": 2}]

@patch("requests.get")
def test_call_api_page_success(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"items": [{"id": 1}]}
    mock_get.return_value = mock_response

    success, items = call_api_page("tracks", page=1, size=10)

    assert success is True
    assert items == [{"id": 1}]

@patch("requests.get")
def test_call_api_page_http_error(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = HTTPError("500 Internal Server Error")
    mock_get.return_value = mock_response

    success, items = call_api_page("tracks", page=1, size=10)

    assert success is False
    assert items == []

def test_transform_data_return_value_for_listen_history():
    data = [
        {
            "user_id": 1,
            "items": [101, 202],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z"
        }
    ]

    expected = [
        {
            "user_id": 1,
            "track_id": 101,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z"
        },
        {
            "user_id": 1,
            "track_id": 202,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z"
        }
    ]

    result = transform_data("listen_history", data)
    assert result == expected

@patch("builtins.open", new_callable=mock_open)
def test_write_opens_file_and_writes_lines(mock_open_fn, sample_data):
    write(sample_data, "test.jsonl")

    mock_open_fn.assert_called_once_with("data/test.jsonl", "a", encoding="utf-8")