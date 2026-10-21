"""The place of the title page among the pages of a document."""

from dataclasses import dataclass
from typing import SupportsInt, final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.printout import Printout


@final
@dataclass(frozen=True, slots=True)
class Front(SupportsInt):
    """The first page that is no approval sheet."""

    _document: Document

    @override
    def __int__(self) -> int:
        """Give the index of the title page, or the count of pages."""
        pages = Printout(self._document).pages()
        return next(
            (
                number
                for number, page in enumerate(pages)
                if not any(
                    "лист утверждения" in line.text.lower() for line in page
                )
            ),
            len(pages),
        )
