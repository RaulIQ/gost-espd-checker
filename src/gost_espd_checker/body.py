"""The paragraphs of a document after its title page."""

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
class Body(Iterable[Paragraph]):
    """Every paragraph on the pages that follow the title page."""

    document: Document

    @override
    def __iter__(self) -> Iterator[Paragraph]:
        """Skip the approval sheet and the title page."""
        return (
            paragraph
            for page in Printout(self.document).pages()[
                int(Front(self.document)) + 1 :
            ]
            for paragraph in page
        )
