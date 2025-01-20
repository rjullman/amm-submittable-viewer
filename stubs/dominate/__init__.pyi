from types import TracebackType
from typing import ContextManager

class Document:
    head: ContextManager[None]

    def __enter__(self) -> None: ...
    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool: ...

def document(title: str | None = None) -> Document: ...
