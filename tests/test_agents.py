"""Tests for the agent system — AgentBase, AgentProposal, StoryAgent,
CameraAgent, ContinuityAgent, and Director.run_agent_cycle()."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from director_os.agents.base import (
    AgentBase, AgentProposal, AgentRequest, AgentResult,
)
from director_os.agents import StoryAgent, CameraAgent, ContinuityAgent
from director_os.director import Director
from director_os.state import DirectorState


# ============================================================================
# AgentProposal dataclass
# ============================================================================

def test_agent_proposal_defaults():
    p = AgentProposal()
    assert p.agent == ""
    assert p.action == ""
    assert p.confidence == 1.0
    assert len(p.proposal_id) == 8


def test_agent_proposal_repr():
    p = AgentProposal(
        agent="camera_agent",
        module="shots",
        field="shots[0].framing",
        action="set",
        value="CU",
        confidence=0.9,
    )
    r = repr(p)
    assert "camera_agent" in r
    assert "CU" in r
    assert "90%" in r


# ============================================================================
# AgentBase protocol
# ============================================================================

def test_agent_base_defaults():
    a = AgentBase()
    assert a.agent_name == "base"
    assert a.bound_domains == []


def test_agent_base_project_slice():
    a = AgentBase()
    assert a.read_project_slice(None) == {}


def test_agent_base_make_proposal():
    a = AgentBase()
    p = a._make_proposal("story", "premise", "set", "A test", "just because", 0.8)
    assert p.agent == "base"
    assert p.module == "story"
    assert p.field == "premise"
    assert p.value == "A test"
    assert p.rationale == "just because"
    assert p.confidence == 0.8


# ============================================================================
# StoryAgent
# ============================================================================

def test_story_agent_name_and_domains():
    a = StoryAgent()
    assert a.agent_name == "story_agent"
    assert "storytelling" in a.bound_domains


def test_story_agent_project_slice():
    from director_os.models.project import Project, Metadata, Story, StoryBeat
    p = Project(
        metadata=Metadata(title="Test"),
        story=Story(premise="A noir mystery", genre=["noir", "suspense"]),
        story_beats=[
            StoryBeat(beat="b1", type="OPENING", emotion="tension"),
        ],
    )
    a = StoryAgent()
    s = a.read_project_slice(p)
    assert "A noir mystery" in s["premise"]
    assert "noir" in s["genre"]
    assert len(s["beats"]) == 1
    assert s["beats"][0]["type"] == "OPENING"


def test_story_agent_propose_noir():
    a = StoryAgent()
    req = AgentRequest(
        agent="story_agent",
        project_slice={"premise": "mystery", "genre": ["noir"], "beats": []},
        context={"genre": "noir", "emotion": "tension"},
    )
    result = a.propose(req)
    assert isinstance(result, AgentResult)
    assert len(result.proposals) > 0
    # Should include beat recommendations
    assert any("story_beats" in p.module for p in result.proposals)
    # Should include some story proposals
    assert any(p.module == "story" for p in result.proposals)


def test_story_agent_propose_scifi():
    a = StoryAgent()
    req = AgentRequest(
        agent="story_agent",
        project_slice={"premise": "space", "genre": ["sci-fi"], "beats": []},
        context={"genre": "sci-fi", "emotion": "awe"},
    )
    result = a.propose(req)
    assert len(result.proposals) > 0
    # Discovery beat should appear for scifi
    texts = [p.rationale for p in result.proposals]
    assert any("sci" in t.lower() or "awe" in t.lower() for t in texts)


# ============================================================================
# CameraAgent
# ============================================================================

def test_camera_agent_name_and_domains():
    a = CameraAgent()
    assert a.agent_name == "camera_agent"
    assert "camera" in a.bound_domains
    assert "lighting" in a.bound_domains


def test_camera_agent_propose_tension():
    a = CameraAgent()
    req = AgentRequest(
        agent="camera_agent",
        project_slice={
            "visual_style": "noir",
            "shots": [
                {"shot_id": "S1", "framing": "", "lens": "", "emotion": "tension"},
            ],
        },
        context={"emotion": "tension"},
    )
    result = a.propose(req)
    assert len(result.proposals) > 0
    # Tension maps to MS framing, 50mm lens
    framings = [p.value for p in result.proposals if "framing" in p.field]
    assert "MS" in framings or any(f in str(framings) for f in ["MS"])


def test_camera_agent_propose_intimacy():
    a = CameraAgent()
    req = AgentRequest(
        agent="camera_agent",
        project_slice={
            "visual_style": "romance",
            "shots": [
                {"shot_id": "S1", "framing": "", "lens": "", "emotion": "intimacy"},
            ],
        },
        context={"emotion": "intimacy"},
    )
    result = a.propose(req)
    # Intimacy → CU + 85mm
    lenses = [p.value for p in result.proposals if "lens" in p.field]
    assert "85mm" in lenses


# ============================================================================
# ContinuityAgent
# ============================================================================

def test_continuity_agent_name():
    a = ContinuityAgent()
    assert a.agent_name == "continuity_agent"


def test_continuity_detects_locked_character():
    a = ContinuityAgent()
    req = AgentRequest(
        agent="continuity_agent",
        project_slice={
            "characters": [
                {"id": "c1", "name": "Detective", "continuity_lock": True,
                 "wardrobe": "", "physical_state": ""},
            ],
            "shots": [],
            "world_weather": "",
            "world_season": "",
            "constraints_avoid": [],
            "constraints_required": [],
        },
        context={},
    )
    result = a.propose(req)
    assert len(result.proposals) > 0
    assert any("Detective" in p.rationale for p in result.proposals)


def test_continuity_detects_undefined_character_ref():
    a = ContinuityAgent()
    req = AgentRequest(
        agent="continuity_agent",
        project_slice={
            "characters": [{"id": "c1", "name": "Hero"}],
            "shots": [
                {"shot_id": "S1", "order": 1, "subject_character": "ghost",
                 "subject_action": "", "notes": ""},
            ],
            "world_weather": "",
            "world_season": "",
            "constraints_avoid": [],
            "constraints_required": [],
        },
        context={},
    )
    result = a.propose(req)
    assert len(result.warnings) > 0
    assert any("ghost" in w for w in result.warnings)


# ============================================================================
# Director.run_agent_cycle()
# ============================================================================

def test_run_agent_cycle_in_plan_state():
    d = Director()
    d.new_project("Noir Film", "A detective story")
    from director_os.models.project import Character, StoryBeat, Shot, Subject
    d.project.characters.append(Character(id="c1", name="Detective", role="protagonist"))
    d.project.story_beats.append(StoryBeat(beat="b1", type="OPENING"))
    d.project.shots.append(Shot(shot_id="S1", order=1, subject=Subject(character="c1")))

    d.start_cycle("make a noir film")
    d.fast_forward_to(DirectorState.PLAN)

    result = d.run_agent_cycle()
    assert "proposals" in result
    assert "state" in result
    assert result["state"] == "plan"
    assert len(result["proposals"]) > 0


def test_run_agent_cycle_no_project():
    d = Director()
    with pytest.raises(RuntimeError, match="No project"):
        d.run_agent_cycle()


def test_run_agent_cycle_in_idle_state():
    d = Director()
    d.new_project("T", "P")
    result = d.run_agent_cycle()
    # IDLE has no agents mapped
    assert result["proposals"] == []
    assert len(result["warnings"]) > 0
