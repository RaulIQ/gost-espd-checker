from docx import Document
from docx.document import Document as Word
from hamcrest import assert_that, contains_exactly, empty

from gost_espd_checker.notes import Notes
from tests.conforming import endorsed
from tests.rulebook import rulebook


def noted(*lines: str) -> Word:
    document = endorsed(Document())
    for line in lines:
        document.add_paragraph(line)
    return document


def test_accepts_single_note_with_period() -> None:
    assert_that(
        Notes(
            noted("Примечание. Плата указателя заряда не подключается."),
            rulebook(),
        ).violations(),
        empty(),
        "single note with a period was not accepted",
    )


def test_accepts_spaced_word() -> None:
    assert_that(
        Notes(
            noted(" ".join("Примечание") + ". Путь к каталогу условный."),
            rulebook(),
        ).violations(),
        empty(),
        "word printed with spaces was not accepted",
    )


def test_accepts_numbered_notes_after_colon() -> None:
    assert_that(
        Notes(
            noted(
                "Примечания:",
                "1. Номер порта относится к рабочему месту.",
                "2. Значения полей сеанса не задаются.",
            ),
            rulebook(),
        ).violations(),
        empty(),
        "numbered notes after a colon were not accepted",
    )


def test_rejects_dash_after_single_note() -> None:
    assert_that(
        [
            str(violation)
            for violation in Notes(
                noted("Примечание — источник не нужен."),
                rulebook(),
            ).violations()
        ],
        contains_exactly(
            "примечание «Примечание — источник не нужен.»:"
            " ошибка ESPD-106-24: после слова «Примечание» стоит «—»"
            " вместо точки (ГОСТ 19.106-78, п. 2.7.1)"
        ),
        "dash after a single note was not rejected",
    )


def test_rejects_period_after_plural_word() -> None:
    assert_that(
        [
            str(violation)
            for violation in Notes(
                noted("Примечания.", "1. Порт задаётся вручную."), rulebook()
            ).violations()
        ],
        contains_exactly(
            "примечание «Примечания.»: ошибка ESPD-106-24: после слова"
            " «Примечания» стоит «.» вместо двоеточия (ГОСТ 19.106-78,"
            " п. 2.7.1)"
        ),
        "period after the plural word was not rejected",
    )


def test_rejects_notes_without_numbers() -> None:
    assert_that(
        [
            str(violation)
            for violation in Notes(
                noted("Примечания:", "Порт задаётся вручную."), rulebook()
            ).violations()
        ],
        contains_exactly(
            "примечание «Примечания:»: ошибка ESPD-106-24: примечания не"
            " пронумерованы (ГОСТ 19.106-78, п. 2.7.1)"
        ),
        "notes without numbers were not rejected",
    )


def test_rejects_number_with_bracket() -> None:
    assert_that(
        [
            str(violation)
            for violation in Notes(
                noted("Примечания:", "1) Порт задаётся вручную.", "2) Сеанс."),
                rulebook(),
            ).violations()
        ],
        contains_exactly(
            "примечание «Примечания:»: ошибка ESPD-106-24: номер примечания"
            " «1)» вместо «1.» (ГОСТ 19.106-78, п. 2.7.1)",
            "примечание «Примечания:»: ошибка ESPD-106-24: номер примечания"
            " «2)» вместо «2.» (ГОСТ 19.106-78, п. 2.7.1)",
        ),
        "number with a bracket was not rejected",
    )
