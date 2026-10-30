import pytest
from src.utils.schemas import AgentResponse
from tests.mock_model import MockChatModel


def test_deep_research_agent_creation():
    from src.agent import create_deep_research_agent

    fake_model = MockChatModel(responses=["Test response"])
    agent = create_deep_research_agent(model=fake_model)
    assert agent is not None

    nodes = agent.get_graph().nodes
    assert "tools" in nodes


def test_run_agent_turn_execution():
    from src.agent import run_agent_turn

    fake_response = (
        "Here is the comparison:\n\n"
        "| Document | Title | Focus |\n"
        "|---|---|---|\n"
        "| IRP 5 | Sukuk | Challenges | Maqasid |\n"
        "\nReference: [IRP 5](https://ifikr.my/resources/irp-5-challenges-maqasid-sukuk/)"
    )
    fake_model = MockChatModel(responses=[fake_response])

    response = run_agent_turn(
        query="Compare IRP 5 and IRP 11",
        user_id="user_test",
        model=fake_model,
    )

    assert isinstance(response, AgentResponse)
    assert "IRP 5" in response.result
    # Table pipes should be sanitized into a 3-column table format
    assert "| IRP 5 | Sukuk — Challenges | Maqasid |" in response.result
