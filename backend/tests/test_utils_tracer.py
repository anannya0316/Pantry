"""Tests for utils/tracer.py."""
import json
import logging
import pytest
from unittest.mock import patch

from utils.tracer import AgentTrace, new_trace, configure_logging


class TestAgentTrace:
    def _trace(self):
        return AgentTrace(request_id="req123", user_id="u1")

    def test_init_sets_fields(self):
        trace = self._trace()
        assert trace.request_id == "req123"
        assert trace.user_id == "u1"

    def test_request_received_logs_correct_event(self):
        trace = self._trace()
        with patch("utils.tracer.logger") as mock_logger:
            trace.request_received("What's in my pantry?")
        mock_logger.info.assert_called_once()
        logged = json.loads(mock_logger.info.call_args[0][0])
        assert logged["event"] == "request_received"
        assert logged["query_len"] == len("What's in my pantry?")
        assert logged["user_id"] == "u1"
        assert logged["request_id"] == "req123"

    def test_intent_classified_logs_groups(self):
        trace = self._trace()
        with patch("utils.tracer.logger") as mock_logger:
            trace.intent_classified(["inventory", "nutrition"])
        logged = json.loads(mock_logger.info.call_args[0][0])
        assert logged["event"] == "intent_classified"
        assert logged["groups"] == ["inventory", "nutrition"]
        assert logged["method"] == "llm"

    def test_llm_call_logs_iteration_and_count(self):
        trace = self._trace()
        with patch("utils.tracer.logger") as mock_logger:
            trace.llm_call(iteration=2, message_count=5)
        logged = json.loads(mock_logger.info.call_args[0][0])
        assert logged["event"] == "llm_call"
        assert logged["iteration"] == 2
        assert logged["message_count"] == 5

    def test_tool_called_logs_tool_and_args(self):
        trace = self._trace()
        with patch("utils.tracer.logger") as mock_logger:
            trace.tool_called("add_item", {"name": "rice"})
        logged = json.loads(mock_logger.info.call_args[0][0])
        assert logged["event"] == "tool_called"
        assert logged["tool"] == "add_item"
        assert logged["args"] == {"name": "rice"}

    def test_tool_result_logs_success_flag(self):
        trace = self._trace()
        with patch("utils.tracer.logger") as mock_logger:
            trace.tool_result("add_item", success=True)
        logged = json.loads(mock_logger.info.call_args[0][0])
        assert logged["event"] == "tool_result"
        assert logged["success"] is True

    def test_response_sent_logs_type_and_length(self):
        trace = self._trace()
        with patch("utils.tracer.logger") as mock_logger:
            trace.response_sent("text", 42)
        logged = json.loads(mock_logger.info.call_args[0][0])
        assert logged["event"] == "response_sent"
        assert logged["response_type"] == "text"
        assert logged["text_length"] == 42

    def test_error_logs_stage_and_message(self):
        trace = self._trace()
        with patch("utils.tracer.logger") as mock_logger:
            trace.error("llm_call", "timeout exceeded")
        logged = json.loads(mock_logger.info.call_args[0][0])
        assert logged["event"] == "error"
        assert logged["stage"] == "llm_call"
        assert logged["message"] == "timeout exceeded"

    def test_ms_field_is_non_negative(self):
        trace = self._trace()
        with patch("utils.tracer.logger") as mock_logger:
            trace.request_received("hello")
        logged = json.loads(mock_logger.info.call_args[0][0])
        assert logged["ms"] >= 0


class TestNewTrace:
    def test_returns_agent_trace_instance(self):
        trace = new_trace("u1")
        assert isinstance(trace, AgentTrace)
        assert trace.user_id == "u1"

    def test_request_id_is_8_chars(self):
        trace = new_trace("u1")
        assert len(trace.request_id) == 8

    def test_each_call_produces_unique_request_id(self):
        t1 = new_trace("u1")
        t2 = new_trace("u1")
        assert t1.request_id != t2.request_id


class TestConfigureLogging:
    def test_sets_info_level(self):
        configure_logging()
        log = logging.getLogger("pantry.agent")
        assert log.level == logging.INFO

    def test_handler_added(self):
        configure_logging()
        log = logging.getLogger("pantry.agent")
        assert len(log.handlers) >= 1

    def test_idempotent_no_duplicate_handlers(self):
        configure_logging()
        count_before = len(logging.getLogger("pantry.agent").handlers)
        configure_logging()
        count_after = len(logging.getLogger("pantry.agent").handlers)
        assert count_after == count_before
