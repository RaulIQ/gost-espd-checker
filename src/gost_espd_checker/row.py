"""One row of the table ``rules.yaml``."""

from dataclasses import dataclass
from typing import final

from typing_extensions import override

from gost_espd_checker.rule import Rule


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
