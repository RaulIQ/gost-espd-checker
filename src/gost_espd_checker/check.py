"""One requirement of the standards, checked against a document."""

from typing import Protocol

from gost_espd_checker.violation import Violation


class Check(Protocol):
    """A source of violations."""

    def violations(self) -> tuple[Violation, ...]:
        """Everything that breaks the requirement."""
        ...
