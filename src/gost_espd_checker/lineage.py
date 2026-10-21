"""A paragraph together with the styles it inherits from."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import final

from docx.oxml.xmlchemy import BaseOxmlElement
from docx.text.font import Font
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.ancestry import Ancestry
from gost_espd_checker.bases import Bases


@final
@dataclass(frozen=True, slots=True)
class Lineage(Ancestry):
    """A paragraph, its style and the bases of that style, in that order."""

    _paragraph: Paragraph

    @override
    def owners(self) -> tuple[BaseOxmlElement, ...]:
        """Put the paragraph first, then its style and every base style."""
        return (
            self._paragraph.paragraph_format.element,
            *(style.element for style in Bases(self._paragraph.style)),
        )

    @override
    def flags(self, pick: Callable[[Font], bool | None]) -> tuple[bool, ...]:
        """Take the run, then its styles, then the styles of the paragraph."""
        return tuple(
            next(
                (
                    found
                    for found in (
                        pick(run.font),
                        *(pick(style.font) for style in Bases(run.style)),
                        *(
                            pick(style.font)
                            for style in Bases(self._paragraph.style)
                        ),
                    )
                    if found is not None
                ),
                False,
            )
            for run in self._paragraph.runs
            if run.text.strip()
        )
