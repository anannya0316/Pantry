"""Tests for utils/llm_client.py."""
import pytest
from unittest.mock import patch, MagicMock

_MOD = "utils.llm_client"


class TestGetApiKey:
    def test_returns_key_when_set(self):
        from utils.llm_client import get_api_key
        with patch(f"{_MOD}.os") as mock_os:
            mock_os.getenv.return_value = "mykey123"
            result = get_api_key()
        assert result == "mykey123"

    def test_returns_none_when_not_set(self):
        from utils.llm_client import get_api_key
        with patch(f"{_MOD}.os") as mock_os:
            mock_os.getenv.return_value = None
            result = get_api_key()
        assert result is None


class TestCallLlm:
    def test_raises_value_error_if_no_api_key(self):
        from utils.llm_client import call_llm
        with patch(f"{_MOD}.os") as mock_os:
            mock_os.getenv.return_value = None
            with pytest.raises(ValueError, match="No LLM API key"):
                call_llm("some prompt")

    def test_returns_stripped_content_on_success(self):
        from utils.llm_client import call_llm
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "  7 days  "}}]
        }
        with (
            patch(f"{_MOD}.os") as mock_os,
            patch(f"{_MOD}.http_requests") as mock_http,
        ):
            mock_os.getenv.return_value = "key123"
            mock_http.post.return_value = mock_resp
            result = call_llm("how long does milk last?")
        assert result == "7 days"

    def test_raises_runtime_error_on_non_200(self):
        from utils.llm_client import call_llm
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        with (
            patch(f"{_MOD}.os") as mock_os,
            patch(f"{_MOD}.http_requests") as mock_http,
        ):
            mock_os.getenv.return_value = "key123"
            mock_http.post.return_value = mock_resp
            with pytest.raises(RuntimeError, match="LLM error 500"):
                call_llm("some prompt")

    def test_passes_temperature_and_timeout_to_request(self):
        from utils.llm_client import call_llm
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "result"}}]
        }
        with (
            patch(f"{_MOD}.os") as mock_os,
            patch(f"{_MOD}.http_requests") as mock_http,
        ):
            mock_os.getenv.return_value = "key"
            mock_http.post.return_value = mock_resp
            call_llm("prompt", temperature=0.5, timeout=30)
        kwargs = mock_http.post.call_args.kwargs
        assert kwargs["timeout"] == 30
        assert kwargs["json"]["temperature"] == 0.5

    def test_includes_bearer_auth_header(self):
        from utils.llm_client import call_llm
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "ok"}}]
        }
        with (
            patch(f"{_MOD}.os") as mock_os,
            patch(f"{_MOD}.http_requests") as mock_http,
        ):
            mock_os.getenv.return_value = "secretkey"
            mock_http.post.return_value = mock_resp
            call_llm("prompt")
        headers = mock_http.post.call_args.kwargs["headers"]
        assert "Bearer secretkey" in headers["Authorization"]
