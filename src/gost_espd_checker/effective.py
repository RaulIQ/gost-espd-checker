"""The formatting of a paragraph as Word shows it, after styles apply."""

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Protocol, TypeVar, final

from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml.xmlchemy import BaseOxmlElement
from docx.shared import Length, Twips
from docx.styles.style import CharacterStyle
from docx.text.font import Font
from docx.text.paragraph import Paragraph
from typing_extensions import override


class Formatting(Protocol):
    """Properties of a paragraph that the standards care about."""

    def alignment(self) -> WD_PARAGRAPH_ALIGNMENT:
        """Tell how the paragraph is aligned."""
        ...

    def indent(self) -> Length:
        """Measure where the first line starts from the margin of the text."""
        ...

    def hyphenation(self) -> bool:
        """Whether Word may hyphenate the paragraph automatically."""
        ...

    def pagebreak(self) -> bool:
        """Whether Word starts the paragraph on a new page."""
        ...


class Position(Protocol):
    """Where a paragraph stands in the structure of a document."""

    def outline(self) -> int:
        """Tell the outline level: 0 for a section, 9 for body text."""
        ...

    def listed(self) -> bool:
        """Whether the paragraph is an item of a Word list."""
        ...


class Typeface(Protocol):
    """How the letters of a paragraph look."""

    def capitals(self) -> bool:
        """Whether every run of text is shown in capitals."""
        ...

    def bold(self) -> bool:
        """Whether every run of text is bold."""
        ...


_Style = TypeVar("_Style", bound=CharacterStyle)


def _chain(style: _Style | None) -> Iterator[_Style]:
    while style is not None:
        yield style
        style = style.base_style


def _owners(paragraph: Paragraph) -> tuple[BaseOxmlElement, ...]:
    return (
        paragraph.paragraph_format.element,
        *(style.element for style in _chain(paragraph.style)),
    )


def _every(paragraph: Paragraph, pick: Callable[[Font], bool | None]) -> bool:
    runs = [run for run in paragraph.runs if run.text.strip()]
    return bool(runs) and all(
        next(
            (
                found
                for found in (
                    pick(run.font),
                    *(pick(style.font) for style in _chain(run.style)),
                    *(pick(style.font) for style in _chain(paragraph.style)),
                )
                if found is not None
            ),
            False,
        )
        for run in runs
    )


@final
@dataclass(frozen=True, slots=True)
class Effective(Formatting):
    """A paragraph whose properties fall back on its style and its bases."""

    paragraph: Paragraph

    @override
    def alignment(self) -> WD_PARAGRAPH_ALIGNMENT:
        """Take the first alignment set; Word aligns left without one."""
        found = [
            value
            for owner in _owners(self.paragraph)
            for value in owner.xpath("./w:pPr/w:jc/@w:val")
        ]
        return WD_PARAGRAPH_ALIGNMENT.from_xml(
            {"start": "left", "end": "right"}.get(found[0], found[0])
            if found
            else "left"
        )

    @override
    def indent(self) -> Length:
        """Add the first line or hanging indent to the left one, like Word."""
        marks = [
            mark
            for owner in _owners(self.paragraph)
            for mark in owner.xpath("./w:pPr/w:ind")
        ]
        return Twips(
            next(
                (
                    int(value)
                    for mark in marks
                    for value in mark.xpath("@w:left | @w:start")[:1]
                ),
                0,
            )
            + next(
                (
                    -int(mark.get(qn("w:hanging")))
                    if mark.get(qn("w:hanging")) is not None
                    else int(mark.get(qn("w:firstLine")))
                    for mark in marks
                    if mark.get(qn("w:hanging")) is not None
                    or mark.get(qn("w:firstLine")) is not None
                ),
                0,
            )
        )

    @override
    def hyphenation(self) -> bool:
        """Allow hyphenation unless the paragraph or a style suppresses it."""
        found = [
            switch
            for owner in _owners(self.paragraph)
            for switch in owner.xpath("./w:pPr/w:suppressAutoHyphens")
        ]
        return not found or found[0].get(qn("w:val")) in {"0", "false", "off"}

    @override
    def pagebreak(self) -> bool:
        """Take the first page break before set; none without one."""
        return next(
            (
                found
                for found in (
                    self.paragraph.paragraph_format.page_break_before,
                    *(
                        style.paragraph_format.page_break_before
                        for style in _chain(self.paragraph.style)
                    ),
                )
                if found is not None
            ),
            False,
        )


@final
@dataclass(frozen=True, slots=True)
class Placement(Position):
    """A paragraph whose place in the structure falls back on its styles."""

    paragraph: Paragraph

    @override
    def outline(self) -> int:
        """Take the first outline level set; body text without one."""
        found = [
            level
            for owner in _owners(self.paragraph)
            for level in owner.xpath("./w:pPr/w:outlineLvl/@w:val")
        ]
        return int(found[0]) if found else 9

    @override
    def listed(self) -> bool:
        """Check the first list number set; zero takes the list away."""
        found = [
            number
            for owner in _owners(self.paragraph)
            for number in owner.xpath("./w:pPr/w:numPr/w:numId/@w:val")
        ]
        return bool(found) and found[0] != "0"


@final
@dataclass(frozen=True, slots=True)
class Lettering(Typeface):
    """The runs of a paragraph, whose fonts fall back on their styles."""

    paragraph: Paragraph

    @override
    def capitals(self) -> bool:
        """Check that every run with text is shown in capitals."""
        return _every(self.paragraph, lambda font: font.all_caps)

    @override
    def bold(self) -> bool:
        """Check that every run with text is bold."""
        return _every(self.paragraph, lambda font: font.bold)
