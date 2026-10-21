from hamcrest import assert_that, equal_to

from gost_espd_checker.spot import Spot


def test_finds_first_name_matching_pattern() -> None:
    assert_that(
        int(Spot(("Листов 7", "АННОТАЦИЯ", "Аннотация"), r"аннотация")),
        equal_to(1),
        "first name matching the pattern was not found",
    )


def test_gives_minus_one_without_match() -> None:
    assert_that(
        int(Spot(("ВВЕДЕНИЕ", "Назначение разработки"), r"содержание")),
        equal_to(-1),
        "missing name did not give minus one",
    )
