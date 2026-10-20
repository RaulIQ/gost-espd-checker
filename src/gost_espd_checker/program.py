"""Something run from the command line."""

from typing import Protocol


class Program(Protocol):
    """Something run from the command line that ends with an exit code."""

    def run(self) -> int:
        """Do the work and return the exit code."""
        ...
