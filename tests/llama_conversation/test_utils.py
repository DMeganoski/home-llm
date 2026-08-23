"""Regression tests for get_oai_formatted_messages (issue #384).

A plain-text assistant reply (no tool call) was being silently dropped when
building the chat-completions style message history, so a later turn would
see the earlier user question with no matching answer in between and would
re-answer it.
"""

from homeassistant.components.conversation import AssistantContent, SystemContent, UserContent
from homeassistant.helpers import llm

from custom_components.llama_conversation.utils import get_oai_formatted_messages


def test_plain_assistant_reply_is_included_in_history():
    conv = [
        SystemContent(content="system prompt"),
        UserContent(content="what time is it"),
        AssistantContent(agent_id="agent-1", content="it is 2:43 PM"),
        UserContent(content="explain how transistors work"),
    ]

    messages = get_oai_formatted_messages(conv)

    assert [m["role"] for m in messages] == ["system", "user", "assistant", "user"]
    assert messages[2]["content"] == "it is 2:43 PM"


def test_assistant_reply_with_tool_calls_is_still_included():
    tool_call = llm.ToolInput("HassTurnOn", {"name": "office lamp"})
    conv = [
        UserContent(content="turn on the office lamp"),
        AssistantContent(agent_id="agent-1", content="", tool_calls=[tool_call]),
    ]

    messages = get_oai_formatted_messages(conv)

    assert messages[1]["role"] == "assistant"
    assert messages[1]["tool_calls"][0]["function"]["name"] == "HassTurnOn"


def test_multi_turn_history_alternates_user_and_assistant():
    conv = [
        UserContent(content="u1"),
        AssistantContent(agent_id="agent-1", content="a1"),
        UserContent(content="u2"),
        AssistantContent(agent_id="agent-1", content="a2"),
        UserContent(content="u3"),
    ]

    messages = get_oai_formatted_messages(conv)

    assert [m["role"] for m in messages] == ["user", "assistant", "user", "assistant", "user"]
