from hamcrest import assert_that, equal_to

from gost_espd_checker.dotted import Dotted


def test_joins_parts_of_number_with_dots() -> None:
    assert_that(
        str(Dotted((4, 17, 2))),
        equal_to("4.17.2"),
        "parts of the number were not joined with dots",
    )
