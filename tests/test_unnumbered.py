from hamcrest import assert_that, equal_to

from gost_espd_checker.unnumbered import Unnumbered


def test_drops_number_of_subsection() -> None:
    assert_that(
        str(Unnumbered(" 3.12. Настройки программы\t")),
        equal_to("Настройки программы"),
        "number of the subsection was not dropped",
    )


def test_keeps_text_without_number() -> None:
    assert_that(
        str(Unnumbered("СОДЕРЖАНИЕ")),
        equal_to("СОДЕРЖАНИЕ"),
        "text without a number did not stay as it was",
    )
