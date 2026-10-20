"""The page breaks and pieces of text of a paragraph."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import final

from docx.text.paragraph import Paragraph
from typing_extensions import override


@final
@dataclass(frozen=True, slots=True)
class Marks(Iterable[bool]):
    """True for every page break and False for every piece of text."""

    paragraph: Paragraph

    @override
    def __iter__(self) -> Iterator[bool]:
        """Go through the paragraph, skipping pieces without text."""
        return (
            mark.tag.endswith("}br")
            for mark in self.paragraph.paragraph_format.element.xpath(
                './/w:t | .//w:br[@w:type="page"]'
            )
            if mark.tag.endswith("}br") or (mark.text or "").strip()
        )
