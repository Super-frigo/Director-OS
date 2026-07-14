"""Translation layer for free-text fields in compiler prompts.

Reuses the LLMClient protocol from director_os/knowledge/llm_client.py
for architectural consistency (ADR-008). Caches translations in the same
llm_cache directory for determinism — identical input always produces
identical output.

Usage:
    from director_os.compilers.translation import Translator, translate_to_english

    # Auto-detect LLM from environment
    translator = Translator.create()

    # Or inject a custom LLM client
    from director_os.knowledge.llm_client import OpenAIClient
    translator = Translator(client=OpenAIClient(api_key="..."))

    # Module-level convenience for mapper.py integration
    translate_to_english("一部民国黑色悬疑短片")

Design:
    - No LLM client -> returns original text silently (non-fatal)
    - No CJK characters -> passthrough immediately, no cache, no LLM call
    - Chinese/mixed text -> LLM translation, cached by content hash
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from director_os.knowledge.llm_client import LLMClient

_HAS_CJK = re.compile(r'[\u4e00-\u9fff]')


class TranslationCache:
    """Simple content-addressed text-to-text translation cache.

    Stores in knowledge/providers/llm_cache/translation_cache.yaml
    alongside the existing LLM knowledge cache.
    """

    def __init__(self, cache_dir: str | Path | None = None):
        if cache_dir is None:
            cache_dir = (
                Path(__file__).resolve().parent.parent.parent
                / "knowledge" / "providers" / "llm_cache"
            )
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_file = self.cache_dir / "translation_cache.yaml"
        self._data: dict[str, str] = {}
        self._load()

    @staticmethod
    def _key(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    def _load(self) -> None:
        if self._cache_file.exists():
            try:
                loaded = yaml.safe_load(
                    self._cache_file.read_text(encoding="utf-8-sig")
                )
                if isinstance(loaded, dict):
                    self._data = loaded
            except Exception:
                self._data = {}

    def _save(self) -> None:
        tmp = self._cache_file.with_suffix(".tmp")
        tmp.write_text(
            yaml.safe_dump(self._data, allow_unicode=True), encoding="utf-8"
        )
        tmp.replace(self._cache_file)

    def get(self, text: str) -> str | None:
        key = self._key(text)
        return self._data.get(key)

    def put(self, text: str, translated: str) -> None:
        key = self._key(text)
        self._data[key] = translated
        self._save()


class Translator:
    """Translates free-text fields to English via an LLM client, with caching.

    Follows the same LLMClient protocol contract as LLMProvider (ADR-008).
    No client -> passthrough mode (non-fatal, same as Director._init_llm_provider).
    """

    SYSTEM_PROMPT = (
        "You are a film production translator. Translate the given Chinese text "
        "into natural, cinematic English suitable for an AI video generation prompt. "
        "Preserve the emotional tone and visual specificity. "
        "Return ONLY the translated text - no explanations, no quotes, no prefixes."
    )

    def __init__(self, client: LLMClient | None = None, cache_dir: str | Path | None = None):
        self._client = client
        self._cache = TranslationCache(cache_dir=cache_dir)

    @classmethod
    def create(cls) -> Translator:
        """Factory: auto-detect LLM from OPENAI_API_KEY environment variable.

        Returns a Translator in passthrough mode if no key is set.
        """
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return cls(client=None)

        try:
            from director_os.knowledge.llm_client import OpenAIClient

            model = os.getenv("OPENAI_MODEL", "gpt-4o")
            base_url = os.getenv("OPENAI_BASE_URL", "")
            client = OpenAIClient(
                api_key=api_key,
                model=model,
                base_url=base_url,
            )
            return cls(client=client)
        except Exception:
            return cls(client=None)

    @property
    def has_client(self) -> bool:
        return self._client is not None

    def translate(self, text: str) -> str:
        """Translate text to English.

        Resolution order:
            1. Empty/pure-ASCII text → returned unchanged.
            2. LLM client configured → fluent translation, cached.
            3. No client → offline glossary fallback (literal, term-by-term).

        Returns original text only if it contains no CJK, or on LLM error
        with no glossary coverage.
        """
        if not text or not text.strip():
            return text

        # CJK gate: no Chinese characters -> passthrough (no cache, no LLM)
        if not _HAS_CJK.search(text):
            return text

        # Path 2: LLM translation (cached for determinism)
        if self._client:
            cached = self._cache.get(text)
            if cached is not None:
                return cached
            try:
                result = self._client.chat(self.SYSTEM_PROMPT, text)
                result = result.strip().strip('"').strip("'")
                if result:
                    self._cache.put(text, result)
                    return result
            except Exception:
                pass  # fall through to offline glossary

        # Path 3: offline glossary fallback (no LLM required)
        from .offline_glossary import translate_offline
        return translate_offline(text)

        # Deterministic: check cache
        cached = self._cache.get(text)
        if cached is not None:
            return cached

        try:
            result = self._client.chat(self.SYSTEM_PROMPT, text)
            result = result.strip().strip('"').strip("'")
            if result:
                self._cache.put(text, result)
                return result
        except Exception:
            pass

        return text


# -- Module-level singleton for mapper.py integration -------------------------

_translator: Translator | None = None


def set_translator(translator: Translator | None) -> None:
    """Set the module-level translator singleton (called during compiler init)."""
    global _translator
    _translator = translator


def translate_to_english(text: str) -> str:
    """Convenience: translate a single text string through the module-level translator.

    Returns the original text unchanged if no translator is configured.
    """
    if _translator is None:
        return text
    return _translator.translate(text)
