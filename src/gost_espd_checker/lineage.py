"""A paragraph together with the styles it inherits from."""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TypeVar, final

from docx.oxml.xmlchemy import BaseOxmlElement
from docx.styles.style import CharacterStyle
from docx.text.font import Font
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.ancestry import Ancestry

_Style = TypeVar("_Style", bound=CharacterStyle)


def _chain(style: _Style | None) -> Iterator[_Style]:
    while style is not None:
        yield style
        style = style.base_style


@final
@dataclass(frozen=True, slots=True)
class Lineage(Ancestry):
    """A paragraph, its style and the bases of that style, in that order."""

    paragraph: Paragraph

    @override
    def owners(self) -> tuple[BaseOxmlElement, ...]:
        """Put the paragraph first, then its style and every base style."""
        return (
            self.paragraph.paragraph_format.element,
            *(style.element for style in _chain(self.paragraph.style)),
        )

    @override
    def fonts(self) -> tuple[tuple[Font, ...], ...]:
        """Put the run first, then its styles, then the paragraph styles."""
        return tuple(
            (
                run.font,
                *(style.font for style in _chain(run.style)),
                *(style.font for style in _chain(self.paragraph.style)),
            )
            for run in self.paragraph.runs
            if run.text.strip()
        )
