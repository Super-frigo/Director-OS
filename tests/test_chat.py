"""Tests for director_os/chat.py — interactive chat mode."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from director_os.chat import (
    ChatDirector,
    ChatResponse,
    _parse_response,
    _build_system_prompt,
    _format_show,
    run_chat,
)
from director_os.director import Director
from director_os.state import DirectorState


# ============================================================================
# _parse_response
# ============================================================================


def test_parse_message_only():
    r = _parse_response("Hello, I'm the Director. Let's plan your film.")
    assert "Hello" in r.message
    assert r.actions == []


def test_parse_with_actions():
    raw = """I've planned a noir structure for your story.

---actions
commands:
  - run_agents: story
  - plan
  - compile: seedance"""
    r = _parse_response(raw)
    assert "noir structure" in r.message
    assert len(r.actions) == 3
    # YAML parses "run_agents: story" as dict {"run_agents": "story"}
    assert any("run_agents" in a for a in r.actions)
    assert any("plan" in str(a) for a in r.actions)
    assert any("compile" in str(a) for a in r.actions)


def test_parse_broken_yaml_graceful():
    raw = "Message here.\n\n---actions\nthis is not: valid: yaml: ["
    r = _parse_response(raw)
    assert "Message" in r.message
    assert r.actions == []  # broken YAML is silently ignored


def test_parse_no_separator():
    r = _parse_response("Just a message with ---actions in the middle of text.")
    # "---actions" on its own line is the separator; inline doesn't count
    assert r.actions == []


def test_parse_empty():
    r = _parse_response("")
    assert r.message == ""
    assert r.actions == []


# ============================================================================
# _build_system_prompt
# ============================================================================


def test_build_prompt_no_project():
    d = Director()
    prompt = _build_system_prompt(d)
    assert "no project" in prompt.lower()
    assert "new:" in prompt
    assert "load:" in prompt


def test_build_prompt_with_project():
    d = Director()
    d.new_project(title="Noir Film", premise="A detective story")
    prompt = _build_system_prompt(d)
    assert "Noir Film" in prompt
    assert "detective story" in prompt
    assert str(d.state.value) in prompt
    assert "legal next states" in prompt


# ============================================================================
# _format_show
# ============================================================================


def test_format_show_no_project():
    d = Director()
    assert "No project" in _format_show(d, "summary")


def test_format_show_summary():
    d = Director()
    d.new_project(title="Test", premise="A test premise")
    out = _format_show(d, "summary")
    assert "Test" in out
    assert "A test premise" in out


def test_format_show_shots():
    d = Director()
    d.new_project(title="Test")
    from director_os.models.project import Shot
    d.project.shots = [
        Shot(shot_id="s1", framing="CU", lens="85mm", movement="static"),
        Shot(shot_id="s2", framing="LS", lens="24mm"),
    ]
    out = _format_show(d, "shots")
    assert "s1" in out and "CU" in out
    assert "s2" in out and "LS" in out


def test_format_show_characters():
    d = Director()
    d.new_project(title="Test")
    from director_os.models.project import Character
    d.project.characters = [
        Character(id="c1", name="Alice", role="hero"),
        Character(id="c2", name="Bob", role="villain"),
    ]
    out = _format_show(d, "characters")
    assert "Alice" in out
    assert "Bob" in out


def test_format_show_beats():
    d = Director()
    d.new_project(title="Test")
    from director_os.models.project import StoryBeat
    d.project.story_beats = [
        StoryBeat(beat="OPENING", type="OPENING", emotion="calm"),
    ]
    out = _format_show(d, "beats")
    assert "OPENING" in out
    assert "calm" in out


def test_format_show_validate():
    d = Director()
    d.new_project(title="T", premise="P")
    from director_os.models.project import Character
    d.project.characters.append(Character(id="c1"))
    out = _format_show(d, "validate")
    assert "valid" in out.lower()


# ============================================================================
# ChatDirector with mock LLM client
# ============================================================================


@pytest.fixture
def mock_client():
    c = MagicMock()
    c.model_name = "test-model"
    return c


@pytest.fixture
def chat_director(mock_client):
    d = Director()
    d.new_project(title="Test Film", premise="A test premise about cinema")
    return ChatDirector(d, mock_client)


def test_chat_turn_with_message_only(chat_director, mock_client):
    mock_client.chat.return_value = "I understand. Let's plan this film."
    resp = chat_director.chat_turn("I want a noir film")
    assert "plan" in resp.message.lower()
    assert resp.actions == []


def test_chat_turn_with_actions(chat_director, mock_client):
    mock_client.chat.return_value = """Got it. Here's a noir plan.

---actions
commands:
  - plan
  - show: summary"""
    resp = chat_director.chat_turn("Plan my film")
    assert len(resp.actions) >= 1
    assert any("plan" in str(a) for a in resp.actions)


def test_chat_turn_empty_response(chat_director, mock_client):
    mock_client.chat.return_value = ""
    resp = chat_director.chat_turn("Hello")
    assert resp.message  # fallback message


def test_chat_turn_history_grows(chat_director, mock_client):
    mock_client.chat.return_value = "Response"
    assert chat_director.turn_count == 0
    chat_director.chat_turn("First message")
    assert chat_director.turn_count == 1
    assert len(chat_director.history) == 2  # user + assistant
    chat_director.chat_turn("Second message")
    assert chat_director.turn_count == 2
    assert len(chat_director.history) == 4


# ============================================================================
# Command execution (_exec_one)
# ============================================================================


def test_exec_new(chat_director):
    result = chat_director._exec_one("new: My Film|A test premise", {})
    assert "Created" in result
    assert chat_director.director.project.metadata.title == "My Film"
    assert chat_director.director.project.story.premise == "A test premise"


def test_exec_show_summary(chat_director):
    result = chat_director._exec_one("show: summary", {})
    assert "Test Film" in result


def test_exec_show_shots(chat_director):
    result = chat_director._exec_one("show: shots", {})
    assert "No shots" in result


def test_exec_show_validate(chat_director):
    from director_os.models.project import Character
    chat_director.director.project.characters.append(Character(id="c1"))
    result = chat_director._exec_one("show: validate", {})
    assert "valid" in result.lower()


def test_exec_unknown_command(chat_director):
    result = chat_director._exec_one("xyzzy", {})
    assert "?" in result


# ============================================================================
# apply_last_cycle
# ============================================================================


def test_apply_last_cycle(chat_director):
    d = chat_director.director
    d.start_cycle("test")
    d.fast_forward_to(DirectorState.PLAN)
    result = chat_director.apply_last_cycle()
    assert "applied" in result or "skipped" in result
