"""L5: 角色矩阵 — Character Matrix.

Extracts: character count, identity/relationships, action/facial descriptions
Outputs:  differentiated casting (position/clothing/eyes/micro-expressions)
"""

from .base import BaseLayer


class CharacterLayer(BaseLayer):
    """L5: Extract character differentiation and positioning."""

    def analyze(self, context: dict) -> dict:
        project = context.get("project")
        intent = context.get("intent", {})
        shots = context.get("shots", [])

        characters = []
        if project and hasattr(project, "characters"):
            for ch in project.characters:
                entry = {
                    "id": ch.id,
                    "name": ch.name,
                    "role": ch.role,
                    "appearance": ch.visual_identity.appearance if hasattr(ch, "visual_identity") and ch.visual_identity else "",
                    "wardrobe": ch.visual_identity.clothing if hasattr(ch, "visual_identity") and ch.visual_identity else "",
                }

                # Find first action in shot list
                for shot in shots:
                    action = shot.get("action", "")
                    if ch.id in action or ch.name in action:
                        entry["first_action"] = action[:80]
                        break

                characters.append(entry)

        # Character directions from intent
        char_dirs = intent.get("character_direction", [])

        # Build visual differentiation for consistency
        differentiation = []
        for ch in characters:
            diff = {
                "id": ch["id"],
                "name": ch["name"],
                "visual_key": f"{ch.get('wardrobe', '')} | {ch.get('appearance', '')}",
            }
            differentiation.append(diff)

        return {
            "character_count": len(characters),
            "characters": characters,
            "main_character": characters[0] if characters else {},
            "supporting_characters": characters[1:] if len(characters) > 1 else [],
            "differentiation": differentiation,
            "presence_in_shots": self._map_shot_presence(characters, shots),
        }

    @staticmethod
    def _map_shot_presence(characters: list, shots: list) -> list:
        """Map which characters appear in which shots."""
        presence = []
        for ch in characters:
            shot_ids = []
            for shot in shots:
                action = shot.get("action", "")
                sid = shot.get("shot_id", "")
                if ch["id"] in action or ch["name"] in action:
                    shot_ids.append(sid)
            if shot_ids:
                presence.append({
                    "character": ch["id"],
                    "shots": shot_ids,
                })
        return presence
