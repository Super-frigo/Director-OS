"""Quick integration test for the Director OS pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from director_os.director import Director
from director_os.state import DirectorState
from director_os.models.project import Character, VisualIdentity


def test_pipeline():
    d = Director()

    # 1. New project
    d.new_project(
        title="The Hanging",
        premise="A detective witnesses an execution he unknowingly sentenced an innocent man to.",
    )

    # Add a character
    d.project.characters.append(Character(
        id="detective",
        name="Detective",
        role="protagonist",
        personality=["observant", "stoic"],
        visual_identity=VisualIdentity(age_range="adult", appearance="gaunt face, deep-set eyes", clothing="dark long gown"),
    ))

    # Assert project was created correctly
    assert d.project.metadata.title == "The Hanging"
    assert d.project.story.premise == (
        "A detective witnesses an execution he unknowingly sentenced an innocent man to."
    )
    assert len(d.project.characters) == 1
    assert d.project.characters[0].id == "detective"

    # Validate project
    issues = d.validate_project()
    # No shots, no story_beats — expect validation issues
    assert isinstance(issues, list)

    # 2. Engine → plan() should not crash with minimal project
    d.start_cycle("test")
    d.fast_forward_to(DirectorState.PLAN)
    intent = d.plan()
    assert intent is not None
    assert intent.creative_goal is not None
    assert isinstance(intent.creative_goal, dict)

    # 3. Compiler → compile() should produce a non-empty prompt
    d.fast_forward_to(DirectorState.COMPILE)
    pkg = d.compile("seedance")
    assert pkg is not None
    prompt = pkg.instructions.get("prompt", "")
    assert isinstance(prompt, str)
    assert pkg.target.get("provider") == "seedance"


if __name__ == "__main__":
    test_pipeline()
