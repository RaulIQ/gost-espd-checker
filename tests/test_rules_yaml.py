import re
from collections import Counter
from pathlib import Path

import yaml
from hamcrest import assert_that, empty, is_in

import gost_espd_checker


def test_gives_every_rule_all_six_fields() -> None:
    table = yaml.safe_load(
        Path(gost_espd_checker.__file__)
        .with_name("rules.yaml")
        .read_text(encoding="utf-8")
    )
    assert_that(
        [
            row["id"]
            for row in table
            if set(row)
            != {"id", "clause", "statement", "kind", "severity", "automatic"}
        ],
        empty(),
        "some rules dont have exactly the six fields of the table",
    )


def test_uses_only_known_kinds_and_severities() -> None:
    table = yaml.safe_load(
        Path(gost_espd_checker.__file__)
        .with_name("rules.yaml")
        .read_text(encoding="utf-8")
    )
    assert_that(
        [
            row["id"]
            for row in table
            if row["kind"]
            not in {
                "страница",
                "форматирование",
                "структура",
                "оформление элементов",
                "содержание и язык",
            }
            or row["severity"] not in {"ошибка", "предупреждение"}
            or not isinstance(row["automatic"], bool)
        ],
        empty(),
        "some rules dont have a known kind, severity or automatic flag",
    )


def test_keeps_ids_unique() -> None:
    table = yaml.safe_load(
        Path(gost_espd_checker.__file__)
        .with_name("rules.yaml")
        .read_text(encoding="utf-8")
    )
    assert_that(
        [
            key
            for key, count in Counter(row["id"] for row in table).items()
            if count > 1
        ],
        empty(),
        "some rule ids are not unique",
    )


def test_lists_every_rule_the_code_checks() -> None:
    package = Path(gost_espd_checker.__file__).parent
    table = yaml.safe_load((package / "rules.yaml").read_text(encoding="utf-8"))
    assert_that(
        sorted(
            {
                key
                for source in package.glob("*.py")
                for key in re.findall(
                    r"ESPD-\d{3}-\d{2}", source.read_text(encoding="utf-8")
                )
            }
            - {row["id"] for row in table if row["automatic"]}
        ),
        empty(),
        "some rules the code checks are missing or not marked automatic",
    )


def test_finds_rules_in_the_code() -> None:
    package = Path(gost_espd_checker.__file__).parent
    assert_that(
        "ESPD-106-01",
        is_in(
            sorted(
                {
                    key
                    for source in package.glob("*.py")
                    for key in re.findall(
                        r"ESPD-\d{3}-\d{2}", source.read_text(encoding="utf-8")
                    )
                }
            )
        ),
        "the scan of the code did not find the rule of the sheet size",
    )
