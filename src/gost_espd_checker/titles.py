"""The titles of sections and subsections of a document."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.check import Check
from gost_espd_checker.rules import Catalog
from gost_espd_checker.section_title import SectionTitle
from gost_espd_checker.subsection_title import SubsectionTitle
from gost_espd_checker.title import Title
from gost_espd_checker.violation import Violation


def _level(paragraph: Paragraph) -> int:
    text = paragraph.text.strip()
    name = paragraph.style.name if paragraph.style is not None else ""
    numbered = (
        1
        if re.match(r"\d+\.\s+\S", text)
        else 2
        if re.match(r"\d+\.\d+\.?\s+\S", text)
        else 0
    )
    styled = {"Heading 1": 1, "Heading 2": 2}.get(name, 0)
    contents = re.search(r"\t\s*\d+$", paragraph.text)
    return (
        0
        if contents or not text
        else styled
        if name.startswith("Heading ")
        else numbered
    )


@final
@dataclass(frozen=True, slots=True)
class Titles(Check):
    """Titles found by the styles of Word or by the numbers in their text."""

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
            for paragraph in self.document.paragraphs
            if _level(paragraph)
            for check in (
                (SectionTitle if _level(paragraph) == 1 else SubsectionTitle)(
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
