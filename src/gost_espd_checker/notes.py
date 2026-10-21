"""The notes of a document: «Примечание.» or numbered «Примечания:»."""

import re
from dataclasses import dataclass
from itertools import takewhile
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.body import Body
from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class Notes(Check):
    """Clause 2.7.1: one note takes a period, several a colon and numbers.

    A note is a paragraph that starts with the word, printed plain or
    with spaces between its letters; the numbered notes are the
    paragraphs right after it that start with a number.
    """

    _document: Document
    _rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report the sign after the word and the numbers of the notes."""
        texts = [
            paragraph.text.strip()
            for paragraph in Body(self._document)
            if paragraph.text.strip()
        ]
        return tuple(
            Violation(
                f"примечание «{text[:40]}»",
                self._rules.rule("ESPD-106-24"),
                message,
            )
            for index, text in enumerate(texts)
            for found in (
                re.match(
                    r"\u043f\s?\u0440\s?\u0438\s?\u043c\s?\u0435\s?\u0447\s?\u0430\s?\u043d\s?\u0438\s?([\u0435\u044f])(?!\w)\s*(\S?)",
                    text,
                    re.IGNORECASE,
                ),
            )
            if found
            for plural in (found[1].lower() == "я",)
            for numbers in (
                [
                    "".join(re.findall(r"^\d+[.)]?", line))
                    for line in takewhile(
                        lambda line: bool(re.match(r"\d", line)),
                        texts[index + 1 :],
                    )
                ],
            )
            for message, broken in (
                (
                    f"после слова «Примечание» стоит «{found[2]}» вместо точки",
                    not plural and found[2] not in {".", ""},
                ),
                (
                    "после слова «Примечание» нет точки",
                    not plural and not found[2],
                ),
                (
                    (
                        f"после слова «Примечания» стоит «{found[2]}» вместо"
                        " двоеточия"
                    ),
                    plural and found[2] not in {":", ""},
                ),
                (
                    "после слова «Примечания» нет двоеточия",
                    plural and not found[2],
                ),
                ("примечания не пронумерованы", plural and not numbers),
                *(
                    (
                        f"номер примечания «{number}» вместо «{position}.»",
                        number != f"{position}.",
                    )
                    for position, number in enumerate(numbers, 1)
                    if plural
                ),
            )
            if broken
        )
