"""Tests for director_os/state.py — state machine, transitions, path_to."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from director_os.state import (
    DirectorState, StateError, CycleContext,
    TRANSITIONS, path_to,
)
from director_os.director import Director


# ============================================================================
# DirectorState enum
# ============================================================================

def test_all_eight_states_exist():
    assert len(DirectorState) == 8
    assert DirectorState.IDLE.value == "idle"
    assert DirectorState.UNDERSTAND.value == "understand"
    assert DirectorState.COMPILE.value == "compile"


# ============================================================================
# Transition table
# ============================================================================

def test_idle_only_goes_to_understand():
    assert TRANSITIONS[DirectorState.IDLE] == {DirectorState.UNDERSTAND}


def test_understand_branches():
    assert DirectorState.CLARIFY in TRANSITIONS[DirectorState.UNDERSTAND]
    assert DirectorState.PLAN in TRANSITIONS[DirectorState.UNDERSTAND]


def test_validate_branches():
    assert DirectorState.PLAN in TRANSITIONS[DirectorState.VALIDATE]   # failed → back to plan
    assert DirectorState.COMMIT in TRANSITIONS[DirectorState.VALIDATE]  # passed → commit


def test_commit_branches():
    assert DirectorState.COMPILE in TRANSITIONS[DirectorState.COMMIT]
    assert DirectorState.IDLE in TRANSITIONS[DirectorState.COMMIT]


def test_compile_only_goes_to_idle():
    assert TRANSITIONS[DirectorState.COMPILE] == {DirectorState.IDLE}


# ============================================================================
# Transition validation (via Director)
# ============================================================================

def test_legal_step_transition():
    d = Director()
    d.start_cycle("test")
    d.transition_to(DirectorState.PLAN)
    assert d.state == DirectorState.PLAN


def test_illegal_step_transition():
    d = Director()
    d.start_cycle("test")
    with pytest.raises(StateError, match="Cannot transition"):
        d.transition_to(DirectorState.COMPILE)


def test_legal_next_states():
    d = Director()
    d.start_cycle("test")
    legal = d.get_legal_transitions()
    assert "clarify" in legal
    assert "plan" in legal
    assert "compile" not in legal


# ============================================================================
# fast_forward_to
# ============================================================================

def test_fast_forward_through_full_path():
    """IDLE → UNDERSTAND → ... → COMPILE in one call."""
    d = Director()
    d.start_cycle("test")
    d.fast_forward_to(DirectorState.COMPILE)
    assert d.state == DirectorState.COMPILE


def test_fast_forward_to_current_state_noop():
    d = Director()
    d.start_cycle("test")
    d.transition_to(DirectorState.PLAN)
    d.fast_forward_to(DirectorState.PLAN)  # already there
    assert d.state == DirectorState.PLAN


def test_fast_forward_cycles_increment_turns():
    d = Director()
    d.start_cycle("test")
    before = d.ctx.turn_count
    d.fast_forward_to(DirectorState.COMMIT)
    assert d.ctx.turn_count > before


# ============================================================================
# path_to (BFS)
# ============================================================================

def test_path_to_same_state_empty():
    assert path_to(DirectorState.IDLE, DirectorState.IDLE) == []


def test_path_to_neighbor():
    p = path_to(DirectorState.IDLE, DirectorState.UNDERSTAND)
    assert p == [DirectorState.UNDERSTAND]


def test_path_to_deep():
    p = path_to(DirectorState.UNDERSTAND, DirectorState.COMPILE)
    assert p == [
        DirectorState.PLAN,
        DirectorState.DESIGN,
        DirectorState.VALIDATE,
        DirectorState.COMMIT,
        DirectorState.COMPILE,
    ]


def test_path_to_validate_to_commit():
    assert DirectorState.COMMIT in path_to(DirectorState.VALIDATE, DirectorState.COMMIT)


def test_path_to_deep_requires_intermediate():
    """Verify the full IDLE → COMPILE path goes through VALIDATE (not skipped)."""
    p = path_to(DirectorState.IDLE, DirectorState.COMPILE)
    # Must go through VALIDATE before COMMIT
    assert DirectorState.VALIDATE in p
    idx_v = p.index(DirectorState.VALIDATE)
    idx_c = p.index(DirectorState.COMMIT)
    assert idx_v < idx_c  # validate before commit


# ============================================================================
# State guards on Director methods
# ============================================================================

def test_plan_blocked_in_idle():
    d = Director()
    with pytest.raises(StateError):
        d.plan()


def test_compile_blocked_in_idle():
    d = Director()
    with pytest.raises(StateError):
        d.compile("seedance")


def test_save_blocked_in_idle():
    d = Director()
    with pytest.raises(StateError):
        d.save_project("/tmp/test.md")


def test_plan_allowed_in_plan_state():
    from director_os.models.project import Project, Metadata, Story, Character
    d = Director()
    d.new_project("T", "P")
    d.project.characters.append(Character(id="c1", role="hero"))
    d.start_cycle("test")
    d.fast_forward_to(DirectorState.PLAN)
    # plan() should succeed now
    intent = d.plan()
    assert intent is not None


# ============================================================================
# CycleContext
# ============================================================================

def test_cycle_context_defaults():
    ctx = CycleContext()
    assert ctx.state == DirectorState.IDLE
    assert ctx.turn_count == 0
    assert len(ctx.cycle_id) == 8  # hex uuid prefix


def test_cycle_context_carries_input():
    ctx = CycleContext(user_input="make a short film")
    assert "short film" in ctx.user_input


# ============================================================================
# start_cycle requires IDLE
# ============================================================================

def test_start_cycle_only_from_idle():
    d = Director()
    d.start_cycle("first")
    d.transition_to(DirectorState.PLAN)
    # Cannot start another cycle from PLAN
    with pytest.raises(StateError):
        d.start_cycle("second")
