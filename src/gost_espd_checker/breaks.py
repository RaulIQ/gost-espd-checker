"""Page breaks typed inside a paragraph, before or after its text."""

from dataclasses import dataclass
from typing import Protocol, final

from docx.text.paragraph import Paragraph
from typing_extensions import override


class Flow(Protocol):
    """Where a paragraph sits against the pages of a document."""

    def opens(self) -> bool:
        """Whether a page break comes before any text of the paragraph."""
        ...

    def closes(self) -> bool:
        """Whether a page break comes after all text of the paragraph."""
        ...


@final
@dataclass(frozen=True, slots=True)
class Breaks(Flow):
    """The page breaks and pieces of text of a paragraph, in their order."""

    paragraph: Paragraph

    @override
    def opens(self) -> bool:
        """Check that the first mark is a page break."""
        return self._marks()[:1] == [True]

    @override
    def closes(self) -> bool:
        """Check that the last mark is a page break."""
        return self._marks()[-1:] == [True]

    def _marks(self) -> list[bool]:
        return [
            mark.tag.endswith("}br")
            for mark in self.paragraph.paragraph_format.element.xpath(
                './/w:t | .//w:br[@w:type="page"]'
            )
            if mark.tag.endswith("}br") or (mark.text or "").strip()
        ]
