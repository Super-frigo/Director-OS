"""Tests for the translation layer (director_os/compilers/translation.py)."""

from unittest.mock import MagicMock

import pytest

from director_os.compilers.translation import (
    Translator,
    TranslationCache,
    translate_to_english,
    set_translator,
)


# ============================================================================
# TranslationCache
# ============================================================================

def test_cache_put_and_get(tmp_path):
    cache = TranslationCache(cache_dir=tmp_path)
    cache.put("hello world", "translated")
    assert cache.get("hello world") == "translated"


def test_cache_miss_returns_none(tmp_path):
    cache = TranslationCache(cache_dir=tmp_path)
    assert cache.get("never stored") is None


def test_cache_persists_across_instances(tmp_path):
    cache1 = TranslationCache(cache_dir=tmp_path)
    cache1.put("persist me", "translated text")
    cache2 = TranslationCache(cache_dir=tmp_path)
    assert cache2.get("persist me") == "translated text"


def test_cache_deterministic_key():
    key1 = TranslationCache._key("some text")
    key2 = TranslationCache._key("some text")
    assert key1 == key2
    assert len(key1) == 16


# ============================================================================
# CJK short-circuit
# ============================================================================

def test_cjk_gate_english_passthrough_no_client_call(tmp_path):
    """Pure English input should NOT trigger LLM call (CJK gate)."""
    mock_client = MagicMock()
    mock_client.chat.return_value = "SHOULD NOT BE CALLED"
    mock_client.model_name = "test"

    t = Translator(client=mock_client, cache_dir=tmp_path)
    result = t.translate("ARRI Alexa65")
    assert result == "ARRI Alexa65"
    mock_client.chat.assert_not_called()


def test_cjk_gate_english_passthrough_no_cache_write(tmp_path):
    """Pure English should NOT write to cache (CJK gate skips cache entirely)."""
    mock_client = MagicMock()
    mock_client.model_name = "test"

    t = Translator(client=mock_client, cache_dir=tmp_path)
    t.translate("Some English sentence")
    assert t._cache.get("Some English sentence") is None


def test_cjk_gate_chinese_triggers_translation(tmp_path):
    """Chinese input SHOULD trigger LLM call."""
    mock_client = MagicMock()
    mock_client.chat.return_value = "Swirly bokeh"
    mock_client.model_name = "test"

    t = Translator(client=mock_client, cache_dir=tmp_path)
    result = t.translate("\u65cb\u7126\u6563\u666f")
    assert result == "Swirly bokeh"
    mock_client.chat.assert_called_once()


def test_cjk_gate_mixed_cjk_english_triggers_translation(tmp_path):
    """Mixed CJK+ASCII input should trigger LLM."""
    mock_client = MagicMock()
    mock_client.chat.return_value = "translated"
    mock_client.model_name = "test"

    t = Translator(client=mock_client, cache_dir=tmp_path)
    result = t.translate("\u4f7f\u7528 ARRI Alexa65 \u62cd\u6444")
    assert result == "translated"
    mock_client.chat.assert_called_once()


def test_cjk_gate_symbols_only_passthrough(tmp_path):
    """Symbol-only input (no CJK) should passthrough."""
    mock_client = MagicMock()
    mock_client.model_name = "test"

    t = Translator(client=mock_client, cache_dir=tmp_path)
    result = t.translate("els+static -> ms+static")
    assert result == "els+static -> ms+static"
    mock_client.chat.assert_not_called()


# ============================================================================
# Translator - no client
# ============================================================================

def test_translator_no_client_returns_original():
    t = Translator(client=None)
    result = t.translate("some text")
    assert result == "some text"


def test_translator_no_client_empty_string():
    t = Translator(client=None)
    assert t.translate("") == ""
    assert t.translate("   ") == "   "


# ============================================================================
# Translator - with mock client
# ============================================================================

def test_translator_with_client_translates(tmp_path):
    mock_client = MagicMock()
    mock_client.chat.return_value = "A short Republican-era noir film"
    mock_client.model_name = "test-model"

    t = Translator(client=mock_client, cache_dir=tmp_path)
    result = t.translate("\u4e00\u90e8\u6c11\u56fd\u9ed1\u8272\u60ac\u7591\u77ed\u7247")
    assert result == "A short Republican-era noir film"
    mock_client.chat.assert_called_once()


