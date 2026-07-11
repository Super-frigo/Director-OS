"""Load library entries from YAML files."""

from ..models.library_entry import LibraryEntry


class LibraryLoader:
    """Loads and indexes library entries by category."""

    def __init__(self):
        self._entries: list[LibraryEntry] = []
        self._by_category: dict[str, list[LibraryEntry]] = {}

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
