"""The lines of a document with text, each with the number of its page."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.printout import Printout


@final
@dataclass(frozen=True, slots=True)
class Lines(Iterable[tuple[int, Paragraph]]):
    """Paragraphs with text, paired with the pages they are printed on."""

    document: Document

    @override
    def __iter__(self) -> Iterator[tuple[int, Paragraph]]:
        """Pair each line with text with its page, counted from zero."""
        return (
            (number, line)
            for number, page in enumerate(Printout(self.document).pages())
            for line in page
            if line.text.strip()
        )
