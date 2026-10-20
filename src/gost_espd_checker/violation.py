"""A single place where a document breaks a GOST requirement."""

from dataclasses import dataclass
from typing import final

from typing_extensions import override


@final
@dataclass(frozen=True, slots=True)
class Violation:
    """What is wrong, where in the document, and which clause says so."""

    place: str
    clause: str
    message: str

    @override
    def __str__(self) -> str:
        """Render as ``place: message (clause)``."""
        return f"{self.place}: {self.message} ({self.clause})"
