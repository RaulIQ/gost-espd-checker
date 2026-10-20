"""The place of a paragraph in the structure, after styles apply."""

from dataclasses import dataclass
from typing import final

from typing_extensions import override

from gost_espd_checker.ancestry import Ancestry
from gost_espd_checker.position import Position


@final
@dataclass(frozen=True, slots=True)
class Placement(Position):
    """A paragraph whose place in the structure falls back on its styles."""

    lineage: Ancestry

    @override
    def outline(self) -> int:
        """Take the first outline level set; body text without one."""
        found = [
            level
            for owner in self.lineage.owners()
            for level in owner.xpath("./w:pPr/w:outlineLvl/@w:val")
        ]
        return int(found[0]) if found else 9

    @override
    def listed(self) -> bool:
        """Check the first list number set; zero takes the list away."""
        found = [
            number
            for owner in self.lineage.owners()
            for number in owner.xpath("./w:pPr/w:numPr/w:numId/@w:val")
        ]
        return bool(found) and found[0] != "0"
