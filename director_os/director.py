"""Director — the single public interface to Director OS."""

from pathlib import Path

from .models.project import Project
from .models.production_intent import ProductionIntent
from .models.execution_package import ExecutionPackage
from .engine.pipeline import EnginePipeline, EngineInput
from .compilers.seedance.compiler import SeedanceCompiler
from .compilers.veo.compiler import VeoCompiler
from dataclasses import asdict
from .library.loader import LibraryLoader


class Director:
    """Director is the single entry point for all user interactions.

    Flow:  Project → Engine → ProductionIntent → Compiler → ExecutionPackage
    """

    def __init__(self):
        self.project: Project | None = None
        self.intent: ProductionIntent | None = None
        self.engine = EnginePipeline()
        self.library = LibraryLoader()
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
            libraries=self.library._by_category,
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
