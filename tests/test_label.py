from hamcrest import assert_that, equal_to

from gost_espd_checker.label import Label


def test_names_element_by_its_caption() -> None:
    assert_that(
        str(Label("таблица", "Таблица 6 — Сообщения", 6)),
        equal_to("таблица «Таблица 6 — Сообщения»"),
        "element was not named by its caption",
    )


def test_names_element_by_its_count_without_caption() -> None:
    assert_that(
        str(Label("иллюстрация", "", 3)),
        equal_to("иллюстрация 3 по порядку"),
        "element without a caption was not named by its count",
    )
