"""The tables of a document with their captions."""

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import final

from docx.document import Document
from docx.table import Table
from typing_extensions import override

from gost_espd_checker.body import Body


@final
@dataclass(frozen=True, slots=True)
class Tables(Iterable[tuple[Table, str, str]]):
    """Tables of the text, each with its «Таблица N» line and appendix.

    The line is empty when the paragraph right over the table is no
    caption; the appendix is its designation, empty in the main text.
    The sheet of changes keeps its own form and is left out, and so is a
    table right under a heading like «ПЕРЕЧЕНЬ СОКРАЩЕНИЙ», which is the
    list itself rather than a table of the text.
    """

    document: Document

    @override
    def __iter__(self) -> Iterator[tuple[Table, str, str]]:
        """Start a table at its first paragraph and look right over it."""
        paragraphs = tuple(Body(self.document))
        owners = tuple(
            tuple(
                paragraph.paragraph_format.element.xpath(
                    "ancestor::w:tbl[last()]"
                )
            )
            for paragraph in paragraphs
        )
        for index in (
            index
            for index in range(len(paragraphs))
            if owners[index]
            and (not index or owners[index - 1] != owners[index])
        ):
            above = [
                paragraphs[earlier].text.strip()
                for earlier in range(index)
                if not owners[earlier] and paragraphs[earlier].text.strip()
            ]
            near = [
                paragraphs[earlier].text.strip()
                for earlier in range(
                    max(
                        (
                            earlier + 1
                            for earlier in range(index)
                            if owners[earlier]
                        ),
                        default=0,
                    ),
                    index,
                )
                if paragraphs[earlier].text.strip()
            ][-1:]
            if (
                any(
                    re.fullmatch(
                        r"лист регистрации изменений", text, re.IGNORECASE
                    )
                    for text in above
                )
                or "лист регистрации изменений"
                in "".join(owners[index][0].itertext()).lower()
                or any(
                    re.fullmatch(r"перечень\s[^.]+", text, re.IGNORECASE)
                    for text in near
                )
            ):
                continue
            yield (
                Table(owners[index][0], self.document),
                "".join(
                    text
                    for text in near
                    if re.match(r"таблица\s+[\w.]*\d", text, re.IGNORECASE)
                ),
                next(
                    (
                        found[1] or ""
                        for text in reversed(above)
                        for found in (
                            re.fullmatch(
                                r"приложение(?:\s+(\S+))?", text, re.IGNORECASE
                            ),
                        )
                        if found
                    ),
                    "",
                ),
            )
