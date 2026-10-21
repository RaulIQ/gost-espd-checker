from docx import Document
from docx.document import Document as Word
from hamcrest import assert_that, contains_exactly, empty

from gost_espd_checker.table_numbering import TableNumbering
from tests.conforming import endorsed
from tests.rulebook import rulebook
from tests.tabled import tabled


def numbered(*captions: str) -> Word:
    document = endorsed(Document())
    for caption in captions:
        if caption.startswith("ПРИЛОЖЕНИЕ"):
            document.add_paragraph(caption)
            continue
        tabled(document, caption, ("Сообщение", "Действия"))
    return document


def test_accepts_numbers_in_order() -> None:
    assert_that(
        TableNumbering(
            numbered("Таблица 1", "Таблица 2", "Таблица 3"), rulebook()
        ).violations(),
        empty(),
        "numbers in order were not accepted",
    )


def test_rejects_skipped_number() -> None:
    assert_that(
        [
            str(violation)
            for violation in TableNumbering(
                numbered("Таблица 1", "Таблица 4"), rulebook()
            ).violations()
        ],
        contains_exactly(
            "таблица «Таблица 4»: ошибка ESPD-015-02: номер 4 вместо 2"
            " (ГОСТ 1.5-2001, п. 4.5.3)"
        ),
        "skipped number was not rejected",
    )


def test_numbers_tables_of_appendix_by_its_designation() -> None:
    assert_that(
        TableNumbering(
            numbered("Таблица 1", "ПРИЛОЖЕНИЕ 3", "Таблица 3.1", "Таблица 3.2"),
            rulebook(),
        ).violations(),
        empty(),
        "tables of the appendix were not numbered by its designation",
    )


def test_rejects_plain_number_in_appendix() -> None:
    assert_that(
        [
            str(violation)
            for violation in TableNumbering(
                numbered("Таблица 1", "ПРИЛОЖЕНИЕ 2", "Таблица 2"), rulebook()
            ).violations()
        ],
        contains_exactly(
            "таблица «Таблица 2»: ошибка ESPD-015-02: номер 2 вместо 2.1"
            " (ГОСТ 1.5-2001, п. 4.5.3)"
        ),
        "plain number in the appendix was not rejected",
    )
