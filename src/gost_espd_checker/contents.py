"""The contents of a document: its title, its page and its entries."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.lines import Lines
from gost_espd_checker.records import Records
from gost_espd_checker.spot import Spot
from gost_espd_checker.unnumbered import Unnumbered
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class Contents(Check):
    """Clause 2.1.4: contents on its own page, after the annotation."""

    document: Document
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report the title, the page and the entries of the contents."""
        lines = tuple(Lines(self.document))
        names = tuple(str(Unnumbered(line.text)) for _, line in lines)
        heading = int(Spot(names, r"содержание|оглавление"))
        if heading < 0:
            return ()
        page, title = lines[heading]
        word = names[heading]
        return tuple(
            Violation("содержание", self.rules.rule("ESPD-106-16"), text)
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
                    int(Spot(names, r"аннотация")) > heading,
                ),
                *(
                    (
                        f"в содержание включена строка «{name}»",
                        bool(
                            re.fullmatch(
                                r"аннотация|содержание",
                                str(Unnumbered(name)),
                                re.IGNORECASE,
                            )
                        ),
                    )
                    for name in Records(self.document)
                ),
            )
            if broken
        )
