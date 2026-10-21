"""The letters of a paragraph as Word shows them, after styles apply."""

from dataclasses import dataclass
from typing import final

from typing_extensions import override

from gost_espd_checker.ancestry import Ancestry
from gost_espd_checker.typeface import Typeface


@final
@dataclass(frozen=True, slots=True)
class Lettering(Typeface):
    """The runs of a paragraph, whose fonts fall back on their styles."""

    _lineage: Ancestry

    @override
    def capitals(self) -> bool:
        """Check that every run with text is shown in capitals."""
        found = self._lineage.flags(lambda font: font.all_caps)
        return bool(found) and all(found)

    @override
    def bold(self) -> bool:
        """Check that every run with text is bold."""
        found = self._lineage.flags(lambda font: font.bold)
        return bool(found) and all(found)
