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

    path: Path
    rules: Catalog
    out: TextIO

    @override
    def run(self) -> int:
        """Print the violations; exit with one when there are any."""
        document = docx.Document(str(self.path))
        found = (
            *Layout(document, self.rules).violations(),
            *Titles(document, self.rules).violations(),
            *Numbering(document, self.rules).violations(),
            *Sheets(document, self.rules).violations(),
            *Indents(document, self.rules).violations(),
            *Pagination(document, self.rules).violations(),
            *Endorsement(document, self.rules).violations(),
            *Contents(document, self.rules).violations(),
            *Lowercase(document, self.rules).violations(),
            *FigureNumbering(document, self.rules).violations(),
            *FigureMentions(document, self.rules).violations(),
            *FigureCaptions(document, self.rules).violations(),
            *TableCaptions(document, self.rules).violations(),
            *TableNumbering(document, self.rules).violations(),
            *TableMentions(document, self.rules).violations(),
            *TableHeads(document, self.rules).violations(),
            *TableOrdinals(document, self.rules).violations(),
        )
        self.out.writelines(f"{violation}\n" for violation in found)
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
