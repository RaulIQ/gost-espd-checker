"""The mentions of tables in the text of a document."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.body import Body
from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.tables import Tables
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class TableMentions(Check):
    """GOST 1.5-2001, clause 4.5.3: the text mentions every table by word."""

    document: Document
    rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report short words, missing tables and tables nobody mentions."""
        tables = [
            (caption, found[1])
            for _, caption, _ in Tables(self.document)
            for found in (
                re.match(r"таблица\s+([\w.]*\d)", caption, re.IGNORECASE),
            )
            if found
        ]
        mentions = [
            (paragraph.text.strip(), found[0], found[1], number)
            for paragraph in Body(self.document)
            if not paragraph.paragraph_format.element.xpath("ancestor::w:tbl")
            and not re.match(
                r"таблица\s+[\w.]*\d", paragraph.text.strip(), re.IGNORECASE
            )
            and not re.search(r"\t\s*\d+\s*$", paragraph.text)
            for found in re.finditer(
                r"(?<!\w)(табл\w*\.?)\s*([\w.]*\d(?:\s*(?:,|и|\u2014|\u2013|-)"
                r"\s*[\w.]*\d)*)",
                paragraph.text,
                re.IGNORECASE,
            )
            if "ГОСТ"
            not in paragraph.text[max(0, found.start() - 30) : found.start()]
            for piece in re.finditer(
                r"((?:\w+\.)*)(\d+)(?:\s*[\u2014\u2013-]\s*(\d+))?", found[2]
            )
            for number in (
                f"{piece[1]}{last}"
                for last in range(int(piece[2]), int(piece[3] or piece[2]) + 1)
            )
        ]
        return (
            *(
                Violation(
                    f"абзац «{text[:40]}»",
                    self.rules.rule("ESPD-015-02"),
                    message,
                )
                for text, mention, word, number in mentions
                for message, broken in (
                    (
                        f"ссылка «{mention}» вместо слова «таблица»",
                        not word.lower().startswith("таблиц")
                        and number
                        == next(
                            f"{piece[1]}{piece[2]}"
                            for piece in re.finditer(
                                r"((?:\w+\.)*)(\d+)", mention
                            )
                        ),
                    ),
                    (
                        f"ссылка на таблицу {number}, которой нет в документе",
                        number not in {known for _, known in tables},
                    ),
                )
                if broken
            ),
            *(
                Violation(
                    f"таблица «{caption}»",
                    self.rules.rule("ESPD-015-02"),
                    f"в тексте нет ссылки на таблицу {number}",
                )
                for caption, number in tables
                if number not in {mentioned for *_, mentioned in mentions}
            ),
        )
