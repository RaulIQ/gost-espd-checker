"""The titles of sections and subsections of a document."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from typing_extensions import override

from gost_espd_checker.check import Check
from gost_espd_checker.effective import Effective, Lettering
from gost_espd_checker.rules import Catalog
from gost_espd_checker.section_title import SectionTitle
from gost_espd_checker.subsection_title import SubsectionTitle
from gost_espd_checker.title import Title
from gost_espd_checker.violation import Violation


def _level(paragraph: Paragraph, *, styled: bool) -> int:
    text = paragraph.text.strip()
    outline = Effective(paragraph).outline()
    numbered = (
        1
        if re.match(r"\d+\.\s+\S", text)
        else 2
        if re.match(r"\d+\.\d+\.?\s+\S", text)
        else 0
    )
    return (
        0
        if re.search(r"\t\s*\d+$", paragraph.text) or not re.search(r"\w", text)
        else outline + 1
        if styled and outline in {0, 1}
        else 0
        if styled
        else numbered
        if Lettering(paragraph).bold()
        else 0
    )


@final
@dataclass(frozen=True, slots=True)
class Titles(Check):
    """Titles found by outline levels, or by bold numbered paragraphs."""

    document: Document
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Check every section and subsection title of the body."""
        styled = any(
            Effective(paragraph).outline() in range(9)
            for paragraph in self.document.paragraphs
        )
        hyphenation = any(
            switch.get(qn("w:val")) not in {"0", "false", "off"}
            for switch in self.document.settings.element.xpath(
                "./w:autoHyphenation"
            )
        )
        return tuple(
            violation
            for paragraph in self.document.paragraphs
            if _level(paragraph, styled=styled)
            for check in (
                (
                    SectionTitle
                    if _level(paragraph, styled=styled) == 1
                    else SubsectionTitle
                )(
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
