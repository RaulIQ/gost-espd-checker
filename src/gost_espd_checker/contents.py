"""The contents of a document: its title, its page and its entries."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.printout import Printout
from gost_espd_checker.violation import Violation


def _lines(document: Document) -> tuple[tuple[int, Paragraph], ...]:
    return tuple(
        (number, line)
        for number, page in enumerate(Printout(document).pages())
        for line in page
        if line.text.strip()
    )


def _bare(text: str) -> str:
    return re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", text.strip())


def _find(lines: tuple[tuple[int, Paragraph], ...], word: str) -> int:
    return next(
        (
            position
            for position, (_, line) in enumerate(lines)
            if re.fullmatch(word, _bare(line.text), re.IGNORECASE)
        ),
        -1,
    )


@final
@dataclass(frozen=True, slots=True)
class Contents(Check):
    """Clause 2.1.4: contents on its own page, after the annotation."""

    document: Document
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report the title, the page and the entries of the contents."""
        lines = _lines(self.document)
        heading = _find(lines, r"содержание|оглавление")
        if heading < 0:
            return ()
        page, title = lines[heading]
        word = _bare(title.text)
        return tuple(
            self._violation(text)
            for text, broken in (
                (
                    f"заголовок «{word}» вместо «СОДЕРЖАНИЕ»",
                    word != "СОДЕРЖАНИЕ",
                ),
                (
                    "содержание пронумеровано как раздел",
                    word != title.text.strip(),
                ),
                (
                    f"перед заголовком «{word}» на той же странице есть текст",
                    heading > 0 and lines[heading - 1][0] == page,
                ),
                (
                    "содержание стоит перед аннотацией",
                    _find(lines, r"аннотация") > heading,
                ),
                *(
                    (
                        f"в содержание включена строка «{name}»",
                        bool(
                            re.fullmatch(
                                r"аннотация|содержание",
                                _bare(name),
                                re.IGNORECASE,
                            )
                        ),
                    )
                    for _, line in lines[heading + 1 :]
                    if re.search(r"\t\s*\d+\s*$", line.text)
                    for name in (line.text.split("\t")[0].strip(),)
                ),
            )
            if broken
        )

    def _violation(self, text: str) -> Violation:
        return Violation("содержание", self.rules.rule("ESPD-106-16"), text)
