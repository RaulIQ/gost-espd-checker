"""The title page of a document."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.front import Front
from gost_espd_checker.printout import Printout


@final
@dataclass(frozen=True, slots=True)
class TitlePage(Iterable[Paragraph]):
    """The lines with text of the first page that is no approval sheet."""

    _document: Document

    @override
    def __iter__(self) -> Iterator[Paragraph]:
        """Skip the approval sheet and the empty lines."""
        number = int(Front(self._document))
        return (
            line
            for page in Printout(self._document).pages()[number : number + 1]
            for line in page
            if line.text.strip()
        )
