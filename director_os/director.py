"""Director — the single public interface to Director OS."""

from pathlib import Path

from .models.project import Project
from .models.production_intent import ProductionIntent
from .models.execution_package import ExecutionPackage
from .engine.pipeline import EnginePipeline, EngineInput
from .compilers.seedance.compiler import SeedanceCompiler
from .compilers.veo.compiler import VeoCompiler
from dataclasses import asdict


class Director:
    """Director is the single entry point for all user interactions.

    Flow:  Project → Engine → ProductionIntent → Compiler → ExecutionPackage
    """

    def __init__(self):
        self.project: Project | None = None
        self.intent: ProductionIntent | None = None
        self.engine = EnginePipeline()
        # Knowledge Resolution (ADR-008): multi-provider pipeline
        from .knowledge import KnowledgeResolver, LocalRulesProvider
        self.resolver = KnowledgeResolver()
        self.resolver.register(LocalRulesProvider())

        # Try to initialize LLM provider from environment
        self._init_llm_provider()
        self._compilers = {
            "seedance": SeedanceCompiler,
            "veo": VeoCompiler,
        }

    def load_project(self, path: str | Path) -> Project:
        from .loader import load_project
        self.project = load_project(path)
        return self.project

    def new_project(self, title: str = "", premise: str = "") -> Project:
        self.project = Project()
        self.project.metadata.title = title
        self.project.story.premise = premise
        return self.project

    def plan(self) -> ProductionIntent:
        """Run Engine: Project → ProductionIntent."""
        if not self.project:
            raise RuntimeError("No project loaded. Call load_project() or new_project() first.")
        inp = EngineInput(
            project=self.project,
            resolver=self.resolver,  # ADR-008: Knowledge Resolution pipeline
        )
        self.intent = self.engine.run(inp)
        return self.intent

    def compile(self, platform: str = "seedance") -> ExecutionPackage:
        """Run Compiler: ProductionIntent → ExecutionPackage."""
        if not self.intent:
            raise RuntimeError("No intent. Call plan() first.")
        cls = self._compilers.get(platform)
        if cls is None:
            available = ", ".join(self._compilers)
            raise ValueError(f"Unknown compiler {platform!r}. Available: {available}")
        compiler = cls()
        # Convert ProductionIntent dataclass → plain dict (compiler contract)
        intent_dict = asdict(self.intent)
        # Run 6-layer analysis
        shot_out = self.engine.engines["shot"].process(EngineInput(project=self.project))
        shots_data = shot_out.get("shots", [])
        layers = self.engine.analyze_layers(self.project, intent_dict, shots_data)
        # Compile with layer context
        result = compiler.compile_with_layers(intent_dict, layers)
        pkg = result.get("execution_package", {})
        return ExecutionPackage(
            target=pkg.get("target", {}),
            instructions=pkg.get("instructions", {}),
            parameters=pkg.get("parameters", {}),
            validation=pkg.get("validation", {}),
            schema_version=pkg.get("schema_version", "1.0"),
        )

    def validate_project(self) -> list[str]:
        if not self.project:
            return ["No project loaded"]
        return self.project.validate()

    def _init_llm_provider(self) -> None:
        """Initialize LLM provider from environment variables if available.

        Set OPENAI_API_KEY to enable LLM-powered knowledge resolution.
        Set OPENAI_BASE_URL for non-OpenAI providers (DeepSeek, etc.).
        Set OPENAI_MODEL to override the default model (gpt-4o).
        """
        import os
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return  # No LLM configured — local rules only

        try:
            from .knowledge import LLMProvider, CacheManager
            from .knowledge.llm_client import OpenAIClient

            model = os.getenv("OPENAI_MODEL", "gpt-4o")
            base_url = os.getenv("OPENAI_BASE_URL", "")

            client = OpenAIClient(
                api_key=api_key,
                model=model,
                base_url=base_url,
            )
            cache = CacheManager()
            self.resolver.set_cache(cache)
            self.resolver.register(LLMProvider(client=client, cache_manager=cache))
        except Exception:
            pass  # LLM init failure is non-fatal — local rules still work
