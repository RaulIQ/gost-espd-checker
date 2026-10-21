"""The page layout of a whole document, section by section."""

from dataclasses import dataclass
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.heading import Heading
from gost_espd_checker.margins import Margins
from gost_espd_checker.page_size import PageSize
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class Layout(Check):
    """The sheet, the margins and the header of every section."""

    _document: Document
    _rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Violations of every section, numbered from one."""
        return tuple(
            violation
            for number, section in enumerate(self._document.sections, start=1)
            for check in (
                PageSize(section, number, self._rules),
                Margins(section, number, self._rules),
                Heading(section, number, self._rules),
            )
            for violation in check.violations()
        )
