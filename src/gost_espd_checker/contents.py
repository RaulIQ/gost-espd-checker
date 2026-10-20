"""The contents of a document: its title, its page and its entries."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.lines import Lines
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
        names = [str(Unnumbered(line.text)) for _, line in lines]
        heading = next(
            (
                position
                for position, name in enumerate(names)
                if re.fullmatch(r"содержание|оглавление", name, re.IGNORECASE)
            ),
            -1,
        )
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
                    next(
                        (
                            position
                            for position, name in enumerate(names)
                            if re.fullmatch(r"аннотация", name, re.IGNORECASE)
                        ),
                        -1,
                    )
                    > heading,
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
                    for _, line in lines[heading + 1 :]
                    if re.search(r"\t\s*\d+\s*$", line.text)
                    for name in (line.text.split("\t")[0].strip(),)
                ),
            )
            if broken
        )
