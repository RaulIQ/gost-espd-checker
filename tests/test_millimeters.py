import secrets

from docx.shared import Mm
from hamcrest import assert_that, equal_to

from gost_espd_checker.millimeters import Millimeters


def test_renders_length_with_decimal_comma() -> None:
    tenths = secrets.randbelow(4000) + 1
    assert_that(
        str(Millimeters(Mm(tenths / 10))),
        equal_to(f"{tenths // 10},{tenths % 10} мм"),
        "length was not rendered in millimetres with a decimal comma",
    )


def test_renders_missing_length_as_unset() -> None:
    assert_that(
        str(Millimeters(None)),
        equal_to("не задано"),
        "missing length was not rendered as unset",
    )
