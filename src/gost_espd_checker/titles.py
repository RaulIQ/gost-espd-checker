"""The titles of sections and subsections of a document."""

from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.oxml.ns import qn
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.headings import Headings
from gost_espd_checker.section_title import SectionTitle
from gost_espd_checker.subsection_title import SubsectionTitle
from gost_espd_checker.title import Title
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class Titles(Check):
    """Every title that the structure of the document reveals."""

    document: Document
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Check every section and subsection title of the body."""
        hyphenation = any(
            switch.get(qn("w:val")) not in {"0", "false", "off"}
            for switch in self.document.settings.element.xpath(
                "./w:autoHyphenation"
            )
        )
        return tuple(
            violation
            for paragraph, level in Headings(self.document).levels()
            if level
            for check in (
                (SectionTitle if level == 1 else SubsectionTitle)(
                    paragraph,
                    f"заголовок «{paragraph.text.strip()}»",
                    self.rules,
                ),
                Title(
                    paragraph,
                    f"заголовок «{paragraph.text.strip()}»",
                    self.rules,
                    hyphenation=hyphenation,
                ),
            )
            for violation in check.violations()
        )
