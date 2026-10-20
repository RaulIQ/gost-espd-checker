import secrets

from hamcrest import assert_that, equal_to

from gost_espd_checker.violation import Violation


def test_renders_place_message_and_clause() -> None:
    number = secrets.randbelow(90) + 2
    assert_that(
        str(Violation(f"раздел {number}", "ГОСТ 19.106-78, п. 1.5", "лист Ж")),
        equal_to(f"раздел {number}: лист Ж (ГОСТ 19.106-78, п. 1.5)"),
        "violation did not render as place, message and clause",
    )
