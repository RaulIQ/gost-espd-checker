"""A length of a document as people read it: in millimetres."""

from dataclasses import dataclass
from typing import final

from docx.shared import Length
from typing_extensions import override


@final
@dataclass(frozen=True, slots=True)
class Millimeters:
    """A length that may be missing from the document."""

    length: Length | None

    @override
    def __str__(self) -> str:
        """Render as ``25,4 мм``, or as unset when the length is missing."""
        if self.length is None:
            return "не задано"
        return f"{self.length.mm:.1f} мм".replace(".", ",")
