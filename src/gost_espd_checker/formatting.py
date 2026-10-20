"""The formatting of a paragraph that the standards care about."""

from typing import Protocol

from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Length


class Formatting(Protocol):
    """Properties of a paragraph that the standards care about."""

    def alignment(self) -> WD_PARAGRAPH_ALIGNMENT:
        """Tell how the paragraph is aligned."""
        ...

    def indent(self) -> Length:
        """Measure where the first line starts from the margin of the text."""
        ...

    def hyphenation(self) -> bool:
        """Whether Word may hyphenate the paragraph automatically."""
        ...

    def pagebreak(self) -> bool:
        """Whether Word starts the paragraph on a new page."""
        ...
