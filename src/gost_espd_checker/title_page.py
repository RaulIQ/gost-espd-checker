"""The title page of a document."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.printout import Printout


@final
@dataclass(frozen=True, slots=True)
class TitlePage(Iterable[Paragraph]):
    """The lines with text of the first page that is no approval sheet."""

    document: Document

    @override
    def __iter__(self) -> Iterator[Paragraph]:
        """Skip the approval sheet and the empty lines."""
        page = next(
            (
                page
                for page in Printout(self.document).pages()
                if not any(
                    "лист утверждения" in line.text.lower() for line in page
                )
            ),
            (),
        )
        return (line for line in page if line.text.strip())
