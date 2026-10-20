from docx import Document
from docx.enum.text import WD_BREAK
from hamcrest import assert_that, is_

from gost_espd_checker.breaks import Breaks


def test_opens_page_with_break_before_text() -> None:
    paragraph = Document().add_paragraph()
    paragraph.add_run().add_break(WD_BREAK.PAGE)
    paragraph.add_run("АННОТАЦИЯ")
    assert_that(
        Breaks(paragraph).opens(),
        is_(True),
        "break before the text did not open a page",
    )


def test_does_not_open_page_with_break_after_text() -> None:
    paragraph = Document().add_paragraph("Листов 24")
    paragraph.add_run().add_break(WD_BREAK.PAGE)
    assert_that(
        Breaks(paragraph).opens(),
        is_(False),
        "opening did not ignore a break after the text",
    )


def test_closes_page_with_break_after_text() -> None:
    paragraph = Document().add_paragraph("2026")
    paragraph.add_run().add_break(WD_BREAK.PAGE)
    assert_that(
        Breaks(paragraph).closes(),
        is_(True),
        "break after the text did not close the page",
    )


def test_does_not_close_page_with_text_after_break() -> None:
    paragraph = Document().add_paragraph("Литера")
    paragraph.add_run().add_break(WD_BREAK.PAGE)
    paragraph.add_run("опытного образца")
    assert_that(
        Breaks(paragraph).closes(),
        is_(False),
        "closing did not ignore a break followed by text",
    )


def test_neither_opens_nor_closes_without_break() -> None:
    assert_that(
        Breaks(Document().add_paragraph("Программное обеспечение")).closes(),
        is_(False),
        "closing did not ignore a paragraph without a break",
    )
