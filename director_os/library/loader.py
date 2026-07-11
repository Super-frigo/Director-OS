"""Load library entries from YAML files."""

from pathlib import Path

import yaml

from ..models.library_entry import LibraryEntry


class LibraryLoader:
    """Loads and indexes library entries by category."""

    def __init__(self):
        self._entries: list[LibraryEntry] = []
        self._by_category: dict[str, list[LibraryEntry]] = {}

    def load_all(self, libraries_dir: str | Path = "") -> None:
        """Auto-discover and load all YAML library entries from a directory tree."""
        path = Path(libraries_dir) if libraries_dir else Path(__file__).resolve().parent.parent.parent / "libraries"
        if not path.exists():
            return
        entries: list[LibraryEntry] = []
        for yaml_file in sorted(path.rglob("*.yaml")):
            if yaml_file.stem.startswith("REF_"):
                continue
            try:
                data = yaml.safe_load(yaml_file.read_text(encoding="utf-8-sig"))
                if not isinstance(data, dict):
                    continue
                lib_data = data.get("library", data)
                if not isinstance(lib_data, dict) or not lib_data.get("metadata", {}).get("id"):
                    continue
                entry = LibraryEntry(
                    metadata=lib_data.get("metadata", {}),
                    category=lib_data.get("category", ""),
                    knowledge=lib_data.get("knowledge", {}),
                    applicability=lib_data.get("applicability", {}),
                    engine_guidance=lib_data.get("engine_guidance", {}),
                    relationships=lib_data.get("relationships", {}),
                    examples=lib_data.get("examples", {}),
                    references=lib_data.get("references", {}),
                    version=lib_data.get("version", "1.0"),
                )
                entries.append(entry)
            except Exception:
                continue
        self.load(entries)

    def load(self, entries: list[LibraryEntry]) -> None:
        self._entries = entries
        self._by_category.clear()
        for e in entries:
            self._by_category.setdefault(e.category, []).append(e)

    def query(self, category: str = "", emotion: str = "", genre: str = "") -> list[LibraryEntry]:
        results: list[LibraryEntry] = []
        pool = self._by_category.get(category, self._entries) if category else self._entries
        for entry in pool:
            app = entry.applicability
            if emotion and emotion not in app.get("emotions", []):
                continue
            if genre and genre not in app.get("genres", []):
                continue
            results.append(entry)
        return results
