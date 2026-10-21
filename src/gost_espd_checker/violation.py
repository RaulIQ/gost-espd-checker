"""A single place where a document breaks a rule of the standards."""

from dataclasses import dataclass
from typing import final

from typing_extensions import override

from gost_espd_checker.rule import Rule


@final
@dataclass(frozen=True, slots=True)
class Violation:
    """What is wrong, where in the document, and which rule says so."""

    _place: str
    _rule: Rule
    _message: str

    @override
    def __str__(self) -> str:
        """Render through the rule, which knows its clause and severity."""
        return self._rule.line(self._place, self._message)
