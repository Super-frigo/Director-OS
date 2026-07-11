"""Quick integration test for the Director OS pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from director_os.director import Director
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

    print(f"1. Project: {d.project.metadata.title}")
    issues = d.validate_project()
    print(f"   Premise: {d.project.story.premise}")
    print(f"   Issues:  {issues if issues else 'None'}")

    # 2. Engine
    intent = d.plan()
    print(f"\n2. Production Intent generated")
    print(f"   Creative Goal: {intent.creative_goal.get('primary', '')[:60]}")

    # 3. Compiler
    pkg = d.compile("seedance")
    prompt = pkg.instructions.get("prompt", "")
    print(f"\n3. Seedance Prompt:")
    print(f"   {prompt[:120] if prompt else '(empty - minimal project has no shot data)'}")
    print(f"\n   Target provider: {pkg.target.get('provider', '')}")

    print("\nPipeline test passed")


if __name__ == "__main__":
    test_pipeline()
