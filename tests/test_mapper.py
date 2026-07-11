"""Unit tests for Seedance mapper — translation accuracy."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from director_os.compilers.seedance.mapper import (
    map_camera_movement,
    map_framing,
    map_lens,
    map_film_stock,
    map_camera_body,
    map_render_engine,
    map_render_settings,
    map_color_grade,
)


def test_map_camera_movement():
    assert "cinematic push" in map_camera_movement("slow_push")
    assert "static" in map_camera_movement("static")
    assert "tracking" in map_camera_movement("tracking")
    assert "" == map_camera_movement("")
    assert "custom_move" == map_camera_movement("custom_move")  # passthrough


def test_map_framing():
    assert "wide shot" in map_framing("wide")
    assert "close-up" in map_framing("cu")
    assert "medium shot" in map_framing("ms")
    assert "extreme close-up" in map_framing("ecu")
    assert "" == map_framing("")


def test_map_lens():
    assert "24mm" in map_lens("24mm")
    assert "50mm" in map_lens("50mm")
    assert "" == map_lens("")


def test_map_film_stock():
    desc = map_film_stock("Kodak Portra 400")
    assert desc and "warm" in desc
    assert "grain" in desc
    assert "" == map_film_stock("")


def test_map_camera_body():
    desc = map_camera_body("ARRI Alexa65")
    assert desc and "Alexa 65" in desc
    assert "6K" in desc
    assert "" == map_camera_body("")


def test_map_render_engine():
    desc = map_render_engine("PBR")
    assert desc and "physically" in desc.lower()
    assert "" == map_render_engine("")


def test_map_render_settings():
    desc = map_render_settings("全局光照+SSS, 8K输出")
    assert desc
    assert "global illumination" in desc.lower() or "illumination" in desc.lower()
    assert "8K" in desc


def test_map_color_grade():
    desc = map_color_grade("暖棕基底冷青灰调")
    assert desc and "brown" in desc.lower()
    assert "teal" in desc.lower()
    assert "" == map_color_grade("")

