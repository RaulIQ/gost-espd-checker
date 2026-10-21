from hamcrest import assert_that, is_

from gost_espd_checker.successors import Successors


def test_lets_next_subsection_follow() -> None:
    assert_that(
        (3, 3) in Successors((3, 2)),
        is_(True),
        "next subsection was not let to follow",
    )


def test_lets_next_section_follow_point() -> None:
    assert_that(
        (5,) in Successors((4, 2, 7)),
        is_(True),
        "next section was not let to follow a point",
    )


def test_refuses_skipped_number() -> None:
    assert_that(
        (3, 4) in Successors((3, 2)),
        is_(False),
        "skipped number was not refused",
    )
