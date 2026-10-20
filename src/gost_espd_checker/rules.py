"""The rules of the standards, kept in the table ``rules.yaml``."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, final

import yaml
from typing_extensions import override


class Rule(Protocol):
    """One requirement of a standard, with its clause and severity."""

    def line(self, place: str, message: str) -> str:
        """Render one violation of the rule."""
        ...


class Catalog(Protocol):
    """The rules known to the checks, found by their ids."""

    def rule(self, key: str) -> Rule:
        """Find the rule by its id."""
        ...


@final
@dataclass(frozen=True, slots=True)
class Row(Rule):
    """One row of the table of rules."""

    fields: dict[str, object]

    @override
    def line(self, place: str, message: str) -> str:
        """Render as ``place: severity id: message (clause)``."""
        head = f"{self.fields['severity']} {self.fields['id']}"
        return f"{place}: {head}: {message} ({self.fields['clause']})"


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
