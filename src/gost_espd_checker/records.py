"""The records of the contents of a document."""

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import takewhile
from typing import final

from docx.document import Document
from typing_extensions import override

from gost_espd_checker.lines import Lines
from gost_espd_checker.spot import Spot
from gost_espd_checker.unnumbered import Unnumbered


@final
@dataclass(frozen=True, slots=True)
class Records(Iterable[str]):
    """The run of lines right after the contents title, each with a page."""

    document: Document

    @override
    def __iter__(self) -> Iterator[str]:
        """Give the number and the name of every record, without its page."""
        lines = tuple(Lines(self.document))
        heading = int(
            Spot(
                tuple(str(Unnumbered(line.text)) for _, line in lines),
                r"содержание|оглавление",
            )
        )
        return (
            line.text.split("\t")[0].strip()
            for _, line in takewhile(
                lambda pair: re.search(r"\t\s*\d+\s*$", pair[1].text),
                lines[heading + 1 :] if heading >= 0 else (),
            )
        )
