from docx import Document
from hamcrest import assert_that, contains_exactly, empty

from gost_espd_checker.bases import Bases


def test_walks_from_style_to_its_bases() -> None:
    document = Document()
    assert_that(
        [style.name for style in Bases(document.styles["Heading 4"])],
        contains_exactly("Heading 4", "Normal"),
        "style and its bases did not come in order",
    )


def test_gives_nothing_without_style() -> None:
    assert_that(
        list(Bases(None)),
        empty(),
        "missing style did not give an empty chain",
    )
