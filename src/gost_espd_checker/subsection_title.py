"""The title of a subsection: indented, lowercase after a capital."""

from dataclasses import dataclass
from typing import final

from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.check import Check
from gost_espd_checker.effective import Effective
from gost_espd_checker.rules import Catalog
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class SubsectionTitle(Check):
    """Clause 2.1.7: a subsection title starts indented, with one capital."""

    paragraph: Paragraph
    place: str
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report a missing indent and letters other than a first capital."""
        formatting = Effective(self.paragraph)
        letters = [char for char in self.paragraph.text if char.isalpha()]
        return tuple(
            Violation(self.place, self.rules.rule("ESPD-106-10"), message)
            for message, broken in (
                (
                    "заголовок подраздела записан без абзацного отступа",
                    formatting.indent() <= 0,
                ),
                (
                    (
                        "заголовок подраздела записан не строчными буквами,"
                        " кроме первой прописной"
                    ),
                    not letters
                    or letters[0].islower()
                    or not any(letter.islower() for letter in letters)
                    or formatting.capitals(),
                ),
            )
            if broken
        )
