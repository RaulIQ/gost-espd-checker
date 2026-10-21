"""The mentions of illustrations in the text of a document."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.body import Body
from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.illustrations import Illustrations
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class FigureMentions(Check):
    """Clause 2.3.1: mentions read «рис. 12», repeated ones «см. рис. 12»."""

    document: Document
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report other words, missing figures and repeats without «см.»."""
        numbers = {
            found[1]
            for _, caption, _, _ in Illustrations(self.document)
            for found in (re.match(r"рис\.?\s*(\d+)", caption, re.IGNORECASE),)
            if found
        }
        mentions = [
            (paragraph.text.strip(), found)
            for paragraph in Body(self.document)
            if not re.match(
                r"рис\.?\s*\d+", paragraph.text.strip(), re.IGNORECASE
            )
            and not re.search(r"\t\s*\d+\s*$", paragraph.text)
            for found in re.finditer(
                r"(?<!\w)(см\.\s*)?(рис\w*\.?)\s*№?\s*(\d+)",
                paragraph.text,
                re.IGNORECASE,
            )
        ]
        return tuple(
            Violation(
                f"абзац «{text[:40]}»", self.rules.rule("ESPD-106-19"), message
            )
            for position, (text, found) in enumerate(mentions)
            for message, broken in (
                (
                    f"ссылка «{found[2]} {found[3]}» вместо «рис. {found[3]}»",
                    found[2].lower() != "рис.",
                ),
                (
                    f"ссылка на рис. {found[3]}, которого нет в документе",
                    found[3] not in numbers,
                ),
                (
                    f"повторная ссылка на рис. {found[3]} без «см.»",
                    not found[1]
                    and any(
                        earlier[3] == found[3]
                        for _, earlier in mentions[:position]
                    ),
                ),
            )
            if broken
        )
