"""The kind of a structural element a paragraph starts."""

import re
from dataclasses import dataclass
from typing import final

from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.lineage import Lineage
from gost_espd_checker.placement import Placement


@final
@dataclass(frozen=True, slots=True)
class Kind:
    """A paragraph named a point, an enumeration, or nothing."""

    paragraph: Paragraph

    @override
    def __str__(self) -> str:
        """Name the element by its number, its dash or its Word list."""
        text = self.paragraph.text.strip()
        return (
            ""
            if not re.search(r"\w", text)
            else "пункт"
            if re.match(r"\d+(?:\.\d+)+\.\s+\S", text)
            else "перечисление"
            if re.match(r"(?:\d+[.)]|[-\u2013\u2014\u2022])\s+\S", text)
            or Placement(Lineage(self.paragraph)).listed()
            else ""
        )
