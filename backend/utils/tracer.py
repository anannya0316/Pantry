import json
import logging
import time
import uuid

logger = logging.getLogger("pantry.agent")


class AgentTrace:
    def __init__(self, request_id: str, user_id: str):
        self.request_id = request_id
        self.user_id = user_id
        self._start = time.perf_counter()

    def _emit(self, event: str, **kwargs):
        record = {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "event": event,
            "ms": round((time.perf_counter() - self._start) * 1000),
            **kwargs,
        }
        logger.info(json.dumps(record))

    def request_received(self, query: str):
        self._emit("request_received", query_len=len(query))

    def intent_classified(self, groups: list, method: str = "llm"):
        self._emit("intent_classified", groups=groups, method=method)

    def llm_call(self, iteration: int, message_count: int):
        self._emit("llm_call", iteration=iteration, message_count=message_count)

    def tool_called(self, tool: str, args: dict):
        self._emit("tool_called", tool=tool, args=args)

    def tool_result(self, tool: str, success: bool):
        self._emit("tool_result", tool=tool, success=success)

    def response_sent(self, response_type: str, text_length: int):
        self._emit("response_sent", response_type=response_type, text_length=text_length)

    def error(self, stage: str, message: str):
        self._emit("error", stage=stage, message=message)


def new_trace(user_id: str) -> AgentTrace:
    return AgentTrace(
        request_id=str(uuid.uuid4())[:8],
        user_id=user_id,
    )


def configure_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    log = logging.getLogger("pantry.agent")
    if not log.handlers:
        log.addHandler(handler)
    log.setLevel(logging.INFO)
