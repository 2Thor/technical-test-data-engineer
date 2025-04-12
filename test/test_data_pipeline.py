import pytest
from unittest.mock import mock_open, call, patch,Mock
from requests.exceptions import HTTPError
import sys 
import os 
import json

from src.data_pipeline.main import call_api_page,write

@pytest.fixture
def sample_data():
    return [{"id": 1}, {"id": 2}]

@patch("builtins.open", new_callable=mock_open)
def test_write_opens_file_and_writes_lines(mock_open_fn, sample_data):
    write(sample_data, "test.jsonl")

    mock_open_fn.assert_called_once_with("data/test.jsonl", "a", encoding="utf-8")

@patch("os.path.exists", return_value=False)
@patch("os.makedirs")
def test_write_creates_folder_if_missing(mock_makedirs, mock_exists, sample_data):
    write(sample_data, "test.jsonl")

    mock_makedirs.assert_called_once_with("data")


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
    mock_get.assert_called_once_with("http://localhost:8000/tracks?page=1&size=10", timeout=5)



@patch("requests.get")
def test_call_api_page_http_error(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = HTTPError("500 Internal Server Error")
    mock_get.return_value = mock_response

    success, items = call_api_page("tracks", page=1, size=10)

    assert success is False
    assert items == []
    mock_get.assert_called_once_with("http://localhost:8000/tracks?page=1&size=10", timeout=5)



