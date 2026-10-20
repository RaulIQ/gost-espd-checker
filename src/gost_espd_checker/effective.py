"""The formatting of a paragraph as Word shows it, after styles apply."""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol, TypeVar, final

from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.shared import Length, Twips
from docx.styles.style import CharacterStyle
from docx.text.paragraph import Paragraph
from typing_extensions import override


class Formatting(Protocol):
    """Properties of a paragraph that the standards care about."""

    def alignment(self) -> WD_PARAGRAPH_ALIGNMENT:
        """Tell how the paragraph is aligned."""
        ...

    def indent(self) -> Length:
        """Measure the indent of the first line."""
        ...

    def capitals(self) -> bool:
        """Whether every run of text is shown in capitals."""
        ...

    def hyphenation(self) -> bool:
        """Whether Word may hyphenate the paragraph automatically."""
        ...


_Style = TypeVar("_Style", bound=CharacterStyle)


def _chain(style: _Style | None) -> Iterator[_Style]:
    while style is not None:
        yield style
        style = style.base_style


@final
@dataclass(frozen=True, slots=True)
class Effective(Formatting):
    """A paragraph whose properties fall back on its style and its bases."""

    paragraph: Paragraph

    @override
    def alignment(self) -> WD_PARAGRAPH_ALIGNMENT:
        """Take the first alignment set; Word aligns left without one."""
        return next(
            (
                found
                for found in (
                    self.paragraph.paragraph_format.alignment,
                    *(
                        style.paragraph_format.alignment
                        for style in _chain(self.paragraph.style)
                    ),
                )
                if found is not None
            ),
            WD_PARAGRAPH_ALIGNMENT.LEFT,
        )

    @override
    def indent(self) -> Length:
        """Take the first indent of the first line set; zero without one."""
        return next(
            (
                found
                for found in (
                    self.paragraph.paragraph_format.first_line_indent,
                    *(
                        style.paragraph_format.first_line_indent
                        for style in _chain(self.paragraph.style)
                    ),
                )
                if found is not None
            ),
            Twips(0),
        )

    @override
    def capitals(self) -> bool:
        """Check that every run with text is shown in capitals."""
        runs = [run for run in self.paragraph.runs if run.text.strip()]
        return bool(runs) and all(
            next(
                (
                    found
                    for found in (
                        run.font.all_caps,
                        *(style.font.all_caps for style in _chain(run.style)),
                        *(
                            style.font.all_caps
                            for style in _chain(self.paragraph.style)
                        ),
                    )
                    if found is not None
                ),
                False,
            )
            for run in runs
        )

    @override
    def hyphenation(self) -> bool:
        """Allow hyphenation unless the paragraph or a style suppresses it."""
        found = [
            switch
            for owner in (
                self.paragraph.paragraph_format.element,
                *(style.element for style in _chain(self.paragraph.style)),
            )
            for switch in owner.xpath("./w:pPr/w:suppressAutoHyphens")
        ]
        return not found or found[0].get(qn("w:val")) in {"0", "false", "off"}
