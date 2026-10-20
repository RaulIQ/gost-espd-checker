"""The letters of a paragraph as Word shows them, after styles apply."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import final

from docx.text.font import Font
from typing_extensions import override

from gost_espd_checker.ancestry import Ancestry
from gost_espd_checker.typeface import Typeface


@final
@dataclass(frozen=True, slots=True)
class Lettering(Typeface):
    """The runs of a paragraph, whose fonts fall back on their styles."""

    lineage: Ancestry

    @override
    def capitals(self) -> bool:
        """Check that every run with text is shown in capitals."""
        return self._every(lambda font: font.all_caps)

    @override
    def bold(self) -> bool:
        """Check that every run with text is bold."""
        return self._every(lambda font: font.bold)

    def _every(self, pick: Callable[[Font], bool | None]) -> bool:
        runs = self.lineage.fonts()
        return bool(runs) and all(
            next(
                (
                    found
                    for found in (pick(font) for font in fonts)
                    if found is not None
                ),
                False,
            )
            for fonts in runs
        )
