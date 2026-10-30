from typing import Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class MockChatModel(BaseChatModel):
    responses: List[Any] = []
    _call_history: List[List[BaseMessage]] = []

    def __init__(self, responses: Optional[List[Any]] = None, **kwargs):
        super().__init__(**kwargs)
        self.responses = list(responses) if responses else ["Mock default response"]
        self._call_history = []

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager: Any = None, **kwargs) -> ChatResult:
        self._call_history.append(messages)
        content = self.responses.pop(0) if self.responses else "Mock response"
        if isinstance(content, AIMessage):
            msg = content
        elif isinstance(content, dict) and "tool_calls" in content:
            msg = AIMessage(content=content.get("content", ""), tool_calls=content["tool_calls"])
        else:
            msg = AIMessage(content=str(content))
        return ChatResult(generations=[ChatGeneration(message=msg)])

    def bind_tools(self, tools: Any, **kwargs: Any) -> "MockChatModel":
        return self

    @property
    def _llm_type(self) -> str:
        return "mock-chat-model"
