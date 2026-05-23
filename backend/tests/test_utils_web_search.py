"""Tests for utils/web_search.py."""
import pytest
from unittest.mock import patch, MagicMock

_MOD = "utils.web_search"


class TestTavilySearch:
    def test_no_api_key_returns_empty_string(self):
        from utils.web_search import tavily_search
        with patch(f"{_MOD}.os") as mock_os:
            mock_os.getenv.return_value = None
            result = tavily_search("tomato facts")
        assert result == ""

    def test_non_200_response_returns_empty(self):
        from utils.web_search import tavily_search
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        with (
            patch(f"{_MOD}.os") as mock_os,
            patch(f"{_MOD}.http_requests") as mock_http,
        ):
            mock_os.getenv.return_value = "tavilykey"
            mock_http.post.return_value = mock_resp
            result = tavily_search("tomato facts")
        assert result == ""

    def test_returns_joined_snippets(self):
        from utils.web_search import tavily_search
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "results": [
                {"content": "snippet one"},
                {"content": "snippet two"},
            ]
        }
        with (
            patch(f"{_MOD}.os") as mock_os,
            patch(f"{_MOD}.http_requests") as mock_http,
        ):
            mock_os.getenv.return_value = "tavilykey"
            mock_http.post.return_value = mock_resp
            result = tavily_search("tomato facts")
        assert "snippet one" in result
        assert "snippet two" in result

    def test_empty_results_list_returns_empty_string(self):
        from utils.web_search import tavily_search
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"results": []}
        with (
            patch(f"{_MOD}.os") as mock_os,
            patch(f"{_MOD}.http_requests") as mock_http,
        ):
            mock_os.getenv.return_value = "tavilykey"
            mock_http.post.return_value = mock_resp
            result = tavily_search("something")
        assert result == ""

    def test_request_exception_returns_empty(self):
        from utils.web_search import tavily_search
        with (
            patch(f"{_MOD}.os") as mock_os,
            patch(f"{_MOD}.http_requests") as mock_http,
        ):
            mock_os.getenv.return_value = "tavilykey"
            mock_http.post.side_effect = Exception("timeout")
            result = tavily_search("tomato facts")
        assert result == ""

    def test_results_without_content_filtered_out(self):
        from utils.web_search import tavily_search
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "results": [
                {"content": "valid snippet"},
                {"content": ""},
                {"title": "no content key"},
            ]
        }
        with (
            patch(f"{_MOD}.os") as mock_os,
            patch(f"{_MOD}.http_requests") as mock_http,
        ):
            mock_os.getenv.return_value = "tavilykey"
            mock_http.post.return_value = mock_resp
            result = tavily_search("test")
        assert result == "valid snippet"

    def test_sends_correct_api_key_in_body(self):
        from utils.web_search import tavily_search
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"results": []}
        with (
            patch(f"{_MOD}.os") as mock_os,
            patch(f"{_MOD}.http_requests") as mock_http,
        ):
            mock_os.getenv.return_value = "my_tavily_key"
            mock_http.post.return_value = mock_resp
            tavily_search("query")
        body = mock_http.post.call_args.kwargs["json"]
        assert body["api_key"] == "my_tavily_key"
        assert body["query"] == "query"
