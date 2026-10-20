from docx import Document
from hamcrest import assert_that, contains_exactly, equal_to

from gost_espd_checker.lineage import Lineage


def test_puts_paragraph_before_its_styles() -> None:
    document = Document()
    paragraph = document.add_paragraph("Состав программы", style="Heading 3")
    assert_that(
        Lineage(paragraph).owners(),
        contains_exactly(
            paragraph.paragraph_format.element,
            document.styles["Heading 3"].element,
            document.styles["Normal"].element,
        ),
        "paragraph and its styles did not come in order of inheritance",
    )


def test_leaves_out_runs_without_text() -> None:
    paragraph = Document().add_paragraph("Связи программ")
    paragraph.add_run("   ")
    assert_that(
        len(Lineage(paragraph).fonts()),
        equal_to(1),
        "run without text was not left out",
    )


def test_puts_run_font_before_fonts_of_styles() -> None:
    document = Document()
    document.styles["Heading 2"].font.name = "Times New Roman"
    document.add_paragraph(style="Heading 2").add_run(
        "Установка программы"
    ).font.name = "Courier New"
    assert_that(
        Lineage(document.paragraphs[0]).fonts()[0][0].name,
        equal_to("Courier New"),
        "font of the run did not come before fonts of the styles",
    )
