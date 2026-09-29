from dataclasses import dataclass
from threading import RLock


@dataclass(frozen=True)
class Chunk:
    document_id: str
    chunk_id: str
    title: str
    source: str
    text: str


class InMemoryChunkStore:
    def __init__(self) -> None:
        self._chunks: list[Chunk] = []
        self._lock = RLock()

    def add(self, chunks: list[Chunk]) -> None:
        with self._lock:
            self._chunks.extend(chunks)

    def all(self) -> list[Chunk]:
        with self._lock:
            return list(self._chunks)

    def clear(self) -> None:
        with self._lock:
            self._chunks.clear()

    @property
    def document_count(self) -> int:
        with self._lock:
            return len({chunk.document_id for chunk in self._chunks})
