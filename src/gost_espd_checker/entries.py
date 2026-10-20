"""The numbered titles and points of a document."""

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.headings import Headings


@final
@dataclass(frozen=True, slots=True)
class Entries(Iterable[tuple[Paragraph, int, tuple[int, ...], bool]]):
    """Titles and points, each with its level, number and trailing dot."""

    document: Document

    @override
    def __iter__(
        self,
    ) -> Iterator[tuple[Paragraph, int, tuple[int, ...], bool]]:
        """Give every title, and every point with two or more parts."""
        for paragraph, level in Headings(self.document).levels():
            found = re.match(
                r"(\d+(?:\.\d+)*)(\.?)\s+\S", paragraph.text.strip()
            )
            number = (
                tuple(int(part) for part in found[1].split("."))
                if found
                else ()
            )
            dotted = bool(found and found[2])
            if level or (len(number) > 1 and dotted):
                yield paragraph, level, number, dotted
