import io
from pathlib import Path

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Mm
from hamcrest import assert_that, equal_to

from gost_espd_checker.cli import Cli
from tests.conforming import conforming
from tests.rulebook import rulebook


def test_exits_with_zero_for_conforming_document(tmp_path: Path) -> None:
    document = Document()
    conforming(document.sections[0])
    path = tmp_path / "доклад.docx"
    document.save(str(path))
    assert_that(
        Cli(path, rulebook(), io.StringIO()).run(),
        equal_to(0),
        "conforming document did not exit with zero",
    )


def test_exits_with_one_for_wrong_document(tmp_path: Path) -> None:
    document = Document()
    conforming(document.sections[0]).right_margin = Mm(15)
    path = tmp_path / "отчёт.docx"
    document.save(str(path))
    assert_that(
        Cli(path, rulebook(), io.StringIO()).run(),
        equal_to(1),
        "wrong document did not exit with one",
    )


def test_prints_violation_of_wrong_document(tmp_path: Path) -> None:
    document = Document()
    conforming(document.sections[0]).right_margin = Mm(15)
    path = tmp_path / "отчёт.docx"
    document.save(str(path))
    out = io.StringIO()
    Cli(path, rulebook(), out).run()
    assert_that(
        out.getvalue(),
        equal_to(
            "раздел 1: ошибка ESPD-106-02: правое поле 15,0 мм вместо 10 мм"
            " (ГОСТ 19.106-78, п. 2.1.2)\n"
        ),
        "violation of the wrong document was not printed",
    )


def test_prints_violation_of_section_title(tmp_path: Path) -> None:
    document = Document()
    conforming(document.sections[0])
    document.add_paragraph(
        "1. ОБЩИЕ СВЕДЕНИЯ."
    ).alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    path = tmp_path / "руководство.docx"
    document.save(str(path))
    out = io.StringIO()
    Cli(path, rulebook(), out).run()
    assert_that(
        out.getvalue(),
        equal_to(
            "заголовок «1. ОБЩИЕ СВЕДЕНИЯ.»: ошибка ESPD-106-12:"
            " в конце заголовка стоит точка (ГОСТ 19.106-78, п. 2.1.7)\n"
        ),
        "violation of the section title was not printed",
    )
