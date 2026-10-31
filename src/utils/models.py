from langchain_core.language_models.chat_models import BaseChatModel
from src.config import get_settings


def get_default_model() -> BaseChatModel:
    """Return configured ChatModel based on environment variables."""
    settings = get_settings()
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=settings.DEFAULT_MODEL, api_key=settings.OPENAI_API_KEY)
    elif settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "your_anthropic_api_key_here":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=settings.DEFAULT_MODEL, api_key=settings.ANTHROPIC_API_KEY)
    elif settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY != "your_google_api_key_here":
        from langchain_google_genai import ChatGoogleGenAI
        return ChatGoogleGenAI(model=settings.DEFAULT_MODEL, api_key=settings.GOOGLE_API_KEY)
    else:
        from langchain_core.language_models.fake_chat_models import FakeListChatModel
        return FakeListChatModel(responses=["No LLM API key configured. Please set OPENAI_API_KEY."])

