"""One row of the table ``rules.yaml``."""

from dataclasses import dataclass
from typing import final

from typing_extensions import override

from gost_espd_checker.rule import Rule


@final
@dataclass(frozen=True, slots=True)
class Row(Rule):
    """One row of the table of rules."""

    _fields: dict[str, object]

    @override
    def line(self, place: str, message: str) -> str:
        """Render as ``place: severity id: message (clause)``."""
        head = f"{self._fields['severity']} {self._fields['id']}"
        return f"{place}: {head}: {message} ({self._fields['clause']})"
