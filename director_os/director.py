"""Director — the single public interface to Director OS."""

from pathlib import Path

from .state import DirectorState, StateError, CycleContext, TRANSITIONS, path_to
from .models.project import Project, HistoryEntry
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
        # State machine (ADR-009 Step 2)
        self.state: DirectorState = DirectorState.IDLE
        self.ctx: CycleContext | None = None
        # Knowledge Resolution (ADR-008): multi-provider pipeline
        from .knowledge import KnowledgeResolver, LocalRulesProvider
        self.resolver = KnowledgeResolver()
        self.resolver.register(LocalRulesProvider())

        # LLM client reference (set by _init_llm_provider)
        self._llm_client: object | None = None

        # Try to initialize LLM provider from environment
        self._init_llm_provider()
        self._compilers = {
            "seedance": SeedanceCompiler,
            "veo": VeoCompiler,
        }
        # Agent registry (ADR-009 Step 3) — lazy init on first use
        self.agents: dict[str, object] = {}

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
        """Run Engine: Project → ProductionIntent.

        Requires PLAN or DESIGN state (STATE_MACHINE §3.4-3.5).
        """
        self._require_state({DirectorState.PLAN, DirectorState.DESIGN})
        if not self.project:
            raise RuntimeError("No project loaded. Call load_project() or new_project() first.")
        inp = EngineInput(
            project=self.project,
            resolver=self.resolver,  # ADR-008: Knowledge Resolution pipeline
        )
        self.intent = self.engine.run(inp)
        return self.intent

    def compile(self, platform: str = "seedance") -> ExecutionPackage:
        """Run Compiler: ProductionIntent → ExecutionPackage.

        Requires COMPILE state (STATE_MACHINE §3.8).
        """
        self._require_state({DirectorState.COMPILE})
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

    # ---- State Machine (ADR-009 Step 2) ------------------------------------

    def start_cycle(self, user_input: str = "") -> CycleContext:
        """Begin a Creative Cycle: IDLE → UNDERSTAND.

        Creates a fresh CycleContext and stores it on the Director.
        The LLM (Director's "brain") calls this when it receives user intent.
        """
        self._require_state({DirectorState.IDLE})
        self.ctx = CycleContext(
            user_input=user_input,
            state=DirectorState.UNDERSTAND,
        )
        self.state = DirectorState.UNDERSTAND
        return self.ctx

    def transition_to(self, target: DirectorState) -> DirectorState:
        """Validate and execute a state transition.

        Raises StateError if *target* is not reachable from the current state.
        Returns the new state on success so the LLM can confirm it.
        """
        legal = TRANSITIONS.get(self.state, set())
        if target not in legal:
            raise StateError(
                f"Cannot transition {self.state.value} → {target.value}. "
                f"Legal next states: {[s.value for s in sorted(legal, key=str)]}"
            )
        self.state = target
        if self.ctx:
            self.ctx.state = target
            self.ctx.turn_count += 1
        return self.state

    def fast_forward_to(self, target: DirectorState) -> DirectorState:
        """Auto-transition through intermediate states to reach *target*.

        Uses BFS to find the shortest legal path.  Useful for CLI batch
        mode and tests where manually stepping through every state is
        impractical.
        """
        for state in path_to(self.state, target):
            self.transition_to(state)
        return self.state

    def get_legal_transitions(self) -> list[str]:
        """Return allowed next-state names (for the LLM to decide next action)."""
        return [s.value for s in sorted(TRANSITIONS.get(self.state, set()), key=str)]

    # ---- Internal guards ---------------------------------------------------

    def _require_state(self, allowed: set[DirectorState]) -> None:
        """Guard: raise StateError if self.state is not in *allowed*."""
        if self.state not in allowed:
            names = [s.value for s in sorted(allowed, key=str)]
            raise StateError(
                f"Operation requires state {names}, current state is "
                f"'{self.state.value}'. Legal next: {self.get_legal_transitions()}"
            )

    def save_project(self, path: str | Path, message: str = "") -> list[str]:
        """Validate, auto-version, and write Project to disk.

        Requires COMMIT state (STATE_MACHINE §3.7).
        Follows Architecture Principle 6 (validation blocks commit) and
        Principle 7 (immutable history).  Every save appends a HistoryEntry
        with auto-incremented version and ISO timestamp.

        Returns the validation issues list (empty if valid, ValueError if
        save is blocked by validation errors).
        """
        self._require_state({DirectorState.COMMIT})
        if not self.project:
            raise RuntimeError("No project loaded. Call load_project() or new_project() first.")

        # 1. Validate — fail fast per Principle 6
        issues = self.project.validate()
        if issues:
            raise ValueError(
                f"Project has {len(issues)} validation issue(s) — "
                "fix them before saving:\n  - " + "\n  - ".join(issues)
            )

        # 2. Auto-version
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Determine next version from history or metadata
        if self.project.history:
            last = self.project.history[-1]
            prev = last.version or self.project.metadata.version or "0.1.0"
        else:
            prev = self.project.metadata.version or "0.1.0"

        # Bump patch: 0.1.0 → 0.1.1, 1.2.3 → 1.2.4
        try:
            parts = prev.split(".")
            parts[-1] = str(int(parts[-1]) + 1)
            next_ver = ".".join(parts)
        except (ValueError, IndexError):
            next_ver = "0.1.1"

        self.project.metadata.version = next_ver
        self.project.metadata.updated_at = now

        # 3. Append history entry
        self.project.history.append(HistoryEntry(
            version=next_ver,
            timestamp=now,
            author="Director",
            notes=message or f"Saved project '{self.project.metadata.title}'",
        ))

        # 4. Write to disk
        from .loader import save_project_file
        save_project_file(self.project, path)

        return issues  # empty — we already validated above

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
            self._llm_client = client
            cache = CacheManager()
            self.resolver.set_cache(cache)
            self.resolver.register(LLMProvider(client=client, cache_manager=cache))
        except Exception:
            pass  # LLM init failure is non-fatal — local rules still work

    def _init_agents(self) -> None:
        """Lazy-init the agent registry after first use."""
        if self.agents:
            return
        from .agents import StoryAgent, CameraAgent, ContinuityAgent
        self.agents = {
            "story": StoryAgent(),
            "camera": CameraAgent(),
            "continuity": ContinuityAgent(),
        }

    def run_agent_cycle(
        self,
        target_agents: list[str] | None = None,
    ) -> dict[str, object]:
        """Dispatch specialist agents and collect their proposals.

        Maps to state machine stages:
            PLAN → StoryAgent
            DESIGN → CameraAgent
            VALIDATE → ContinuityAgent

        Agents work in KB mode by default. When self._llm_client is set,
        agent.propose() receives it for LLM-powered reasoning.

        Returns a dict with keys: proposals, warnings, stats, state.
        """
        self._init_agents()
        if not self.project:
            raise RuntimeError("No project loaded")

        # Determine which agents to run based on state
        state_agents: dict[DirectorState, list[str]] = {
            DirectorState.PLAN: ["story"],
            DirectorState.DESIGN: ["camera"],
            DirectorState.VALIDATE: ["continuity"],
        }
        selected = target_agents or state_agents.get(self.state, [])
        if not selected:
            return {
                "proposals": [],
                "warnings": [f"No agents for state '{self.state.value}'"],
                "stats": {},
                "state": self.state.value,
            }

        all_proposals: list[dict] = []
        all_warnings: list[str] = []
        all_stats: dict[str, dict] = {}

        for name in selected:
            agent = self.agents.get(name)
            if not agent:
                all_warnings.append(f"Agent '{name}' not registered")
                continue

            from .agents.base import AgentRequest
            req = AgentRequest(
                agent=name,
                project_slice=agent.read_project_slice(self.project),
                context={
                    "genre": " ".join(self.project.story.genre) if self.project.story.genre else "",
                    "premise": self.project.story.premise,
                    "emotion": getattr(self.intent, "narrative_intent", {}).get("premise", ""),
                    "cycle_id": self.ctx.cycle_id if self.ctx else "",
                },
            )
            result = agent.propose(req, llm_client=self._llm_client)
            for p in result.proposals:
                all_proposals.append({
                    "id": p.proposal_id,
                    "agent": p.agent,
                    "module": p.module,
                    "field": p.field,
                    "action": p.action,
                    "value": p.value,
                    "rationale": p.rationale,
                    "confidence": p.confidence,
                })
            all_warnings.extend(result.warnings)
            all_stats[name] = result.stats

        return {
            "proposals": all_proposals,
            "warnings": all_warnings,
            "stats": all_stats,
            "state": self.state.value,
        }
