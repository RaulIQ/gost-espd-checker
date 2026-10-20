"""Page breaks typed inside a paragraph, before or after its text."""

from dataclasses import dataclass
from typing import final

from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.flow import Flow


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
