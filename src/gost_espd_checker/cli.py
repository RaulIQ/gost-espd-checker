"""The command line: ``gost-espd-checker документ.docx``."""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, TextIO, final

import docx
from typing_extensions import override

from gost_espd_checker.layout import Layout


class Program(Protocol):
    """Something run from the command line that ends with an exit code."""

    def run(self) -> int:
        """Do the work and return the exit code."""
        ...


@final
@dataclass(frozen=True, slots=True)
class Cli(Program):
    """Checks one ``.docx`` file and prints a violation per line."""

    path: Path
    out: TextIO

    @override
    def run(self) -> int:
        """Print the violations; exit with one when there are any."""
        found = Layout(docx.Document(str(self.path))).violations()
        self.out.writelines(f"{violation}\n" for violation in found)
        return 1 if found else 0


def main() -> None:
    """Entry point of the ``gost-espd-checker`` command."""
    parser = argparse.ArgumentParser(
        prog="gost-espd-checker",
        description="Проверяет документ .docx на соответствие ГОСТ ЕСПД",
    )
    parser.add_argument("document", type=Path, help="файл .docx")
    sys.exit(Cli(parser.parse_args().document, sys.stdout).run())
