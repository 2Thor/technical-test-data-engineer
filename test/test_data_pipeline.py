from unittest.mock import mock_open, patch,Mock
from requests.exceptions import HTTPError
from prefect.logging import disable_run_logger
from prefect.testing.utilities import prefect_test_harness
from src.data_pipeline.main import call_api_page,write_to_jsonl,get_output_filename
from src.data_pipeline.transform import main
from datetime import datetime
import pytest


@pytest.fixture
def sample_data():
    return [{"id": 1}, {"id": 2}]

""" Test API """
@patch("requests.get")
def test_call_api_page_success(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"items": [{"id": 1}]}
    mock_get.return_value = mock_response

    with prefect_test_harness(), disable_run_logger():
        items = call_api_page.fn("tracks", page=1, size=10)

    mock_get.assert_called_with("http://localhost:8000/tracks?page=1&size=10", timeout=5)
    assert items == [{"id": 1}]

@patch("requests.get")
@patch("src.data_pipeline.main.get_run_logger")
def test_call_api_page_http_error(mock_logger,mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = HTTPError("500 Internal Server Error")
    mock_get.return_value = mock_response
    with pytest.raises(HTTPError):
        with prefect_test_harness(), disable_run_logger():
            call_api_page.fn("tracks", page=1, size=10)
    
    assert mock_get.call_count == 1
    mock_logger.return_value.error.assert_called_with(
        "[tracks] Échec page 1 : 500 Internal Server Error"
    )


""" Test pipeline functions """
def test_transform_data_listen_history():
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
    with prefect_test_harness():
        result = main("listen_history", data)

    assert result == expected

def test_get_output_filename():
    base_name = "test_file"
    with prefect_test_harness():
        file_name = get_output_filename(base_name)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    assert file_name == f"{base_name}_{timestamp}.jsonl"


@patch("builtins.open")
def test_write_opens_file_and_writes_lines(mock_open, sample_data):
    with prefect_test_harness(), disable_run_logger():
        write_to_jsonl(sample_data, "test.jsonl")
    
    mock_open.assert_called_once_with("data/test.jsonl", "a", encoding="utf-8")