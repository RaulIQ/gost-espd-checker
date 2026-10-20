"""The rules a check can look up."""

from typing import Protocol

from gost_espd_checker.rule import Rule


class Catalog(Protocol):
    """The rules known to the checks, found by their ids."""

    def rule(self, key: str) -> Rule:
        """Find the rule by its id."""
        ...
