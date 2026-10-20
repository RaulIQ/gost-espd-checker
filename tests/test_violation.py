import secrets

from hamcrest import assert_that, equal_to

from gost_espd_checker.row import Row
from gost_espd_checker.violation import Violation


def test_renders_through_its_rule() -> None:
    number = secrets.randbelow(90) + 2
    assert_that(
        str(
            Violation(
                f"раздел {number}",
                Row(
                    {
                        "id": "ESPD-106-77",
                        "clause": "ГОСТ 19.106-78, п. 9.9",
                        "severity": "предупреждение",
                    }
                ),
                "лист Ж",
            )
        ),
        equal_to(
            f"раздел {number}: предупреждение ESPD-106-77: лист Ж"
            " (ГОСТ 19.106-78, п. 9.9)"
        ),
        "violation did not render through its rule",
    )
