from docx import Document
from docx.document import Document as Word
from hamcrest import assert_that, contains_exactly, empty

from gost_espd_checker.table_captions import TableCaptions
from tests.conforming import endorsed
from tests.rulebook import rulebook
from tests.tabled import tabled


def captioned(caption: str) -> Word:
    document = endorsed(Document())
    tabled(document, caption, ("Имя файла", "Адрес записи"))
    return document


def test_accepts_caption_with_dash_and_name() -> None:
    assert_that(
        TableCaptions(
            captioned("Таблица 1 — Файл программы и адрес записи"), rulebook()
        ).violations(),
        empty(),
        "caption with a dash and a name was not accepted",
    )


def test_accepts_caption_without_name() -> None:
    assert_that(
        TableCaptions(captioned("Таблица 7"), rulebook()).violations(),
        empty(),
        "caption without a name was not accepted",
    )


def test_rejects_table_without_caption() -> None:
    assert_that(
        [
            str(violation)
            for violation in TableCaptions(
                captioned("Адреса записи приведены ниже."), rulebook()
            ).violations()
        ],
        contains_exactly(
            "таблица 1 по порядку: ошибка ESPD-015-01: над таблицей нет"
            " надписи «Таблица» и номера (ГОСТ 1.5-2001, п. 4.5.2)"
        ),
        "table without a caption was not rejected",
    )


def test_rejects_dot_instead_of_dash() -> None:
    assert_that(
        [
            str(violation)
            for violation in TableCaptions(
                captioned("Таблица 1. Файлы прошивки"), rulebook()
            ).violations()
        ],
        contains_exactly(
            "таблица «Таблица 1. Файлы прошивки»: ошибка ESPD-015-01:"
            " наименование отделено от номера не тире (ГОСТ 1.5-2001, п. 4.5.2)"
        ),
        "dot instead of the dash was not rejected",
    )


def test_rejects_period_after_name() -> None:
    assert_that(
        [
            str(violation)
            for violation in TableCaptions(
                captioned("Таблица 2 — Режимы работы."), rulebook()
            ).violations()
        ],
        contains_exactly(
            "таблица «Таблица 2 — Режимы работы.»: ошибка ESPD-015-01:"
            " в конце наименования таблицы стоит точка (ГОСТ 1.5-2001,"
            " п. 4.5.2)"
        ),
        "period after the name was not rejected",
    )


def test_rejects_name_in_small_letter() -> None:
    assert_that(
        [
            str(violation)
            for violation in TableCaptions(
                captioned("Таблица 3 — режимы работы"), rulebook()
            ).violations()
        ],
        contains_exactly(
            "таблица «Таблица 3 — режимы работы»: ошибка ESPD-015-01:"
            " первая буква наименования таблицы строчная"
            " (ГОСТ 1.5-2001, п. 4.5.2)"
        ),
        "name in a small letter was not rejected",
    )


def test_rejects_name_in_capitals() -> None:
    assert_that(
        [
            str(violation)
            for violation in TableCaptions(
                captioned("Таблица 4 — РЕЖИМЫ РАБОТЫ"), rulebook()
            ).violations()
        ],
        contains_exactly(
            "таблица «Таблица 4 — РЕЖИМЫ РАБОТЫ»: ошибка ESPD-106-23:"
            " наименование таблицы записано прописными буквами"
            " (ГОСТ 19.106-78, п. 2.6.2)"
        ),
        "name in capitals was not rejected",
    )
