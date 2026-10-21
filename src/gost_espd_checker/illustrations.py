"""The illustrations of a document with their numbers."""

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import accumulate, takewhile
from typing import final

from docx.document import Document
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.body import Body


@final
@dataclass(frozen=True, slots=True)
class Illustrations(Iterable[tuple[Paragraph, str, bool, int]]):
    """Pictures, charts and diagrams, each with its «Рис. N» line.

    Every item holds the paragraph of the illustration, the line with
    its number or an empty one, whether that line stands over the
    illustration, and the count of appendices before it.
    """

    _document: Document

    @override
    def __iter__(self) -> Iterator[tuple[Paragraph, str, bool, int]]:
        """Look for the number under the illustration, then right over it."""
        paragraphs = tuple(Body(self._document))
        drawn = tuple(
            bool(
                paragraph.paragraph_format.element.xpath(
                    ".//w:drawing//*[local-name()='graphicData']"
                    "[contains(@uri, '/picture') or contains(@uri, '/chart')"
                    " or contains(@uri, '/diagram')"
                    " or contains(@uri, 'wordprocessingCanvas')]"
                    " | .//w:pict[not(ancestor::*[local-name()='Fallback'])]"
                    "//*[local-name()='imagedata']"
                )
            )
            for paragraph in paragraphs
        )
        parts = tuple(
            accumulate(
                bool(
                    re.fullmatch(
                        r"приложение(?:\s+\d+)?",
                        paragraph.text.strip(),
                        re.IGNORECASE,
                    )
                )
                for paragraph in paragraphs
            )
        )
        taken: set[int] = set()
        for index in (index for index, mark in enumerate(drawn) if mark):
            found = [
                position
                for position in (
                    *[
                        position
                        for position in takewhile(
                            lambda position: not drawn[position],
                            range(index + 1, len(paragraphs)),
                        )
                        if paragraphs[position].text.strip()
                    ][:3],
                    *[
                        position
                        for position in takewhile(
                            lambda position: not drawn[position],
                            range(index - 1, -1, -1),
                        )
                        if paragraphs[position].text.strip()
                    ][:1],
                )
                if position not in taken
                and re.match(
                    r"рис\.?\s*\d+",
                    paragraphs[position].text.strip(),
                    re.IGNORECASE,
                )
            ][:1]
            taken.update(found)
            yield (
                paragraphs[index],
                "".join(
                    paragraphs[position].text.strip() for position in found
                ),
                any(position < index for position in found),
                parts[index],
            )
