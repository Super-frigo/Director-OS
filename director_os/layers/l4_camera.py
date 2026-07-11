"""L4: 镜头语法 — Camera Grammar.

Extracts: action rhythm, dialogue tension, plot turn points
Outputs:  shot sequence + camera layout + timeline storyboard
"""

from .base import BaseLayer


# Shot type → narrative function mapping
SHOT_FUNCTION_MAP = {
    "els": "establishing_context",
    "est": "establishing_context",
    "ls": "spatial_context",
    "mls": "character_environment",
    "ms": "character_action",
    "mcu": "character_focus",
    "cu": "emotional_detail",
    "ecu": "intense_detail",
}

SHOT_TENSION_MAP = {
    "static": "neutral",
    "slow_push": "building",
    "slow_pull": "releasing",
    "handheld": "unstable",
    "tracking": "following",
    "dolly_in": "intensifying",
    "dolly_out": "distancing",
    "crane": "revealing",
    "whip_pan": "abrupt_shift",
    "zoom_in": "focusing",
}


class CameraLayer(BaseLayer):
    """L4: Extract camera grammar — shot sequence, rhythm, and coverage."""

    def analyze(self, context: dict) -> dict:
        shots = context.get("shots", [])
        intent = context.get("intent", {})
        cam = intent.get("camera_strategy", {})
        temporal = intent.get("temporal_design", {})

        shot_sequence = []
        for i, shot in enumerate(shots):
            framing = shot.get("framing", "").lower()
            movement = shot.get("movement", "").lower()
            lens = shot.get("lens", "")
            action = shot.get("action", "")
            duration = shot.get("duration", "")

            shot_sequence.append({
                "order": i + 1,
                "shot_id": shot.get("shot_id", f"shot_{i+1}"),
                "framing": framing,
                "movement": movement,
                "lens": lens,
                "action": action[:60] if action else "",
                "duration": duration,
                "function": SHOT_FUNCTION_MAP.get(framing, "generic"),
                "tension": SHOT_TENSION_MAP.get(movement, "neutral"),
            })

        # Coverage pattern
        coverage_pattern = self._detect_coverage(shot_sequence)

        # Rhythm analysis
        durations = []
        for s in shot_sequence:
            d = s.get("duration", "")
            try:
                durations.append(float(d.replace("s", "")))
            except (ValueError, AttributeError):
                pass

        avg_duration = sum(durations) / len(durations) if durations else 0
        if avg_duration > 6:
            pacing = "slow"
        elif avg_duration > 3:
            pacing = "medium"
        else:
            pacing = "fast"

        return {
            "shot_count": len(shot_sequence),
            "shot_sequence": shot_sequence,
            "coverage_pattern": coverage_pattern,
            "pacing": pacing,
            "avg_shot_duration": round(avg_duration, 1),
            "primary_framing": cam.get("framing", ""),
            "primary_movement": temporal.get("motion_style", cam.get("movement", "")),
            "storyboard_summary": self._summarize_sequence(shot_sequence),
        }

    @staticmethod
    def _detect_coverage(seq: list) -> str:
        """Detect coverage pattern from shot sequence."""
        framings = [s["framing"] for s in seq]
        wide_count = sum(1 for f in framings if f in ("els", "ls", "mls"))
        close_count = sum(1 for f in framings if f in ("cu", "ecu", "mcu"))
        if close_count > wide_count:
            return "close_up_dominated"
        elif wide_count > close_count:
            return "wide_establishing_dominated"
        else:
            return "balanced"

    @staticmethod
    def _summarize_sequence(seq: list) -> str:
        """Create a one-line storyboard summary."""
        if not seq:
            return ""
        parts = []
        for s in seq:
            label = f"{s['framing'] or '?'}"
            if s['movement']:
                label += f"+{s['movement']}"
            parts.append(label)
        return " → ".join(parts)
