from contextlib import contextmanager
from typing import Iterator


class LangfuseClient:
    def __init__(self) -> None:
        self.enabled = False

    @contextmanager
    def trace(self, _: str) -> Iterator[None]:
        yield
