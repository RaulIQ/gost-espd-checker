from docx import Document
from docx.document import Document as Word
from hamcrest import assert_that, contains_exactly, empty

from gost_espd_checker.table_mentions import TableMentions
from tests.conforming import endorsed
from tests.rulebook import rulebook
from tests.tabled import tabled


def mentioned(*texts: str) -> Word:
    document = endorsed(Document())
    for text in texts:
        document.add_paragraph(text)
    tabled(document, "Таблица 1 — Адреса", ("Файл", "Адрес"))
    tabled(document, "Таблица 2 — Признаки", ("Признак", "Действия"))
    return document


def test_accepts_mentions_by_word() -> None:
    assert_that(
        TableMentions(
            mentioned("Адреса приведены в таблице 1.", "См. таблицу 2."),
            rulebook(),
        ).violations(),
        empty(),
        "mentions by the word were not accepted",
    )


def test_rejects_table_without_mention() -> None:
    assert_that(
        [
            str(violation)
            for violation in TableMentions(
                mentioned("Адреса приведены в таблице 1."), rulebook()
            ).violations()
        ],
        contains_exactly(
            "таблица «Таблица 2 — Признаки»: ошибка ESPD-015-02: в тексте нет"
            " ссылки на таблицу 2 (ГОСТ 1.5-2001, п. 4.5.3)"
        ),
        "table without a mention was not rejected",
    )


def test_rejects_shortened_word() -> None:
    assert_that(
        [
            str(violation)
            for violation in TableMentions(
                mentioned("Признаки (табл. 2) и адреса (таблица 1)."),
                rulebook(),
            ).violations()
        ],
        contains_exactly(
            "абзац «Признаки (табл. 2) и адреса (таблица 1).»: ошибка"
            " ESPD-015-02: ссылка «табл. 2» вместо слова «таблица»"
            " (ГОСТ 1.5-2001, п. 4.5.3)"
        ),
        "shortened word was not rejected",
    )


def test_rejects_mention_of_missing_table() -> None:
    assert_that(
        [
            str(violation)
            for violation in TableMentions(
                mentioned("Таблицы 1 и 2 дополняет таблица 8."), rulebook()
            ).violations()
        ],
        contains_exactly(
            "абзац «Таблицы 1 и 2 дополняет таблица 8.»: ошибка ESPD-015-02:"
            " ссылка на таблицу 8, которой нет в документе"
            " (ГОСТ 1.5-2001, п. 4.5.3)"
        ),
        "mention of a missing table was not rejected",
    )


def test_counts_every_table_of_range() -> None:
    document = mentioned("Сообщения вне таблиц 1—3 не описаны.")
    tabled(document, "Таблица 3 — Коды", ("Код", "Значение"))
    assert_that(
        TableMentions(document, rulebook()).violations(),
        empty(),
        "every table of the range was not counted",
    )


def test_ignores_table_of_other_standard() -> None:
    assert_that(
        [
            str(violation)
            for violation in TableMentions(
                mentioned("Вид документа по ГОСТ 19.101-2024, табл. 2."),
                rulebook(),
            ).violations()
        ],
        contains_exactly(
            "таблица «Таблица 1 — Адреса»: ошибка ESPD-015-02: в тексте нет"
            " ссылки на таблицу 1 (ГОСТ 1.5-2001, п. 4.5.3)",
            "таблица «Таблица 2 — Признаки»: ошибка ESPD-015-02: в тексте нет"
            " ссылки на таблицу 2 (ГОСТ 1.5-2001, п. 4.5.3)",
        ),
        "table of another standard was not ignored",
    )
