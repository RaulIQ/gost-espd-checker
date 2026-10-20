"""The rules of the standards, kept in the table ``rules.yaml``."""

from dataclasses import dataclass
from pathlib import Path
from typing import final

import yaml
from typing_extensions import override

from gost_espd_checker.catalog import Catalog
from gost_espd_checker.row import Row
from gost_espd_checker.rule import Rule


@final
@dataclass(frozen=True, slots=True)
class Rules(Catalog):
    """The table of rules in a YAML file."""

    path: Path

    @override
    def rule(self, key: str) -> Rule:
        """Find the row of the rule; fail when the table lacks it."""
        rows = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        found = [row for row in rows if row["id"] == key]
        if not found:
            message = f"Rule {key} is missing from {self.path}"
            raise KeyError(message)
        return Row(found[0])
