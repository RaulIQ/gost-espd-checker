from docx import Document
from hamcrest import assert_that, contains_exactly

from gost_espd_checker.body import Body
from tests.conforming import endorsed


def test_leaves_out_title_page() -> None:
    document = endorsed(Document())
    document.add_paragraph("АННОТАЦИЯ")
    assert_that(
        [paragraph.text for paragraph in Body(document)],
        contains_exactly("АННОТАЦИЯ"),
        "title page was not left out",
    )
