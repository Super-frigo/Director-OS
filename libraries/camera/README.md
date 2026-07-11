# Camera Library

Status: Active

## Purpose

Camera Library stores camera design and focal length knowledge for Camera Agent reference during planning and design.

## Structure

Each entry follows `library.schema.yaml` format.

## Categories

### Focal Length
- [24mm Wide](entries/lens_24mm_wide.yaml) — Environmental context and distortion
- [35mm Standard](entries/lens_35mm_standard.yaml) — The human eye equivalent
- [50mm Portrait](entries/lens_50mm_portrait.yaml) — Natural perspective, minimal distortion
- [85mm Compression](entries/lens_85mm_compression.yaml) — Emotional isolation and intimacy

### Camera Height
- [Low Angle](entries/height/height_low_angle.yaml) — Power, monumentality, threat
- [Eye Level](entries/height/height_eye_level.yaml) — Neutral, immersive, intimate
- [High Angle](entries/height/height_high_angle.yaml) — Vulnerability, surveillance, fate
- [Bird's Eye](entries/height/height_birds_eye.yaml) — Omniscient, pattern, finality

### Camera Angle
- [Front](entries/angle/angle_front.yaml) — Confrontation, honesty, direct address
- [Side](entries/angle/angle_side.yaml) — Observation, distance, silhouette
- [Back](entries/angle/angle_back.yaml) — Following, mystery, journey
- [Three-Quarter](entries/angle/angle_three_quarter.yaml) — Narrative workhorse, most versatile
- [Over-the-Shoulder](entries/angle/angle_ots.yaml) — Dialogue standard, spatial relationship
- [Dutch Angle](entries/angle/angle_dutch.yaml) — Instability, dread, disorientation

### Shot Size
- [Shot Size Reference](entries/shot_size/shot_size_reference.yaml) — ECU to ELS framing guide

### Camera Movement
- [Static](entries/movement/movement_static.yaml) — Locked-off observation
- [Dolly In](entries/movement/movement_dolly_in.yaml) — Approach and intensification
- [Push-In / Pull-Out](entries/movement/movement_push_pull.yaml) — Emotional approach and retreat
- [Tracking](entries/movement/movement_tracking.yaml) — Side-by-side movement
- [Handheld](entries/movement/movement_handheld.yaml) — Urgency and realism
- [Steadicam](entries/movement/movement_steadicam.yaml) — Flowing subjective movement
- [Follow Shot](entries/movement/movement_follow.yaml) — Walking beside the character
- [Crane / Jib](entries/movement/movement_crane.yaml) — Vertical movement, scale reveal

## Usage

Camera Agent queries this library during DESIGN stage to select or recommend lens configurations for each Shot.
