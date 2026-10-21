"""The level of a title: a section, a subsection or no title at all."""

import re
from dataclasses import dataclass
from typing import SupportsInt, final

from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.lettering import Lettering
from gost_espd_checker.lineage import Lineage
from gost_espd_checker.placement import Placement


@final
@dataclass(frozen=True, slots=True)
class Level(SupportsInt):
    """A paragraph leveled by its outline, or by a bold number without one."""

    _paragraph: Paragraph
    _styled: bool

    @override
    def __int__(self) -> int:
        """Give 1 for a section, 2 for a subsection, 0 for anything else."""
        text = self._paragraph.text.strip()
        outline = Placement(Lineage(self._paragraph)).outline()
        numbered = (
            1
            if re.match(r"\d+\.\s+\S", text)
            else 2
            if re.match(r"\d+\.\d+\.?\s+\S", text)
            else 0
        )
        return (
            0
            if not re.search(r"\w", text)
            else outline + 1
            if self._styled and outline in {0, 1}
            else 0
            if self._styled
            else numbered
            if Lettering(Lineage(self._paragraph)).bold()
            else 0
        )
