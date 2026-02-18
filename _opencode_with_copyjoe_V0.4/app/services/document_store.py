from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class StoredDocument:
    document_id: str
    file_name: str
    extension: str
    source_path: Path
    converted_path: Path
    converted_text: str
    created_at: datetime


class DocumentStore:
    def __init__(self) -> None:
        self._items: dict[str, StoredDocument] = {}

    def add(self, item: StoredDocument) -> None:
        self._items[item.document_id] = item

    def get(self, document_id: str) -> StoredDocument | None:
        return self._items.get(document_id)

    def list_by_ids(self, document_ids: list[str]) -> list[StoredDocument]:
        return [self._items[doc_id] for doc_id in document_ids if doc_id in self._items]

    def clear(self, remove_files: bool = False) -> int:
        items = list(self._items.values())
        if remove_files:
            for item in items:
                try:
                    if item.source_path.exists():
                        item.source_path.unlink()
                except Exception:
                    pass
                try:
                    if item.converted_path.exists():
                        item.converted_path.unlink()
                except Exception:
                    pass

        self._items.clear()
        return len(items)