def test_translator_caches_and_reuses(tmp_path):
    """Same input twice -> second call hits cache, client called only once."""
    mock_client = MagicMock()
    mock_client.chat.return_value = "translated output"
    mock_client.model_name = "test-model"

    t = Translator(client=mock_client, cache_dir=tmp_path)
    r1 = t.translate("\u91cd\u590d\u8f93\u5165\u6587\u672c")
    r2 = t.translate("\u91cd\u590d\u8f93\u5165\u6587\u672c")
    assert r1 == "translated output"
    assert r2 == "translated output"
    mock_client.chat.assert_called_once()


def test_translator_client_error_returns_original(tmp_path):
    mock_client = MagicMock()
    mock_client.chat.side_effect = RuntimeError("API down")
    mock_client.model_name = "test-model"

    t = Translator(client=mock_client, cache_dir=tmp_path)
    result = t.translate("\u4e00\u4e9b\u4e2d\u6587\u6587\u672c")
    assert result == "\u4e00\u4e9b\u4e2d\u6587\u6587\u672c"


def test_translator_has_client():
    mock_client = MagicMock()
    mock_client.model_name = "test"
    t = Translator(client=mock_client)
    assert t.has_client is True

    t2 = Translator(client=None)
    assert t2.has_client is False


# ============================================================================
# Module-level singleton
# ============================================================================

def test_set_translator_and_translate_to_english(tmp_path):
    mock_client = MagicMock()
    mock_client.chat.return_value = "English result"
    mock_client.model_name = "test"

    t = Translator(client=mock_client, cache_dir=tmp_path)
    set_translator(t)
    result = translate_to_english("\u4e2d\u6587\u8f93\u5165")
    assert result == "English result"
    set_translator(None)


def test_translate_to_english_no_translator_set():
    set_translator(None)
    result = translate_to_english("\u4efb\u610f\u6587\u672c")
    assert result == "\u4efb\u610f\u6587\u672c"


# ============================================================================
# Translator.create() factory
# ============================================================================

def test_translator_create_no_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    t = Translator.create()
    assert t.has_client is False
    assert t.translate("hello") == "hello"


# ============================================================================
# Integration: SeedanceCompiler
# ============================================================================

def test_seedance_compiler_accepts_translator():
    from director_os.compilers.seedance.compiler import SeedanceCompiler

    mock_client = MagicMock()
    mock_client.chat.return_value = "A detective"
    mock_client.model_name = "test"

    translator = Translator(client=mock_client)
    compiler = SeedanceCompiler(translator=translator)
    assert compiler.prompt_builder._tr is translator


def test_seedance_compiler_translates_free_text(tmp_path):
    from director_os.compilers.seedance.compiler import SeedanceCompiler

    mock_client = MagicMock()
    mock_client.chat.return_value = "ENGLISH OUTPUT"
    mock_client.model_name = "test"

    translator = Translator(client=mock_client, cache_dir=tmp_path)
    compiler = SeedanceCompiler(translator=translator)

    intent = {
        "visual_direction": {"atmosphere": "\u538b\u6291\u7684\u591c\u665a", "mood": ["tension"]},
        "camera_strategy": {"framing": "wide_shot"},
        "character_direction": [{"name": "\u4fa6\u63a2", "action": "\u8d70\u8fdb\u5e9f\u5f03\u5de5\u5382"}],
        "narrative_intent": {"premise": "\u4e00\u4e2a\u4fa6\u63a2\u53d1\u73b0\u771f\u76f8"},
    }

    result = compiler.compile(intent)
    prompt = result["execution_package"]["instructions"]["prompt"]
    assert "ENGLISH OUTPUT" in prompt


def test_seedance_compiler_no_translator_preserves_original():
    from director_os.compilers.seedance.compiler import SeedanceCompiler

    compiler = SeedanceCompiler(translator=None)
    intent = {
        "visual_direction": {"atmosphere": "\u538b\u6291\u7684\u591c\u665a"},
        "camera_strategy": {"framing": "wide_shot"},
        "character_direction": [{"name": "\u4fa6\u63a2", "action": "\u8d70\u8fdb\u5e9f\u5f03\u5de5\u5382"}],
        "narrative_intent": {"premise": "\u4e00\u4e2a\u4fa6\u63a2\u53d1\u73b0\u771f\u76f8"},
    }

    result = compiler.compile(intent)
    prompt = result["execution_package"]["instructions"]["prompt"]
    assert "\u4fa6\u63a2" in prompt
