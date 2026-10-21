"""The command line: ``gost-espd-checker документ.docx``."""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO, final

import docx
from typing_extensions import override

import gost_espd_checker
from gost_espd_checker.catalog import Catalog
from gost_espd_checker.contents import Contents
from gost_espd_checker.endorsement import Endorsement
from gost_espd_checker.figure_captions import FigureCaptions
from gost_espd_checker.figure_mentions import FigureMentions
from gost_espd_checker.figure_numbering import FigureNumbering
from gost_espd_checker.indents import Indents
from gost_espd_checker.layout import Layout
from gost_espd_checker.lowercase import Lowercase
from gost_espd_checker.notes import Notes
from gost_espd_checker.numbering import Numbering
from gost_espd_checker.pagination import Pagination
from gost_espd_checker.program import Program
from gost_espd_checker.rules import Rules
from gost_espd_checker.sheets import Sheets
from gost_espd_checker.table_captions import TableCaptions
from gost_espd_checker.table_heads import TableHeads
from gost_espd_checker.table_mentions import TableMentions
from gost_espd_checker.table_numbering import TableNumbering
from gost_espd_checker.table_ordinals import TableOrdinals
from gost_espd_checker.titles import Titles


@final
@dataclass(frozen=True, slots=True)
class Cli(Program):
    """Checks one ``.docx`` file and prints a violation per line."""

    _path: Path
    _rules: Catalog
    _out: TextIO

    @override
    def run(self) -> int:
        """Print the violations; exit with one when there are any."""
        document = docx.Document(str(self._path))
        found = (
            *Layout(document, self._rules).violations(),
            *Titles(document, self._rules).violations(),
            *Numbering(document, self._rules).violations(),
            *Sheets(document, self._rules).violations(),
            *Indents(document, self._rules).violations(),
            *Pagination(document, self._rules).violations(),
            *Endorsement(document, self._rules).violations(),
            *Contents(document, self._rules).violations(),
            *Lowercase(document, self._rules).violations(),
            *FigureNumbering(document, self._rules).violations(),
            *FigureMentions(document, self._rules).violations(),
            *FigureCaptions(document, self._rules).violations(),
            *Notes(document, self._rules).violations(),
            *TableCaptions(document, self._rules).violations(),
            *TableNumbering(document, self._rules).violations(),
            *TableMentions(document, self._rules).violations(),
            *TableHeads(document, self._rules).violations(),
            *TableOrdinals(document, self._rules).violations(),
        )
        self._out.writelines(f"{violation}\n" for violation in found)
        return 1 if found else 0


def main() -> None:
    """Entry point of the ``gost-espd-checker`` command."""
    parser = argparse.ArgumentParser(
        prog="gost-espd-checker",
        description="Проверяет документ .docx на соответствие ГОСТ ЕСПД",
    )
    parser.add_argument("document", type=Path, help="файл .docx")
    sys.exit(
        Cli(
            parser.parse_args().document,
            Rules(Path(gost_espd_checker.__file__).with_name("rules.yaml")),
            sys.stdout,
        ).run()
    )
