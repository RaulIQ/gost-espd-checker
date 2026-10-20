"""A title or an entry of contents without its leading number."""

import re
from dataclasses import dataclass
from typing import final

from typing_extensions import override


@final
@dataclass(frozen=True, slots=True)
class Unnumbered:
    """The text of a line after its number, like «1.2.» or «3.»."""

    text: str

    @override
    def __str__(self) -> str:
        """Drop the number and the spaces around the text."""
        return re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", self.text.strip())
