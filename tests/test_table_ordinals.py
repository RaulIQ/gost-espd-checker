from docx import Document
from hamcrest import assert_that, contains_exactly, empty

from gost_espd_checker.table_ordinals import TableOrdinals
from tests.conforming import endorsed
from tests.rulebook import rulebook
from tests.tabled import tabled


def test_accepts_table_without_column_of_ordinals() -> None:
    document = endorsed(Document())
    tabled(document, "Таблица 1 — Пример", ("Действие", "Результат"))
    assert_that(
        TableOrdinals(document, rulebook()).violations(),
        empty(),
        "table without a column of ordinals was not accepted",
    )


def test_rejects_column_of_ordinals() -> None:
    document = endorsed(Document())
    tabled(
        document,
        "Таблица 4 — Контрольный пример",
        ("№", "Действие"),
        ("1", "Нажать"),
    )
    assert_that(
        [
            str(violation)
            for violation in TableOrdinals(document, rulebook()).violations()
        ],
        contains_exactly(
            "таблица «Таблица 4 — Контрольный пример»: ошибка ESPD-015-05:"
            " в таблице есть графа «№» (ГОСТ 1.5-2001, п. 4.5.7)"
        ),
        "column of ordinals was not rejected",
    )
