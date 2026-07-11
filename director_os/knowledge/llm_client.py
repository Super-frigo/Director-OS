"""LLM Client abstraction — plug any model into the Knowledge Resolver.

Usage:
    from director_os.knowledge.llm_client import OpenAIClient

    client = OpenAIClient(api_key="sk-...", model="gpt-5")
    # or: client = OpenAIClient(base_url="https://api.deepseek.com/v1", ...)

    provider = LLMProvider(client=client, cache_manager=CacheManager())
    resolver.register(provider)
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """Protocol that any LLM client must satisfy.

    Implementations must provide:
    - chat(system, user) -> str: send a chat completion and return text
    - model_name: str property identifying the model
    """

    def chat(self, system: str, user: str) -> str:
        """Send a chat completion and return the response text."""
        ...

    @property
    def model_name(self) -> str:
        """Return the model identifier (e.g. 'gpt-5', 'claude-4')."""
        ...


class OpenAIClient:
    """LLM client for OpenAI-compatible APIs.

    Works with:
    - OpenAI (api_key + model)
    - DeepSeek (base_url="https://api.deepseek.com/v1")
    - Any OpenAI-compatible proxy or local server (Ollama, vLLM, etc.)

    Requires: pip install openai
    """

    def __init__(
        self,
        api_key: str = "",
        model: str = "gpt-4o",
        base_url: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2000,
        timeout: float = 30.0,
    ):
        self._api_key = api_key
        self._model = model
        self._base_url = base_url
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout
        self._client = None

    @property
    def model_name(self) -> str:
        return self._model

    def _get_client(self):
        """Lazy-init the OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError(
                    "OpenAI client requires 'pip install openai'. "
                    "For other LLM providers, implement the LLMClient protocol."
                )
            kwargs = {"api_key": self._api_key, "timeout": self._timeout, "max_retries": 2}
            if self._base_url:
                kwargs["base_url"] = self._base_url
            self._client = OpenAI(**kwargs)
        return self._client

    def chat(self, system: str, user: str) -> str:
        """Send a chat completion and return the text response."""
        client = self._get_client()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})

        response = client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        return response.choices[0].message.content or ""
