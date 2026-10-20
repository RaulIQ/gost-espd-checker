"""The page numbers of a document: one run through all its sections."""

from dataclasses import dataclass
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class Pagination(Check):
    """Clause 2.1.1: no section numbers its pages separately."""

    document: Document
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report every section but the first that sets a start page number."""
        return tuple(
            Violation(
                f"раздел {number}",
                self.rules.rule("ESPD-106-05"),
                f"нумерация страниц начинается заново от {start}",
            )
            for number, properties in enumerate(
                self.document.element.body.xpath(
                    "./w:p/w:pPr/w:sectPr | ./w:sectPr"
                ),
                start=1,
            )
            if number > 1
            for start in properties.xpath("./w:pgNumType/@w:start")
        )
