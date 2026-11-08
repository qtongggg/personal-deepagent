# src/resume_agent.py
import os
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
import deepagents
from src.utils.models import get_default_model
from src.skills.resume_skill import retrieve_resume_knowledge

RESUME_AGENT_PROMPT = """You are QT-Agent, the official technical representative for Mah Qing Tong (QT).
Your purpose is to answer questions about QT's career, technical skills, projects, and education.
Instructions:
1. Always use the `retrieve_resume_knowledge` tool to retrieve accurate details from QT's official resume before answering.
2. Ground all answers strictly on the retrieved context. Never invent companies, dates, degrees, or tools.
3. Keep answers clear, confident, professional, and concise (under 120 words unless the user specifically asks for deep technical details).
4. If asked about topics completely unrelated to QT (like cooking, weather, or other people), politely explain that you are QT's resume representative and redirect them back to his technical background.
"""

def create_resume_agent(model: Optional[BaseChatModel] = None):
    """Assemble and returns the Resume DeepAgent."""
    active_model = model or get_default_model()

    agent = deepagents.create_deep_agent(
        model = active_model,
        tools = [retrieve_resume_knowledge],
        system_prompt = RESUME_AGENT_PROMPT,
    )

    return agent

def ask_resume_agent(question: str, agent=None) -> str:
    """Convenience helper to ask a single quesetion and get the text response."""
    if agent is None:
        agent = create_resume_agent()

    # Run the agent turn
    response = agent.invoke({"messages": [HumanMessage(content=question)]})

    # Find the final AI reply in the message history
    messages = response.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
        
    return "No response generated"


if __name__ =="__main__":

    print("=" * 60)
    print("🤖 QT Resume DeepAgent Terminal CLI")
    print("Type your questions below. Type 'exit' to quit.")
    print("=" * 60)

    agent = create_resume_agent()

    while True:
        try:
            user_input = input("\nYou > ").strip()
            if not user_input or user_input.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break

            print("\nThinking...")
            reply = ask_resume_agent(user_input, agent=agent)
            print(f"\nQT-Agent > {reply}\n")
        except KeyboardInterrupt:
            print("\nSession ended.")
            break
