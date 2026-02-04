import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.claude_agent import ClaudeAgent, SYSTEM_PROMPT


@pytest.fixture
def agent():
    return ClaudeAgent(api_key="test_key")


def test_agent_initialization(agent):
    """Test Claude agent initialization"""
    assert agent.model == "claude-3-5-sonnet-20241022"
    assert agent.conversation_history == []


def test_reset_conversation(agent):
    """Test conversation reset"""
    agent.conversation_history = [{"role": "user", "content": "test"}]
    agent.reset_conversation()
    assert agent.conversation_history == []


def test_system_prompt():
    """Test system prompt is defined"""
    assert "web automation" in SYSTEM_PROMPT.lower()
    assert "playwright" in SYSTEM_PROMPT.lower()
    assert "mcp" in SYSTEM_PROMPT.lower()
