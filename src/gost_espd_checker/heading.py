"""The upper field of a page: forms 1 and 2 of GOST 19.106-78."""

from dataclasses import dataclass
from typing import final

from docx.section import Section
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class Heading(Check):
    """Clause 2.1.2: the page number above the designation of the document."""

    _section: Section
    _number: int
    _rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report a missing page number and a missing designation under it."""
        paragraphs = self._section.header.part.element.xpath(".//w:p")
        page = next(
            (
                index
                for index, paragraph in enumerate(paragraphs)
                if any(
                    instruction.split()[:1] == ["PAGE"]
                    for instruction in paragraph.xpath(
                        ".//w:instrText/text() | .//w:fldSimple/@w:instr"
                    )
                )
            ),
            len(paragraphs),
        )
        return tuple(
            Violation(
                f"раздел {self._number}",
                self._rules.rule(key),
                f"в верхнем колонтитуле нет {missing}",
            )
            for key, missing, absent in (
                ("ESPD-106-03", "номера страницы", page == len(paragraphs)),
                (
                    "ESPD-106-04",
                    "обозначения документа под номером страницы",
                    not any(
                        "".join(paragraph.xpath(".//w:t/text()")).strip()
                        for paragraph in paragraphs[page + 1 :]
                    ),
                ),
            )
            if absent
        )
