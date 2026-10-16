import json
from pathlib import Path


class HistoryService:
    def __init__(self, storage_path: str | None = None):
        project_root = Path(__file__).resolve().parents[2]
        self.storage_path = Path(storage_path) if storage_path else project_root / 'backend' / 'history.json'
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text('[]', encoding='utf-8')

    def add_entry(self, entry: dict) -> dict:
        history = self._read()
        history.append(entry)
        self.storage_path.write_text(json.dumps(history, indent=2), encoding='utf-8')
        return entry

    def get_history(self) -> list[dict]:
        return self._read()

    def _read(self) -> list[dict]:
        try:
            with self.storage_path.open('r', encoding='utf-8') as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    return data
        except (json.JSONDecodeError, OSError):
            pass
        self.storage_path.write_text('[]', encoding='utf-8')
        return []
