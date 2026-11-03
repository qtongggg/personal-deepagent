from typing import Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from src.config import get_settings


class SafeFakeChatModel(FakeListChatModel):
    """Fallback fake chat model that supports bind_tools when no API key is set."""

    def bind_tools(self, tools: Any, **kwargs: Any) -> "SafeFakeChatModel":
        return self


def get_default_model() -> BaseChatModel:
    """Return configured ChatModel based on environment variables."""
    settings = get_settings()
    model_lower = (settings.DEFAULT_MODEL or "").lower()

    if ("deepseek" in model_lower or not settings.OPENAI_API_KEY) and settings.DEEPSEEK_API_KEY and settings.DEEPSEEK_API_KEY != "your_deepseek_api_key_here":
        from langchain_openai import ChatOpenAI
        actual_model = settings.DEFAULT_MODEL if "deepseek" in model_lower else "deepseek-chat"
        return ChatOpenAI(model=actual_model, api_key=settings.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    elif settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=settings.DEFAULT_MODEL, api_key=settings.OPENAI_API_KEY)
    elif settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "your_anthropic_api_key_here":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=settings.DEFAULT_MODEL, api_key=settings.ANTHROPIC_API_KEY)
    elif settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY != "your_google_api_key_here":
        from langchain_google_genai import ChatGoogleGenAI
        return ChatGoogleGenAI(model=settings.DEFAULT_MODEL, api_key=settings.GOOGLE_API_KEY)
    else:
        return SafeFakeChatModel(
            responses=["No LLM API key configured. Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY in .env."]
        )

