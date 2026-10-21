"""The captions over the tables of a document."""

import re
from dataclasses import dataclass
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.check import Check
from gost_espd_checker.label import Label
from gost_espd_checker.tables import Tables
from gost_espd_checker.violation import Violation


@final
@dataclass(frozen=True, slots=True)
class TableCaptions(Check):
    """GOST 1.5-2001, clause 4.5.2: «Таблица N» and a name over a table.

    GOST 19.106-78, clause 2.6.2, adds that the name is in small letters.
    """

    _document: Document
    _rules: Catalog

    @override
    def violations(self) -> tuple[Violation, ...]:
        """Report missing captions, wrong dashes, periods and capitals."""
        return tuple(
            Violation(
                str(Label("таблица", caption, position + 1)),
                self._rules.rule(key),
                text,
            )
            for position, (_, caption, _) in enumerate(Tables(self._document))
            for rest in (
                re.sub(
                    r"^таблица\s+[\w.]*\d", "", caption, flags=re.IGNORECASE
                ),
            )
            for name in (re.sub(r"^\s*[\u2014\u2013.:-]?\s*", "", rest),)
            for letters in ("".join(re.findall(r"[^\W\d_]", name)),)
            for key, text, broken in (
                (
                    "ESPD-015-01",
                    "над таблицей нет надписи «Таблица» и номера",
                    not caption,
                ),
                (
                    "ESPD-015-01",
                    "наименование отделено от номера не тире",
                    bool(rest.strip())
                    and not re.match(r"\s+[\u2014\u2013]\s+\S", rest),
                ),
                (
                    "ESPD-015-01",
                    "в конце наименования таблицы стоит точка",
                    name.endswith("."),
                ),
                (
                    "ESPD-015-01",
                    "первая буква наименования таблицы строчная",
                    name[:1].islower(),
                ),
                (
                    "ESPD-106-23",
                    "наименование таблицы записано прописными буквами",
                    len(letters) > 1 and letters.isupper(),
                ),
            )
            if broken
        )
